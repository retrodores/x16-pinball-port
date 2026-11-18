#!/usr/bin/env python3
from pathlib import Path
import os,subprocess as sp,time,json,re,wave
r=Path(__file__).resolve().parents[1];o=r/'wireframe/evidence';o.mkdir(exist_ok=True);results=[];mhz=int(os.environ.get('TEST_MHZ','8'))
for cpu in os.environ.get('TEST_CPUS','c02 c816').split():
 for ram in map(int,os.environ.get('TEST_RAM','512 2048').split()):
  name=f'play-{cpu}-{ram}'+os.environ.get('TEST_TAG','');log=o/(name+'.log')
  with log.open('w')as stream:
   p=sp.Popen(['/opt/x16emu-r49/x16emu','-'+cpu,'-rom','/opt/x16emu-r49/rom.bin','-ram',str(ram),'-mhz',str(mhz),'-warp','-echo','raw','-fsroot',str(r/'wireframe/build'),'-prg',str(r/'wireframe/build'/cpu/os.environ.get('TEST_BINARY','auto.prg')),'-run','-wav',str(o/(name+'.wav'))+',auto','-gif',str(o/(name+'.gif'))+',wait'],stdout=stream,stderr=stream,env=dict(os.environ,SDL_VIDEODRIVER='dummy',SDL_AUDIODRIVER='dummy'))
   try:
    deadline=time.monotonic()+480
    while '# DONE' not in log.read_text(errors='replace'):
     assert p.poll()is None,'emulator stopped early'
     assert time.monotonic()<deadline,'sustained-play timeout'
     time.sleep(.25)
   finally:
    p.terminate()
    try:p.wait(timeout=5)
    except sp.TimeoutExpired:p.kill();p.wait()
  text=log.read_text(errors='replace');m=re.search(r'# RESULT ([0-9a-f ]+)',text);assert m,text[-2000:]
  n,maximum,average,missed,drains,returns=[int(x,16)for x in m[1].split()]
  assert drains==9,(name,'game did not finish',drains)
  host=(r/'wireframe/build/replay.log').read_text()
  assert re.findall(r'^# PLAY .+$',text,re.M)==re.findall(r'^# PLAY .+$',host,re.M),(name,'native/host replay mismatch')
  with wave.open(str(o/(name+'.wav'))) as f:assert f.getnframes()>f.getframerate()*5
  clock=re.search(r'# CLOCK ([0-9a-f ]+)',text);assert clock
  ticks,draws,max_gap,max_debt=[int(x,16)for x in clock[1].split()]
  gaps=[int(x,16)for x in re.search(r'# GAPS ([0-9a-f ]+)',text)[1].split()]
  assert abs(ticks-n)<=6,(name,'simulation lost real time',ticks,n)
  assert draws/ticks*60>=40,(name,'rendering below playable 40 FPS mean',draws,ticks)
  assert max_gap<=6,(name,'long visual freeze',max_gap)
  assert sum(gaps[3:])/draws<.01,(name,'frequent frames slower than 30 FPS')
  results.append(dict(cpu=cpu,ram=ram,mhz=mhz,frames=n,max_cycles=maximum,avg_cycles=average,over_budget=missed,drains=drains,returns=returns,video_ticks=ticks,draws=draws,mean_fps=round(draws/ticks*60,3),max_gap_ticks=max_gap,max_debt=max_debt,gap_histogram=gaps))
  print(json.dumps(results[-1]),flush=True)
(o/('results'+os.environ.get('TEST_TAG','')+'.json')).write_text(json.dumps(results,indent=2)+'\n')
assert mhz!=8 or all(row['max_cycles']<133333 and row['over_budget']==0 for row in results),'strict 8 MHz frame budget exceeded'
