#!/usr/bin/env python3
"""Record actual VERA output and validate every original effect on both CPUs."""
from pathlib import Path
import os,re,subprocess as sp,time,wave,json
import numpy as np
from scipy.signal import correlate
root=Path(__file__).resolve().parents[1]
out=root/'wireframe/evidence';out.mkdir(parents=True,exist_ok=True)
results=[]
manifest=json.loads((root/'direct/build/integer/audio-manifest.json').read_text())
source=np.frombuffer((root/'assets/SFX.BIN').read_bytes(),dtype='i1').astype(float)
for cpu in ('c02','c816'):
 for ram in (512,2048):
  build=root/'wireframe/build'
  name=f'audio-{cpu}-{ram}';log=out/(name+'.log');wav=out/(name+'.wav')
  with log.open('w') as stream:
   p=sp.Popen(['/opt/x16emu-r49/x16emu','-'+cpu,'-rom','/opt/x16emu-r49/rom.bin','-ram',str(ram),'-mhz','8','-warp','-echo','raw','-wav',str(wav)+',wait','-fsroot',str(build),'-prg',str(build/cpu/'audio.prg'),'-run'],stdout=stream,stderr=stream,env=dict(os.environ,SDL_AUDIODRIVER='dummy',SDL_VIDEODRIVER='dummy'))
   try:
    deadline=time.monotonic()+70
    while '# AUDIO DONE' not in log.read_text(errors='replace'):
     assert p.poll() is None,'emulator exited early'
     assert time.monotonic()<deadline,'audio IRQ test timed out'
     time.sleep(.1)
    time.sleep(.1)
   finally:
    p.terminate()
    try:p.wait(timeout=5)
    except sp.TimeoutExpired:p.kill();p.wait()
  text=log.read_text(errors='replace');assert not re.search(r'^not ok',text,re.M),text
  events=[(int(i,16),int(t,16)/8e6) for i,t in re.findall(r'# EFFECT (\w+) (\w+)',text)]
  assert len(events)==7
  with wave.open(str(wav)) as w:
   assert w.getsampwidth()==2
   rate=w.getframerate();channels=w.getnchannels();data=np.frombuffer(w.readframes(w.getnframes()),'<i2').reshape(-1,channels)
  duration=len(data)/rate;assert 8.5<duration<13,duration
  rms=[];correlations=[];offset=0
  for index,(effect,start) in enumerate(events):
   end=events[index+1][1] if index+1<len(events) else duration
   segment=data[max(0,int(start*rate)):min(len(data),int(end*rate))].astype(np.float64)
   value=float(np.sqrt(np.mean(segment*segment)));assert value>5,(cpu,ram,effect,value)
   rms.append(round(value,2))
   # Check the complete waveform, including samples across RAM bank boundaries.
   n=manifest['lengths'][effect];pcmrate=25e6/512*21/128
   indices=np.minimum(np.floor(np.arange(int(n*rate/pcmrate))*pcmrate/rate).astype(int),n-1)
   expected=source[offset:offset+n][indices];offset+=n;expected-=expected.mean()
   lo=max(0,int((start-.03)*rate));hi=min(len(data),int((start+n/pcmrate+.05)*rate))
   segment=data[lo:hi,0].astype(float)
   k=int(np.argmax(correlate(segment,expected,mode='valid',method='fft')))
   similarity=float(np.corrcoef(segment[k:k+len(expected)],expected)[0,1])
   assert similarity>.95,(cpu,ram,effect,'waveform mismatch',similarity)
   correlations.append(round(similarity,5))
  results.append({'cpu':cpu,'ram_kb':ram,'seconds':duration,'rate':rate,'effect_rms':rms,'source_correlations':correlations})
  print(f'{cpu} {ram} KB: seven recorded effects, IRQ banking/arithmetic, mute, stop and cleanup PASS',flush=True)
(out/'audio-results.json').write_text(json.dumps(results,indent=2)+'\n')
