"""Run original mechanism pose patches on actual 65C02 VERA at both RAM sizes."""
from pathlib import Path
import subprocess as sp,os,time
r=Path(__file__).resolve().parents[2];o=r/'cadet/play-build'
cc='/opt/llvm-mos-sdk-23.4.0/llvm-mos/bin/mos-cx16-clang'
sp.run([cc,'-Os','-Icadet/play-build','cadet/game/dynamic.c','cadet/game/test_dynamic.c','-o',str(o/'DYNAMIC-TEST.PRG')],cwd=r,check=True)
for ram in ('512','2048'):
 log=o/f'dynamic-{ram}.log'
 with log.open('w')as f:
  p=sp.Popen(['/opt/x16emu-r49/x16emu','-c02','-rom','/opt/x16emu-r49/rom.bin','-ram',ram,'-warp','-echo','raw','-fsroot',str(o),'-prg',str(o/'DYNAMIC-TEST.PRG'),'-run'],stdout=f,stderr=f,env=dict(os.environ,SDL_VIDEODRIVER='dummy',SDL_AUDIODRIVER='dummy'))
  try:
   deadline=time.monotonic()+120
   while '# DONE' not in log.read_text(errors='replace'):
    assert p.poll()is None and time.monotonic()<deadline,'native dynamic test timeout'
    time.sleep(.1)
  finally:
   p.terminate()
   try:p.wait(timeout=5)
   except sp.TimeoutExpired:p.kill();p.wait()
 s=log.read_text(errors='replace');assert '# DYNAMIC PASS'in s,s
 print(ram,s[s.index('# DYNAMIC'):].strip(),flush=True)
