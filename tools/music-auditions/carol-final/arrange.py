"""Synthesize the instrument kit and encode the editable score as a ZSM v1 stream."""
import argparse
from collections import Counter, defaultdict
import json
from pathlib import Path
import struct

import numpy as np
from scipy import signal

HZ = 60
RATE = 42                              # VERA PCM rate register
SR = 25_000_000/512*RATE/128
KEYS = (0,1,2,4,5,6,8,9,10,12,13,14)
# Algorithm 4: two independent modulator/carrier pairs in OPM register order.
# op tuple = DT1/MUL, TL, AR, D1R, D2R, D1L/RR. Short bright transients
# and a quieter body keep the bells legible when the guitar pair enters.
BELL = ((6,29,31,21,8,0x56),(3,37,31,19,6,0x46),(1,17,31,13,4,0x46),(2,27,31,17,5,0x56))
GLASS = ((3,39,28,14,6,0x45),(7,45,30,19,5,0x55),(1,21,27,11,2,0x35),(2,32,30,17,3,0x45))
KEYS_PATCH = ((2,36,28,16,3,0x37),(1,34,24,11,2,0x38),(1,20,27,9,1,0x28),(0x11,27,22,10,1,0x28))
STRING = ((1,38,22,8,1,0x26),(2,47,19,7,1,0x26),(1,24,18,7,0,0x27),(0x21,30,16,8,0,0x27))
GTR_L = ((1,12,31,17,3,0x38),(3,25,31,20,5,0x49),(1,20,31,9,1,0x2a),(0x11,27,30,12,2,0x3a))
GTR_R = ((0x11,16,31,16,3,0x39),(2,24,31,20,6,0x5a),(1,21,31,10,1,0x29),(0x51,28,30,13,1,0x3a))
BASS = ((1,24,31,20,7,0x58),(3,37,31,21,8,0x69),(1,19,31,12,1,0x39),(2,32,31,16,3,0x49))
SOLO = ((1,17,30,16,1,0x28),(3,31,31,17,4,0x49),(1,19,28,9,1,0x28),(0x21,29,25,10,2,0x38))
PATCHES = (BELL,GLASS,KEYS_PATCH,STRING,GTR_L,GTR_R,BASS,SOLO)
PAN = (0xc0,0xc0,0x80,0x40,0x80,0x40,0xc0,0xc0)
FEEDBACK = (1,1,3,2,6,6,4,5)


def drum_kit():
    # All waveforms are synthesized here. The song contains no audio from the video.
    rng=np.random.default_rng(12025)
    length=round(SR*.76)
    t=np.arange(length)/SR
    def noise(lo,hi):
        b=signal.butter(3,[lo,hi],btype='bandpass',fs=SR,output='sos')
        x=signal.sosfilt(b,rng.normal(size=length))
        return x/np.std(x)
    def tone(f,fall,release):
        phase=2*np.pi*(f*t+fall*.032*(1-np.exp(-t/.032)))
        return np.sin(phase)*np.exp(-t/release)
    def room(x,pan):
        lr=np.column_stack((x*(1-pan),x*(1+pan)))
        for side,delays in enumerate(((.027,.071),(.039,.089))):
            for delay,level in zip(delays,(.14,.065)):
                d=round(delay*SR)
                lr[d:,side]+=x[:-d]*level
        return lr
    def metal(lifetime):
        x=noise(3200,7300)*.66 + noise(1700,5800)*.18
        for f in (1693,2377,3279,4262,5513,6971):
            x+=.055*np.sin(2*np.pi*f*t+.65*np.sin(2*np.pi*f*.317*t))
        return x*np.exp(-t/lifetime)
    kick=room((tone(47,105,.104)*.93 + noise(750,4800)*np.exp(-t/.005)*.14),0)
    snare=room((.36*tone(186,51,.065)+.18*tone(329,36,.039)+
                .42*noise(680,6500)*np.exp(-t/.081)+.18*noise(200,2000)*np.exp(-t/.039)),.045)
    tom=room(.66*tone(116,73,.12)+noise(300,5400)*np.exp(-t/.028)*.16,-.22)
    floor=room(.80*tone(78,54,.15)+noise(280,4700)*np.exp(-t/.019)*.13,.25)
    hats=room(metal(.034)*.32,-.25)
    open_hat=room(metal(.115)*.29,-.23)
    crash=room(metal(.23)*.43,.12)
    # Preblend coincident strokes for the single hardware FIFO.
    voices=[kick,snare,tom,floor,hats,open_hat,crash]
    return voices


