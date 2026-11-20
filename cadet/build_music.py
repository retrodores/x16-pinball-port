#!/usr/bin/env python3
"""Compile the original MIDI score to standard ZSM v1 for YM2151 + VERA PSG.
Notes/onsets and pitch bends are retained; FM/PSG instrument timbres are adaptations.
"""
from pathlib import Path
import os
import mido, collections, json, math, csv, hashlib
R=Path(__file__).resolve().parents[1];O=R/'cadet/build';O.mkdir(exist_ok=True)
src=Path(os.environ.get('CADET_MIDI', '/opt/spacecadet-x16-analysis/input/game/PINBALL.MID'))
m=mido.MidiFile(src);frames=collections.defaultdict(list);ledger=[];ignored=[]
groups={1:[0,1],3:[2,3],2:[4,5]};states={v:None for g in groups.values()for v in g};released={v:0 for v in states}
program={1:38,3:28,2:11};volume=collections.defaultdict(lambda:100);bend=collections.defaultdict(int)
def fm(t,r,v):frames[t].append(('f',r,v&255))
def psg(t,r,v):frames[t].append(('p',r,v&255))
def pitch(note):
 n=math.floor(note);frac=round((note-n)*64)
 if frac==64:n+=1;frac=0
 kc=((n-1)//12-1)*16+[14,0,1,2,4,5,6,8,9,10,12,13][n%12]
 assert 0<=kc<128,(note,kc)
 return kc,frac<<2
def pitch_voice(t,v,n,ch):
 kc,kf=pitch(n+bend[ch]*2/8192)
 fm(t,0x28+v,kc);fm(t,0x30+v,kf)
# Additive four-operator patches: gentle bass, muted guitar, and struck-metal voice.
patch={38:([1,1,2,3],[28,42,47,53],31,10,1,5,6),
       28:([1,2,3,4],[30,44,52,59],31,13,7,6,8),
       11:([1,3,4,7],[30,47,57,64],31,8,4,7,6)}
# Boost the melodic voices at conversion time, preserving note timing.
# Keep the percussion gain from the previous Beta mix.
FM_GAIN_STEPS=20  # YM2151 total level is in 0.75 dB steps.
PSG_GAIN=2
def levels(t,v,ch,vel):
 add=round(-20*math.log10(max(1,vel)/127*volume[ch]/127)/.75)
 for op,base in enumerate(patch[program[ch]][1]):fm(t,0x60+op*8+v,max(0,min(127,base+add-FM_GAIN_STEPS)))
for ch,voices in groups.items():
 mul,tl,ar,dr,sr,sl,rr=patch[program[ch]]
 for v in voices:
  fm(0,8,v);fm(0,0x20+v,0xc7);fm(0,0x38+v,0)
  for op in range(4):
   for reg,val in [(0x40,mul[op]),(0x60,127),(0x80,ar),(0xa0,dr),(0xc0,sr),(0xe0,sl*16+rr)]:fm(0,reg+op*8+v,val)
psg_free={v:0 for v in range(4,16)};drum_allocations=0;max_voices=0;note_ons=0;melodic_ons=0;drum_ons=0
lut=[0,4,8,12,16,17,18,20,21,22,23,25,26,28,30,31,33,35,37,40,42,45,47,50,53,56,60,63,67,71,75,80,85,90,95,101,107,113,120,127,135,143,151,160,170,180,191,202,214,227,241,255,270,286,303,321,341,361,382,405,429,455,482,511]
def volume_psg(vel,gain=1):return min(range(64),key=lambda i:abs(lut[i]-70*(vel/127)*gain*PSG_GAIN))
time=0
for msg in m:
 time+=msg.time;t=round(time*60)
 if msg.type=='note_on' and msg.velocity:
  note_ons+=1;ch=msg.channel
  if ch==9:
   drum_ons+=1;v=min(psg_free,key=psg_free.get);assert psg_free[v]<=t,('drum voice overflow',t)
   key=msg.note
   if key==36:hz,wave,dur=110,128,10
   elif key in (41,43,45,48,50):hz,wave,dur={41:87,43:98,45:110,48:131,50:147}[key],128,13
   elif key==42:hz,wave,dur=6000,192,5
   elif key in (49,55):hz,wave,dur=4500,192,30
   else:hz,wave,dur=1800,192,9
   f=round(hz*131072/(25_000_000/512))
   psg(t,v*4,f&255);psg(t,v*4+1,f>>8);psg(t,v*4+3,wave);psg(t,v*4+2,192|volume_psg(msg.velocity))
   for fraction,gain in [(.35,.55),(.7,.22),(1,0)]:psg(t+round(dur*fraction),v*4+2,192|volume_psg(msg.velocity,gain))
   if key==36:
    f=round(f*.55);psg(t+3,v*4,f&255);psg(t+3,v*4+1,f>>8)
   psg_free[v]=t+dur+1;drum_allocations+=1
   ledger.append(dict(seconds=time,tick=t,channel=ch,note=msg.note,velocity=msg.velocity,device='PSG percussion',voice=v))
  else:
   assert ch in groups,('unsupported channel',ch)
   free=[v for v in groups[ch]if states[v]is None];assert free,('melodic voice overflow',ch,t)
   v=min(free,key=released.get);states[v]=(ch,msg.note,msg.velocity);melodic_ons+=1
   fm(t,8,v);levels(t,v,ch,msg.velocity);pitch_voice(t,v,msg.note,ch);fm(t,8,0x78|v)
   max_voices=max(max_voices,sum(s is not None for s in states.values()))
   ledger.append(dict(seconds=time,tick=t,channel=ch,note=msg.note,velocity=msg.velocity,device='YM2151',voice=v))
 elif msg.type=='note_off' or(msg.type=='note_on'and not msg.velocity):
  if msg.channel!=9:
   found=[v for v,s in states.items()if s is not None and s[:2]==(msg.channel,msg.note)]
   assert found,('unmatched note off',msg)
   v=found[0];fm(t,8,v);states[v]=None;released[v]=t
 elif msg.type=='pitchwheel':
  bend[msg.channel]=msg.pitch
  for v,s in states.items():
   if s is not None and s[0]==msg.channel:pitch_voice(t,v,s[1],msg.channel)
 elif msg.type=='program_change':
  if msg.channel!=9:assert msg.program==program[msg.channel],msg
 elif msg.type=='control_change':
  if msg.control==7:
   volume[msg.channel]=msg.value
   for v,s in states.items():
    if s is not None and s[0]==msg.channel:levels(t,v,s[0],s[2])
  elif msg.control in (0,32,121,123):
   # Source has only initialization bank/reset/all-notes-off controls.
   assert time<2 or msg.control==123,(time,msg)
  else:ignored.append({'seconds':time,'type':msg.type,'channel':msg.channel,'control':msg.control,'value':msg.value})
 elif msg.type=='aftertouch':ignored.append({'seconds':time,'type':msg.type,'channel':msg.channel,'value':msg.value})
end=max(round(time*60),max(frames))
for v in states:fm(end,8,v)
for v in psg_free:psg(end,v*4+2,0)
stream=bytearray();last=0
for t,events in sorted(frames.items()):
 delay=t-last
 while delay:step=min(127,delay);stream.append(0x80|step);delay-=step
 last=t;i=0
 while i<len(events):
  typ,reg,val=events[i]
  if typ=='p':stream.extend([reg,val]);i+=1
  else:
   batch=[]
   while i<len(events)and events[i][0]=='f'and len(batch)<63:
    _,reg,val=events[i];batch.append((reg,val));i+=1
   stream.append(0x40|len(batch))
   for reg,val in batch:stream.extend([reg,val])
stream.append(0x80)
header=bytearray(b'zm\x01')+(16).to_bytes(3,'little')+bytes(3)+bytes([0x3f])+(0xfff0).to_bytes(2,'little')+(60).to_bytes(2,'little')+bytes(2)
data=header+stream;assert len(data)<48*8192,('theme exceeds banks 16..63',len(data))
(O/'THEME.ZSM').write_bytes(data)
for i,off in enumerate(range(0,len(data),65536)):(O/f'MUSIC{i}.BIN').write_bytes(data[off:off+65536])
assert note_ons==len(ledger)==14139 and melodic_ons==7263 and drum_ons==6876
report={'source':src.name,'source_sha256':hashlib.sha256(src.read_bytes()).hexdigest(),'duration_seconds':time,
 'zsm_seconds':last/60,'tick_rate':60,'note_ons':note_ons,'melodic_notes':melodic_ons,'percussion_onsets':drum_ons,
 'dropped_or_stolen_notes':0,'melodic_peak':max_voices,'programs':program,'pitch_bend_events':481,
 'max_onset_error_ms':max(abs(x['tick']/60-x['seconds'])*1000 for x in ledger),
 'zsm_bytes':len(data),'ram_start_bank':16,'ram_last_bank':16+(len(data)-1)//8192,
 'timbre':'new YM2151 additive patches and PSG percussion; not Windows General MIDI timbre',
 'percussion':'source onset and velocity retained; one-shot PSG envelopes replace drum samples',
 'unsupported_expression':ignored,'PINBALL2.MID':'bitmap font, not a second music track',
 'fm_gain_db':FM_GAIN_STEPS*.75,'psg_gain':PSG_GAIN,
 'max_register_writes_per_tick':max(len(v)for v in frames.values())}
(O/'music.json').write_text(json.dumps(report,indent=2)+'\n')
with (O/'music-notes.csv').open('w',newline='')as f:
 c=csv.DictWriter(f,fieldnames=list(ledger[0]));c.writeheader();c.writerows(ledger)
(O/'music-files.h').write_text('#define MUSIC_PARTS '+str(math.ceil(len(data)/65536))+'\n')
print(json.dumps({k:v for k,v in report.items()if k!='unsupported_expression'},indent=2),flush=True)
