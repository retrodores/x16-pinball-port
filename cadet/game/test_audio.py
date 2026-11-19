"""Native restart, exact sample storage, bank-gap playback and routing checks."""
from pathlib import Path
import subprocess as sp,time,os,json,re,wave
import numpy as np
from scipy.signal import resample,fftconvolve
r=Path(__file__).resolve().parents[2];o=r/'cadet/play-build'
cc='/opt/llvm-mos-sdk-23.4.0/llvm-mos/bin/mos-cx16-clang'
catalog=json.loads((r/'cadet/build/audio-catalog.json').read_text())
manifest=json.loads((o/'resident-audio.json').read_text())
data=b''.join((o/f'PCM{i}.BIN').read_bytes() for i in range(len(manifest['load_banks'])))
offset=0
for bank,ptr,size,name in manifest['effects']:
 entry=next(e for e in catalog['assets'] if e['name']==name)
 expected=(r/'cadet/build/PCM'/entry['pcm']).read_bytes()
 assert data[offset:offset+size]==expected,name
 assert manifest['banks'][offset//8192]==bank and 0xa000+offset%8192==ptr,name
 offset+=size
assert offset==len(data)==manifest['bytes']==148242
sp.run(['cc','-O2','-Icadet/play-build','cadet/game/test_audio_events.c','-o',str(o/'audio-events-host')],cwd=r,check=True)
sp.run([str(o/'audio-events-host')],cwd=r,check=True)
sp.run([cc,'-Os','-Icadet/play-build','cadet/game/audio.s','cadet/game/test_audio_start.c','-o',str(o/'AUDIO-START.PRG')],cwd=r,check=True)
sp.run([cc,'-Os','cadet/game/audio.s','cadet/game/test_music_lz.c','-o',str(o/'MUSIC-LZ-TEST.PRG')],cwd=r,check=True)
raw=(o/'THEME.ZSM').read_bytes()[16:]
for i,offset in enumerate(range(0,len(raw),65536)):(o/f'RAW{i}.BIN').write_bytes(raw[offset:offset+65536])
def run(name,ram,record=False):
 log=o/f'{name.lower()}-{ram}.log'
 with log.open('w')as f:
  cmd=['/opt/x16emu-r49/x16emu','-c02','-rom','/opt/x16emu-r49/rom.bin','-ram',str(ram),'-mhz','8','-warp','-echo','raw','-fsroot',str(o),'-prg',str(o/(name+'.PRG')),'-run']
  if record:cmd+=['-wav',str(o/f'audio-start-{ram}.wav')+',auto']
  p=sp.Popen(cmd,stdout=f,stderr=f,env=dict(os.environ,SDL_VIDEODRIVER='dummy',SDL_AUDIODRIVER='dummy'))
  try:
   deadline=time.monotonic()+120
   while '# DONE'not in log.read_text(errors='replace'):
    assert p.poll()is None and time.monotonic()<deadline,'native audio test timeout'
    time.sleep(.1)
  finally:
   p.terminate()
   try:p.wait(timeout=5)
   except sp.TimeoutExpired:p.kill();p.wait()
 return log.read_text(errors='replace')
report={'pcm_bytes':len(data),'exact_stored_samples':len(manifest['effects']),'ram':{}}
for ram in (512,2048):
 s=run('MUSIC-LZ-TEST',ram);assert '# MUSIC LZ PASS'in s,s
 s=run('AUDIO-START',ram,True);assert '# AUDIO START PASS'in s,s
 costs=[int(x,16) for x in re.search(r'# AUDIO START ([0-9a-f]+) ([0-9a-f]+)',s).groups()]
 with wave.open(str(o/f'audio-start-{ram}.wav'))as f:
  rate=f.getframerate();a=np.frombuffer(f.readframes(f.getnframes()),'<i2').reshape(-1,f.getnchannels()).mean(axis=1)
 matches={}
 for name in ['SOUND43','SOUND17','SOUND49D','SOUND14','SOUND35']:
  b=np.frombuffer((r/'cadet/build/PCM'/(name+'.PCM')).read_bytes(),np.int8).astype(float)
  b=resample(b,round(len(b)*rate/11062.6220703125));b-=b.mean();n=len(b)
  corr=fftconvolve(a,b[::-1],mode='valid');cs=np.r_[0,np.cumsum(a*a)];power=cs[n:]-cs[:-n]
  corr=np.abs(corr)/np.sqrt(np.maximum(power,1)*np.dot(b,b));at=int(np.argmax(corr))
  matches[name]={'seconds':at/rate,'correlation':float(corr[at])}
  assert corr[at]>.90,(ram,name,matches[name])
 report['ram'][ram]={'music_start_cycles':costs[0],'prefetch_max_cycles':costs[1],'waveforms':matches,'music_lz_compared_bytes':856956}
 print('Native audio PASS',ram,costs,flush=True)
(o/'audio-validation.json').write_text(json.dumps(report,indent=2)+'\n')
print('Exact storage, four music loops, staged restart/cancel, routing and five sample playbacks PASS',flush=True)
