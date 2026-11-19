"""Regression fixtures for powered versus passive flipper contacts on r49."""
from pathlib import Path
import subprocess as sp, os, time
r=Path(__file__).resolve().parents[2];o=r/'cadet/play-build'
cc='/opt/llvm-mos-sdk-23.4.0/llvm-mos/bin/mos-cx16-clang'
sources=['wireframe/widemul.s','wireframe/sqrt.s','wireframe/narrowmul_shared.s','cadet/game/signedmul.s','cadet/game/fraction.s','cadet/game/ratio.s','cadet/game/bounds.s','cadet/game/test_flipper_contact.c']
from build_native import build_native
build_native('FLIPPER-CONTACT',sources)
for ram in ('512','2048'):
 log=o/f'flipper-contact-{ram}.log'
 with log.open('w') as f:
  p=sp.Popen(['/opt/x16emu-r49/x16emu','-c02','-rom','/opt/x16emu-r49/rom.bin','-ram',ram,'-warp','-echo','raw','-fsroot',str(o),'-prg',str(o/'FLIPPER-CONTACT.PRG'),'-run'],stdout=f,stderr=f,env=dict(os.environ,SDL_VIDEODRIVER='dummy',SDL_AUDIODRIVER='dummy'))
  try:
   deadline=time.monotonic()+60
   while '# DONE' not in log.read_text(errors='replace'):
    assert p.poll() is None and time.monotonic()<deadline,'emulator did not complete'
    time.sleep(.1)
  finally:
   p.terminate()
   try:p.wait(timeout=5)
   except sp.TimeoutExpired:p.kill();p.wait()
 assert '# FLIPPER PASS' in log.read_text(errors="replace"),log.read_text(errors="replace")
 print('Powered/passive flipper contacts PASS',ram,flush=True)
