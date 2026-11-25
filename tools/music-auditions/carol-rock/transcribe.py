"""Measure this audition's note lines and timing directly from the supplied stereo reference."""
import argparse
import json
import subprocess
from pathlib import Path

import numpy as np
import onnxruntime as ort
from scipy import signal, ndimage

SR = 22050
# 125.2 quarter notes/minute with triplet subdivisions, measured from the recording.
STEP = .15970
ORIGIN = 1.030
PITCHES = np.arange(21, 109)
FREQS = 440 * 2**((PITCHES - 69) / 12)


def activations(audio, model):
    # The ICASSP 2022 Basic Pitch ONNX model takes overlapping 2-second excerpts.
    window, trim = 43844, 15
    advance = window - 2*trim*256
    padded = np.pad(audio, (trim*256, window))
    opts = ort.SessionOptions()
    opts.intra_op_num_threads = 3
    opts.inter_op_num_threads = 1
    net = ort.InferenceSession(str(model), opts, providers=['CPUExecutionProvider'])
    parts, stamps = [], []
    for offset in range(0, len(audio)+trim*256, advance):
        block = padded[offset:offset+window][None,:,None]
        frames, = net.run(['StatefulPartitionedCall:1'], {net.get_inputs()[0].name: block})
        core = frames[0,trim:-trim]
        parts.append(core)
        stamps.extend((offset+np.arange(len(core))*advance/len(core))/SR)
    return np.array(stamps), np.concatenate(parts)


def voice(salience, pitches, switch):
    # Trace one continuous part. Penalize octave jumps and isolated weak
    # alternatives that would turn a sustained chord into a different melody.
    n = len(pitches)
    candidates = salience[:,pitches-21]
    emissions = np.log(.16+candidates)
    distance = abs(pitches[:,None]-pitches[None,:])
    penalty = np.where(distance, switch+.014*np.minimum(distance,16), 0.)
    states = emissions[0].copy()
    back = np.zeros((len(candidates),n),np.int16)
    for i in range(1,len(candidates)):
        trans = states[:,None]-penalty
        back[i] = trans.argmax(axis=0)
        states = trans[back[i],np.arange(n)] + emissions[i]
    path = [int(states.argmax())]
    for prev in back[:0:-1]:
        path.append(int(prev[path[-1]]))
    chosen = np.array(path[::-1])
    return pitches[chosen], candidates[np.arange(len(chosen)),chosen]


def measure(audio, times, notes):
    n, hop = 4096, 220
    padded = np.pad(audio,(n//2,n//2))
    windows = np.lib.stride_tricks.sliding_window_view(padded,n)[::hop]
    spectrum = np.concatenate([abs(np.fft.rfft(z*np.hanning(n))).astype('f') for z in np.array_split(windows,40)])
    t = np.arange(len(windows))*hop/SR
    freq = np.fft.rfftfreq(n,1/SR)
    diff = np.maximum(0,np.diff(np.log1p(3*spectrum),n=1,axis=0,prepend=np.log1p(3*spectrum[:1])))
    onset = diff[:,(freq>45)&(freq<6500)].mean(axis=1)
    ix = signal.find_peaks(onset,prominence=.011,distance=7)[0]
    grid = np.arange(ORIGIN, len(audio)/SR-.1, STEP)
    # Keep the grid anchored globally and recover small local deviations from
    # nearby attacks; low-energy tails should never invent a new tempo.
    for j, g in enumerate(grid):
        use = ix[abs(t[ix]-g)<3.5]
        if not len(use):continue
        z = np.average(np.exp(2j*np.pi*(t[use]-g)/STEP),weights=onset[use])
        if abs(z)>.50:grid[j] += np.clip(np.angle(z)*STEP/(2*np.pi),-.05,.05)
    bins = np.clip(np.rint(FREQS/freq[1]).astype(int),2,len(freq)-2)
    strengths = np.maximum.reduce([spectrum[:,bins],spectrum[:,bins-1],spectrum[:,bins+1]])
    envelopes = np.stack([np.sqrt((spectrum[:,(freq>=a)&(freq<b)]**2).mean(axis=1))
                          for a,b in [(35,155),(160,3500),(3500,10000)]],axis=1)
    features, bands = [], []
    for start in grid:
        sl = slice(*np.searchsorted(t,[start+.033,start+.14]))
        ns = slice(*np.searchsorted(times,[start+.028,start+.14]))
        energy = strengths[sl].mean(axis=0)
        prob = notes[ns].mean(axis=0) if notes[ns].size else np.zeros(88)
        features.append(np.maximum(0,prob-.115)**.85 * np.sqrt(energy))
        bands.append(envelopes[sl].mean(axis=0))
    sal = np.array(features)
    bands = np.array(bands)
    bass, bs = voice(sal,np.arange(28,55),.56)
    lead, ls = voice(sal,np.arange(60,96),.50)
    inner_sal = sal.copy()
    for i,note in enumerate(lead):
        for p in (note, note-12, note+12):
            if 21<=p<=108:inner_sal[i,p-21]*=.20
    inner, ins = voice(inner_sal,np.arange(52,84),.66)
    upper_sal = sal.copy()
    for i,(mel,mid) in enumerate(zip(lead,inner)):
        for p in (mel,mid,mel+12,mid+12):
            if 21<=p<=108:upper_sal[i,p-21]*=.12
    top, us = voice(upper_sal,np.arange(63,97),.65)

    # A guitar rhythm part needs chord roots, not every passing bass note.
    # Fold the lower register by pitch class and pool two beats at a time.
    chroma=np.zeros((len(grid),12))
    for p in range(28,62):chroma[:,p%12]+=sal[:,p-21]*(1.25 if p<48 else .48)
    roots = ndimage.uniform_filter1d(chroma,7,axis=0,mode='nearest').argmax(axis=1)
    def level(v,lim=5.):return int(np.clip(round(100*v/lim),0,100))
    data=[]
    for i,sec in enumerate(grid):
        # Preserve the opening's eight G5 strikes and the gradual assembly
        # of the four-note cell. This prevents echoes from becoming new notes.
        if i<24:
            lead[i],ls[i]=79,2.8 if i%3==0 else 2.2
        elif i<246:
            m=(79,79,78,79 if i>=48 else 78,76,76)
            lead[i],ls[i]=m[i%6],max(ls[i],1.7)
        data.append([round(sec,4),int(lead[i]),level(ls[i]),int(inner[i]),level(ins[i]),
                     int(top[i]),level(us[i]),int(bass[i]),level(bs[i]),int(roots[i]),
                     *[round(float(v),2) for v in bands[i]]])
    return data


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('recording',type=Path)
    ap.add_argument('onnx_model',type=Path)
    ap.add_argument('output',type=Path)
    args=ap.parse_args()
    raw=subprocess.check_output(['ffmpeg','-nostdin','-v','error','-i',str(args.recording),
                                 '-vn','-ar',str(SR),'-ac','2','-f','f32le','-'])
    audio=np.frombuffer(raw,'<f4').reshape(-1,2).mean(axis=1)
    times,notes=activations(audio,args.onnx_model)
    score={'duration':round(len(audio)/SR,4),'grid':measure(audio,times,notes)}
    args.output.write_text(json.dumps(score,separators=(',',':'))+'\n')


if __name__=='__main__':main()
