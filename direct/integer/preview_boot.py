#!/usr/bin/env python3
"""Run under xvfb-run. Boots the distribution PRG and sends actual SDL keys."""
from pathlib import Path
import os, subprocess as sp, sys, time
root=Path(__file__).resolve().parents[2]
ram=sys.argv[1] if len(sys.argv)>1 else '512'
out=root/'evidence/integer-preview';out.mkdir(parents=True,exist_ok=True)
log=out/f'normal-{ram}.log'
with log.open('w') as stream:
 p=sp.Popen(['/opt/x16emu-r49/x16emu','-rom','/opt/x16emu-r49/rom.bin',
  '-ram',ram,'-mhz','8','-scale','1','-echo','raw',
  '-fsroot',str(root/'direct/build/integer/preview'),'-prg',str(root/'direct/build/integer/preview/CMDRX.PRG'),'-run'],
  stdout=stream,stderr=stream,env=dict(os.environ,SDL_AUDIODRIVER='dummy'))
 try:
  window=sp.check_output(['xdotool','search','--sync','--onlyvisible','--name','Commander X16'],timeout=10).decode().splitlines()[0]
  sp.run(['xdotool','windowfocus',window],check=True)
  time.sleep(3)
  def key(kind,k):sp.run(['xdotool',kind,'--window',window,k],check=True)
  def shot(name):sp.run(['import','-window',window,str(out/f'{name}-{ram}.png')],check=True)
  shot('start');key('key','n');time.sleep(4);shot('fed')
  key('keydown','space');time.sleep(10);shot('charged')
  key('keyup','space');time.sleep(2);shot('launched')
  key('keydown','Shift_L');key('keydown','Shift_R');time.sleep(1);shot('flippers')
  key('keyup','Shift_L');key('keyup','Shift_R')
  key('key','p');time.sleep(.5);shot('paused')
  key('key','p');time.sleep(.5);key('key','Escape');time.sleep(1);shot('exit')
  stream.flush()
  assert 'CMDRX CADET PREVIEW ENDED' in log.read_text(errors='replace'),'ESC did not restore BASIC'
  print(f'normal boot, SDL keys and clean exit completed on {ram} KB')
 finally:
  p.terminate()
  try:p.wait(timeout=5)
  except sp.TimeoutExpired:p.kill();p.wait()