class Score:
    def __init__(self, duration):
        self.duration=round(duration*HZ)
        self.events=defaultdict(list)
        self.parts=[[] for _ in range(24)]
        self.drum_events=[]
        self.fades=[]
        self.psg_fades=[]
        self.sustain_at=None
        self.sources=drum_kit()

    def note(self,ch,t,end,pitch,strength):
        if end>t and strength>0:
            self.parts[ch].append((round(t*HZ),round(end*HZ),int(pitch),float(strength)))

    def trigger(self,t,mask,volume):
        if mask:self.drum_events.append((round(t*HZ),int(mask),int(volume)))

    def compile(self, omit=None):
        events=self.events
        counts=Counter()
        for ch,patch in enumerate(PATCHES):
            if omit=='fm':continue
            init=events[0]
            init += [('f',0x20+ch,PAN[ch]|FEEDBACK[ch]<<3|4),('f',0x30+ch,0),('f',0x38+ch,0)]
            for op,params in enumerate(patch):
                for base,v in zip((0x40,0x60,0x80,0xa0,0xc0,0xe0),params):
                    init.append(('f',base+op*8+ch,v))
        # PSG duties and pans are per part: bass core and pick, bell echoes,
        # stereo string pair, palm-mute edge, organ, and metallic cymbal tails.
        waves=(0x80,0x12,0x80,0x80,0x1d,0x23,0x80,0x80,0x0c,0x17,0x80,0x80,0xc0,0xc0,0x80,0x80)
        pans=(192,192,128,64,128,64,128,64,128,64,128,64,128,64,128,64)
        tune=(0,0,-.04,.04,-.05,.06,0,0,-.04,.05,-.035,.035,0,0,-.04,.04)
        # Measured in the hardware mixer. YM TL uses 0.75 dB steps and a
        # halving of linear gain is 6.02 dB. Channel trims leave percussion space.
        lift=(15,16,13,13,10,10,8,10)
        def carriers(ch,gain):
            base=PATCHES[ch][2][1]
            tl=int(np.clip(round(base-lift[ch]-8.03*np.log2(max(.0005,gain))),0,112))
            other=min(127,tl+PATCHES[ch][3][1]-base)
            return [('f',0x70+ch,tl),('f',0x78+ch,other)]
        fm_mask=psg_mask=0
        for ch,part in enumerate(self.parts):
            if not part or (ch<8 and omit=='fm') or (ch>=8 and omit=='psg'):continue
            part=sorted(part)
            if ch<8:fm_mask|=1<<ch
            else:
                j=ch-8;psg_mask|=1<<j;events[0].append(('p',4*j+3,waves[j]))
            for k,(start,end,note,gain) in enumerate(part):
                if k+1<len(part):end=min(end,part[k+1][0])
                end=min(end,self.duration)
                if not 0<=start<end:continue
                counts[ch]+=1
                if ch<8:
                    oc,degree=divmod(note-13,12);kc=oc*16+KEYS[degree]
                    events[start].extend([('f',8,ch),('f',0x28+ch,kc),
                                          *carriers(ch,gain),('f',8,0x78|ch)])
                    events[end].append(('f',8,ch))
                else:
                    j=ch-8
                    freq=round(440*2**((note+tune[j]-69)/12)*131072/(25_000_000/512))
                    vol=int(np.clip(round(63+8*np.log2(max(.003,gain))),1,63))
                    events[start].extend([('p',4*j,freq&255),('p',4*j+1,freq>>8),
                                          ('p',4*j+2,pans[j]|vol)])
                    for delta,adj in ((3,5),(9,9)):
                        if start+delta<end and j not in (0,4,5,10,11):
                            events[start+delta].append(('p',4*j+2,pans[j]|max(1,vol-adj)))
                    events[end].append(('p',4*j+2,0))
        if omit!='fm':
            if self.sustain_at is not None:
                for ch in range(8):
                    # Change both carrier envelopes to sustain before the last
                    # attack. Its measured swell is controlled by TL automation.
                    for base in (0xb0,0xb8,0xd0,0xd8):
                        events[round(self.sustain_at*HZ)].append(('f',base+ch,0))
            for ch,t,gain in self.fades:
                events[round(t*HZ)].extend(carriers(ch,gain))
        if omit!='psg':
            for ch,t,gain in self.psg_fades:
                j=ch-8
                vol=int(np.clip(round(63+8*np.log2(max(.001,gain))),0,63))
                events[round(t*HZ)].append(('p',4*j+2,pans[j]|vol))
        masks=sorted(set(m for _,m,_ in self.drum_events)) if omit!='pcm' else []
        if masks:
            events[0].append(('d',1,RATE))
            for t,mask,lvl in self.drum_events:
                events[t].extend([('d',0,lvl),('d',2,masks.index(mask))])
        stream=bytearray(); regs={}; prev=0
        for tick in sorted(set(events)|{self.duration}):
            if tick>self.duration:raise ValueError('note outside track')
            writes=[]
            for chip,reg,v in events[tick]:
                # Key and PCM trigger writes are strobes, even for repeated notes.
                if (chip,reg) not in (('f',8),('d',2)) and regs.get((chip,reg))==v:continue
                writes.append((chip,reg,v));regs[chip,reg]=v
            if not writes and tick!=self.duration:continue
            delay=tick-prev;prev=tick
            while delay:
                step=min(delay,127);stream.append(128+step);delay-=step
            off=0
            while off<len(writes):
                chip,reg,v=writes[off]
                if chip=='p':stream.extend((reg,v));off+=1;continue
                end=off+1;limit=63 if chip=='f' else 31
                while end<len(writes) and end-off<limit and writes[end][0]==chip:end+=1
                if chip=='f':stream.append(64+end-off)
                else:stream.extend((64,2*(end-off)))
                for _,r,x in writes[off:end]:stream.extend((r,x))
                off=end
        stream.append(128)
        table=bytearray();samples=bytearray()
        for index,mask in enumerate(masks):
            mix=sum(v for j,v in enumerate(self.sources) if mask&(1<<j))
            limit=.72 if mask&64 else .44 if mask&32 else .36 if mask&14 else .29 if mask&1 else .16
            mix=mix[:round(limit*SR)].copy()
            mix[:4]*=np.linspace(0,1,4)[:,None];mix[-80:]*=np.linspace(1,0,80)[:,None]
            # Gentle drum-bus saturation leaves FM/PSG headroom in the hardware sum.
            raw=np.rint(116*np.tanh(mix*1.32)).astype(np.int8).tobytes()
            table.extend(bytes((index,0x10))+len(samples).to_bytes(3,'little')+
                         len(raw).to_bytes(3,'little')+bytes(8));samples.extend(raw)
        offset=16+len(stream) if masks else 0
        header=b'zm\1'+bytes(3)+offset.to_bytes(3,'little')+bytes((fm_mask,))+struct.pack('<HHH',psg_mask,HZ,0)
        return header+stream+(b'PCM'+bytes((len(masks)-1,))+table+samples if masks else b''), counts
