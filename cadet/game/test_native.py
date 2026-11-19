from pathlib import Path
import subprocess as sp,time,os,re,json,sys
r=Path(__file__).resolve().parents[2];o=r/'cadet/play-build';ram=sys.argv[1];mhz=sys.argv[2]if len(sys.argv)>2 else '8'
expected=int(sys.argv[3]) if len(sys.argv)>3 else 6000
program=sys.argv[4] if len(sys.argv)>4 else 'TEST.PRG'
assert 1<=expected<=60000,expected
tag=f'native-{ram}-{mhz}' + (f'-{expected}' if expected!=6000 else '') + ('-'+Path(program).stem.lower() if program!='TEST.PRG' else '')
log=o/(tag+'.log')
with log.open('w')as f:
 p=sp.Popen(['/opt/x16emu-r49/x16emu','-c02','-rom','/opt/x16emu-r49/rom.bin','-ram',ram,'-mhz',mhz,'-warp','-echo','raw','-fsroot',str(o),'-prg',str(o/program),'-run'],stdout=f,stderr=f,env=dict(os.environ,SDL_AUDIODRIVER='dummy',SDL_VIDEODRIVER='dummy'))
 try:
  deadline=time.monotonic()+max(240,expected*.06)
  while '# DONE'not in log.read_text(errors='replace'):
   assert p.poll()is None
   assert time.monotonic()<deadline,'native timeout'
   assert '# LOAD FAILED'not in log.read_text(errors='replace')
   time.sleep(.25)
 finally:
  p.terminate()
  try:p.wait(timeout=5)
  except sp.TimeoutExpired:p.kill();p.wait()
s=log.read_text(errors='replace')
v=[int(n,16)for n in re.search(r'# RESULT ([0-9a-f ]+)',s)[1].split()]
report=dict(zip(['frames','max_cycles','mean_cycles','over_budget','missed_frame_starts','irq_max','music_errors'],v));report.update(ram=int(ram),mhz=int(mhz),expected_frames=expected,program=program)
report['budget_pass']=report['max_cycles']<=133333 if mhz=='8' else None
(o/(tag+'.json')).write_text(json.dumps(report,indent=2)+'\n');print(report)
assert report['frames']==expected and report['music_errors']==0
if mhz=='8':assert report['max_cycles']<=133333,report
