#!/usr/bin/env python3
"""Exercise the actual distribution PRG using SDL keys; run under xvfb-run."""
from pathlib import Path
from PIL import Image,ImageChops
import os,subprocess as sp,sys,time,wave
r=Path(__file__).resolve().parents[1];cpu=sys.argv[1] if len(sys.argv)>1 else 'c02';ram=sys.argv[2] if len(sys.argv)>2 else '512'
o=r/'wireframe/evidence';mhz=sys.argv[3]if len(sys.argv)>3 else '8';name=f'keyboard-{cpu}-{ram}-{mhz}';log=o/(name+'.log')
with log.open('w') as stream:
 p=sp.Popen(['/opt/x16emu-r49/x16emu','-'+cpu,'-rom','/opt/x16emu-r49/rom.bin','-ram',ram,'-mhz',mhz,'-scale','1','-echo','raw','-fsroot',str(r/'wireframe/build'),'-prg',str(r/f'wireframe/build/{cpu}/CADET.PRG'),'-run','-wav',str(o/(name+'.wav'))+',auto'],stdout=stream,stderr=stream,env=dict(os.environ,SDL_AUDIODRIVER='dummy'))
 try:
  w=sp.check_output(['xdotool','search','--sync','--onlyvisible','--name','Commander X16'],timeout=10).decode().splitlines()[0]
  sp.run(['xdotool','windowfocus',w],check=True);time.sleep(3)
  def key(kind,k):sp.run(['xdotool',kind,'--window',w,k],check=True)
  def shot(n):
   path=o/(name+'-'+n+'.png');sp.run(['import','-window',w,str(path)],check=True);return Image.open(path).resize((320,240),Image.Resampling.NEAREST).convert('RGB')
  initial=shot('ready');key('key','m');time.sleep(.4);no_music=shot('music-off');assert ImageChops.difference(initial.crop((298,144,309,154)),no_music.crop((298,144,309,154))).getbbox(),'M key did not toggle music';key('key','m');time.sleep(.3);key('key','n');time.sleep(.5);served=shot('served')
  key('keydown','space');time.sleep(4);charged=shot('charged');assert ImageChops.difference(served.crop((180,197,192,215)),charged.crop((180,197,192,215))).getbbox(),'wireframe spring did not compress';key('keyup','space');time.sleep(1);launched=shot('launched')
  key('key','p');time.sleep(.4);paused=shot('paused');time.sleep(.4);paused2=shot('paused-again');assert ImageChops.difference(paused,paused2).getbbox() is None,'pause did not freeze the table'
  key('key','p');key('keydown','Shift_L');key('keydown','Shift_R');time.sleep(.3);raised=shot('flippers');key('keyup','Shift_L');key('keyup','Shift_R');time.sleep(.3);lowered=shot('lowered')
  assert ImageChops.difference(raised.crop((65,186,139,211)),lowered.crop((65,186,139,211))).getbbox(),'flipper sprites did not move'
  assert ImageChops.difference(served.crop((207,37,307,45)),launched.crop((207,37,307,45))).getbbox(),'launch status did not change'
  assert ImageChops.difference(served.crop((0,0,200,230)),launched.crop((0,0,200,230))).getbbox(),'ball did not leave launcher'
  palette=(r/'wireframe/build/PALETTE.BIN').read_bytes();a,b=palette[4:6];color=((b&15)*17,(a>>4)*17,(a&15)*17)
  assert all(charged.getpixel((x,156))==color for x in range(207,307)),'full charge did not register'
  key('key','Up');key('key','s');time.sleep(.3);key('key','s');time.sleep(.3);key('key','Escape');deadline=time.monotonic()+8
  while 'WIREFRAME ENDED' not in log.read_text(errors='replace') and time.monotonic()<deadline:time.sleep(.1)
  shot('exit');stream.flush()
  assert 'WIREFRAME ENDED' in log.read_text(errors='replace'),'ESC did not restore BASIC'
 finally:
  p.terminate()
  try:p.wait(timeout=5)
  except sp.TimeoutExpired:p.kill();p.wait()
with wave.open(str(o/(name+'.wav')))as f:
 assert f.getnframes()>f.getframerate()//10,'no recorded effect duration'
 import array
 samples=array.array('h',f.readframes(f.getnframes()));assert max(samples)-min(samples)>256,'recording was silent'
print(f'{cpu} {ram} KB {mhz} MHz: normal PRG, launch, visible plunger, flippers, pause, music/nudge/sound keys and clean exit PASS')
