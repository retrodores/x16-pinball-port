#!/usr/bin/env python3
"""Original quiet triangle-wave effects and a two-voice 64-step music loop."""
from pathlib import Path
import math,json
r=Path(__file__).resolve().parent;o=r/'build';o.mkdir(exist_ok=True)
# VERA's measured/implemented 6-bit logarithmic volume curve.
lut=[0,4,8,12,16,17,18,20,21,22,23,25,26,28,30,31,33,35,37,40,42,45,47,50,53,56,60,63,67,71,75,80,85,90,95,101,107,113,120,127,135,143,151,160,170,180,191,202,214,227,241,255,270,286,303,321,341,361,382,405,429,455,482,511]
def vol(peak,f):return min(range(64),key=lambda i:abs(lut[i]-lut[peak]*max(0,f)))
def freq(hz):return round(hz*131072/(25e6/512))
# id, start Hz, end Hz, ticks, peak volume, priority. Triangle, no noise/pulse.
spec=[(190,95,7,31,2),(145,80,6,28,1),(1046.5,1046.5,14,39,4),(440,880,15,35,3),(110,220,18,29,1),(523.25,130.81,36,34,5),(300,220,5,25,0)]
lines=[];manifest=[]
for i,(a,b,n,v,priority)in enumerate(spec):
 frames=[]
 for t in range(n):
  gain=min(1,t/2)*max(0,(n-1-t)/(n-3))**1.5
  hz=a*(b/a)**(t/(n-1));f=freq(hz);frames.extend([f&255,f>>8,192|vol(v,gain),128])
 lines.append(f'sfx_{i}: .byte '+','.join(map(str,frames)))
 manifest.append(dict(id=i,frames=n,start_hz=a,end_hz=b,peak_volume=v,priority=priority))
lines+=['sfx_addresses: .word '+','.join('sfx_'+str(i)for i in range(7)),'sfx_ticks: .byte '+','.join(str(a[2])for a in spec),'sfx_priorities: .byte '+','.join(str(a[4])for a in spec)]
# Original C-major / A-minor arcade phrase; each step is 16 video ticks.
melody=[60,64,67,72,71,67,64,62, 60,64,69,67,65,64,62,67,
        57,60,64,69,67,64,60,59, 57,60,65,64,62,60,59,64,
        65,69,72,76,74,72,69,67, 65,69,74,72,71,69,67,64,
        67,71,74,72,69,67,64,62, 65,64,62,59,60,64,67,0]
bass=[36,43,36,43,33,40,33,40,41,48,41,48,43,50,43,48]
def notes(ns):return [freq(440*2**((n-69)/12))if n else 0 for n in ns]
for name,ns in [('melody',melody),('bass',bass)]:
 vals=notes(ns);lines+=[name+'_lo: .byte '+','.join(str(f&255)for f in vals),name+'_hi: .byte '+','.join(str(f>>8)for f in vals)]
lines+=['melody_env: .byte '+','.join(str(192|vol(26,min(1,t/2)*min(1,(15-t)/4)))for t in range(16)),'bass_env: .byte '+','.join(str(192|vol(21,min(1,t/3)*max(0,(63-t)/50)))for t in range(64))]
(o/'sound-data.inc').write_text('\n'.join(lines)+'\n');(o/'sound-manifest.json').write_text(json.dumps({'effects':manifest,'music_steps':64,'ticks_per_step':16,'music_seconds':64*16/60,'waveform':'triangle','music_peak_volumes':[26,21]},indent=2)+'\n')
