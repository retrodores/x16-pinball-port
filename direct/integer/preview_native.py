#!/usr/bin/env python3
"""Normal-ROM boot of the instrumented UI; bounded and no testbench injection."""
from pathlib import Path
import os, subprocess as sp, time, shutil
root=Path(__file__).resolve().parents[2]
out=root/'evidence/integer-preview';out.mkdir(parents=True,exist_ok=True)
fs=root/'direct/build/integer/preview-test';fs.mkdir(exist_ok=True)
for f in (root/'direct/build/integer/preview').glob('*.BIN'):shutil.copyfile(f,fs/f.name)
shutil.copyfile(root/'direct/build/integer/preview/test-ui.bin',fs/'UI.BIN')
for ram in (512,2048):
 log=out/f'instrumented-{ram}.log'
 with log.open('w') as stream:
  p=sp.Popen(['/opt/x16emu-r49/x16emu','-rom','/opt/x16emu-r49/rom.bin',
   '-ram',str(ram),'-mhz','8','-warp','-sound','none','-echo','raw',
   '-fsroot',str(fs),'-prg',str(root/'direct/build/integer/preview/test.prg'),'-run',
   '-gif',str(out/f'instrumented-{ram}.gif')+',wait'],stdout=stream,stderr=stream,
   env=dict(os.environ,SDL_AUDIODRIVER='dummy',SDL_VIDEODRIVER='dummy'))
  try:
   deadline=time.monotonic()+60
   while '# EXIT' not in log.read_text(errors='replace'):
    assert p.poll() is None,'emulator exited before completing checks'
    assert time.monotonic()<deadline,'normal-boot test timed out'
    time.sleep(.1)
   text=log.read_text(errors='replace')
   for marker in ('BOOT','CHARGE+','PAUSE+','CHUTE+','FLIPPERS+','RELEASE+','EXIT'):
    assert '# '+marker in text,marker
   assert 'CMDRX CADET PREVIEW ENDED' in text
   time.sleep(.1)
  finally:
   p.terminate()
   try:p.wait(timeout=5)
   except sp.TimeoutExpired:p.kill();p.wait()
 print(f'normal ROM boot and direct-mechanics UI checks PASS on {ram} KB')
