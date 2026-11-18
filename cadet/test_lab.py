#!/usr/bin/env python3
from pathlib import Path
import os,sys,subprocess as sp,time,json,re,wave
import numpy as np
from scipy.signal import resample_poly,correlate
from fractions import Fraction
r=Path(__file__).resolve().parents[1];o=r/'cadet/build';mode=sys.argv[1];ram=sys.argv[2]
log=o/f'{mode}-{ram}.log';wav=o/f'{mode}-{ram}.wav'
if not os.environ.get('ANALYZE_ONLY'):
 with log.open('w')as f:
  p=sp.Popen(['/opt/x16emu-r49/x16emu','-c02','-rom','/opt/x16emu-r49/rom.bin','-ram',ram,'-mhz','8','-warp','-echo','raw',
              '-fsroot',str(o),'-prg',str(o/(mode+'.PRG')),'-run','-wav',str(wav)+',wait'],stdout=f,stderr=f,
             env=dict(os.environ,SDL_AUDIODRIVER='dummy',SDL_VIDEODRIVER='dummy'))
  try:
   deadline=time.monotonic()+600
   while '# DONE'not in log.read_text(errors='replace'):
    assert p.poll()is None,'emulator exited'
    assert time.monotonic()<deadline,'player timeout'
    assert 'LOAD FAILED'not in log.read_text(errors='replace'),'asset failed to load'
    time.sleep(.25)
  finally:
   p.terminate()
   try:p.wait(timeout=5)
   except sp.TimeoutExpired:p.kill();p.wait()
s=log.read_text(errors='replace')
stats=[int(x,16)for x in re.search(r'# STATS ([0-9a-f ]+)',s)[1].split()]
assert stats[0]<133333 and stats[4]==0,stats
events=[(n,int(i,16),int(t,16)/8_000_000)for n,i,t in re.findall(r'# EVENT (\w+) (\w+) (\w+)',s)]
with wave.open(str(wav))as w:
 rate=w.getframerate();channels=w.getnchannels();data=np.frombuffer(w.readframes(w.getnframes()),'<i2').reshape(-1,channels)[:,0].astype(float)
assert np.max(np.abs(data))>128,'recording silent'
report={'mode':mode,'ram':int(ram),'irq_max_cycles':stats[0],'fm_writes':stats[1],'psg_writes':stats[2],'loops':stats[3],
        'stream_errors':stats[4],'recorded_seconds':len(data)/rate,'peak':float(np.max(np.abs(data)))}
if mode=='MUSIC_TEST':
 assert stats[3]==1 and len(data)/rate>527,report
 elapsed=next(t for n,i,t in events if n=='LOOP')-next(t for n,i,t in events if n=='MUSIC')
 expected_seconds=json.loads((o/'music.json').read_text())
 report['loop_seconds']=elapsed
 assert abs(elapsed-527.933333)<.05,('music tempo drift',elapsed)
 assert np.sqrt(np.mean(data*data))>30,report
else:
 effects=[x for x in events if x[0]=='EFFECT'];catalog=json.loads((o/'audio-catalog.json').read_text())['assets']
 assert len(effects)==len(catalog)==60
 matches=[]
 for (name,i,t),asset in zip(effects,catalog):
  raw=np.frombuffer((o/'PCM'/asset['pcm']).read_bytes(),np.int8).astype(float)
  # Exact PCM amplitude/order check, independent of sample-hold phase.
  # At master volume 11, VERA multiplies signed 8-bit by 92; emulator mix by 2.
  # Its 48828 Hz integer host clock occasionally skips a VERA mix sample.
  assert rate==48828,rate
  a=max(0,int((t-.02)*rate));b=min(len(data),int((t+asset['pcm_seconds']+.05)*rate))
  clip=data[a:b].astype(np.int32)
  assert np.all(clip%184==0),(asset['name'],'unexpected amplitude')
  decoded=(clip//184).astype(np.int8)
  changes=np.r_[0,np.flatnonzero(decoded[1:]!=decoded[:-1])+1]
  wanted=np.r_[0,np.flatnonzero(raw[1:]!=raw[:-1])+1]
  # First/last silence belongs to a neighboring hold, not an onset marker.
  if raw[wanted[0]]==0:wanted=wanted[1:]
  if raw[wanted[-1]]==0:wanted=wanted[:-1]
  needle=raw[wanted].astype(np.int8).tobytes()
  offset=decoded[changes].tobytes().find(needle)
  assert offset>=0,(asset['name'],'PCM byte order mismatch')
  observed=changes[offset:offset+len(wanted)]
  # The first run can merge with the preceding held sample: compare transitions.
  error=(observed[1:]-observed[1])-(wanted[1:]-wanted[1])*rate/asset['actual_rate']
  maximum=float(np.max(np.abs(error)))
  # Allow <0.103 ms for emulator host-clock resampling; amplitude order is exact.
  assert maximum<5.0,(asset['name'],'PCM hold timing error',maximum)
  matches.append({'asset':asset['name'],'exact_amplitude_sequence':True,'amplitude_runs':len(wanted),'max_hold_error_mix_samples':maximum})
 report['effects']=matches
(o/f'{mode}-{ram}.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({k:v for k,v in report.items()if k!='effects'}),flush=True)
