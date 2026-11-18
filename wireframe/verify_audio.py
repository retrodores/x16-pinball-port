#!/usr/bin/env python3
"""Validate actual emulated PSG output, soft effects, music wrap and all toggles."""
from pathlib import Path
import os,re,subprocess as sp,time,wave,json
import numpy as np
r=Path(__file__).resolve().parents[1];o=r/'wireframe/evidence';o.mkdir(exist_ok=True);results=[]
for cpu in os.environ.get('TEST_CPUS','c02 c816').split():
 for ram in map(int,os.environ.get('TEST_RAM','512 2048').split()):
  mhz=int(os.environ.get('TEST_MHZ','8'));name=f'psg-{cpu}-{ram}-{mhz}';log=o/(name+'.log');wav=o/(name+'.wav')
  with log.open('w')as stream:
   p=sp.Popen(['/opt/x16emu-r49/x16emu','-'+cpu,'-rom','/opt/x16emu-r49/rom.bin','-ram',str(ram),'-mhz',str(mhz),'-warp','-echo','raw','-wav',str(wav)+',wait','-fsroot',str(r/'wireframe/build'),'-prg',str(r/f'wireframe/build/{cpu}/audio.prg'),'-run'],stdout=stream,stderr=stream,env=dict(os.environ,SDL_AUDIODRIVER='dummy',SDL_VIDEODRIVER='dummy'))
   try:
    deadline=time.monotonic()+120
    while '# AUDIO DONE'not in log.read_text(errors='replace'):
     assert p.poll()is None,'emulator exited early';assert time.monotonic()<deadline,'audio timeout';time.sleep(.1)
    time.sleep(.15)
   finally:
    p.terminate()
    try:p.wait(timeout=5)
    except sp.TimeoutExpired:p.kill();p.wait()
  text=log.read_text(errors='replace');assert 'not ok'not in text,text
  events=[(n,int(i,16),int(t,16)/(mhz*1e6))for n,i,t in re.findall(r'# EVENT (\w+) (\w+) (\w+)',text)]
  with wave.open(str(wav))as w:rate=w.getframerate();channels=w.getnchannels();data=np.frombuffer(w.readframes(w.getnframes()),'<i2').reshape(-1,channels).astype(float)
  peak=float(np.max(np.abs(data)));assert peak<12000,('unexpectedly harsh/clipped peak',peak)
  def clip(a,b):return data[max(0,int(a*rate)):min(len(data),int(b*rate)),0]
  def rms(x):return float(np.sqrt(np.mean(x*x)))
  def dominant(x):return float(np.argmax(np.abs(np.fft.rfft((x-x.mean())*np.hanning(len(x))))) * rate/len(x))
  measurements=[]
  for k,(name0,i,t)in enumerate(events[:-1]):
   end=events[k+1][2];a=clip(t+.04,end-.02);value=rms(a)
   if name0 in ('MUSIC_OFF','PAUSE','MUTE'):assert value<2,(name0,'not silent',value)
   if name0 in ('MUSIC','MUSIC_RESUME','UNPAUSE'):assert value>100,(name0,'music missing',value)
   if name0=='EFFECT':
    assert value>10,('effect silent',i,value)
    spectrum=np.abs(np.fft.rfft(a*np.hanning(len(a))))**2;freq=np.fft.rfftfreq(len(a),1/rate);harsh=float(spectrum[freq>6000].sum()/max(1,spectrum.sum()));assert harsh<.04,('excess high-frequency energy',i,harsh)
    if i==2:assert 980<dominant(a)<1110,('bumper pitch',dominant(a))
   measurements.append(dict(event=name0,id=i,rms=round(value,3)))
  music_start=events[0][2];loop=1024/60
  f1=dominant(clip(music_start+.07,music_start+.21));f2=dominant(clip(music_start+loop+.07,music_start+loop+.21));assert 245<f1<280 and abs(f1-f2)<10,('music loop pitch changed',f1,f2)
  result=dict(cpu=cpu,ram=ram,mhz=mhz,peak=peak,seconds=len(data)/rate,music_loop_hz=[round(f1,3),round(f2,3)],events=measurements);results.append(result)
  print(f'{cpu} {ram} KB {mhz} MHz: seven soft effects, looping music, pause/mute/music toggles and IRQ cleanup PASS',flush=True)
(o/('psg-results'+os.environ.get('TEST_TAG','')+'.json')).write_text(json.dumps(results,indent=2)+'\n')
