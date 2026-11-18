from pathlib import Path
from PIL import Image,ImageChops
import subprocess as sp,time,os,wave
import numpy as np
r=Path(__file__).resolve().parents[1];o=r/'cadet/build'
with (o/'keyboard-lab.log').open('w')as f:
 p=sp.Popen(['/opt/x16emu-r49/x16emu','-c02','-rom','/opt/x16emu-r49/rom.bin','-ram','512','-mhz','8','-scale','1',
 '-echo','raw','-fsroot',str(o),'-prg',str(o/'LAB.PRG'),'-run','-wav',str(o/'keyboard-lab.wav')+',auto'],stdout=f,stderr=f,env=dict(os.environ,SDL_AUDIODRIVER='dummy'))
 try:
  w=sp.check_output(['xdotool','search','--sync','--onlyvisible','--name','Commander X16'],timeout=10).decode().splitlines()[0]
  sp.run(['xdotool','windowfocus',w],check=True);time.sleep(5)
  def key(k):sp.run(['xdotool','key','--window',w,k],check=True);time.sleep(.2)
  def shot(n):
   path=o/n;sp.run(['import','-window',w,str(path)],check=True);return Image.open(path).convert('RGB')
  before=shot('lab-ready.png')
  reference=Image.open(o/'x16-layout.png').convert('RGB')
  assert before.size==(640,480),before.size
  # Exclude the separate status text layer; background pixels must be exact.
  assert ImageChops.difference(before.crop((0,0,384,470)),reference.crop((0,0,384,470))).getbbox()is None,'VERA tile output differs from packed pixels'
  key('m');key('Right');key('Right');key('space');time.sleep(8);during=shot('lab-playing.png')
  assert ImageChops.difference(before.crop((384,368,640,400)),during.crop((384,368,640,400))).getbbox(),'keys did not update status'
  assert ImageChops.difference(before.crop((0,0,384,470)),during.crop((0,0,384,470))).getbbox()is None,'audio IRQ corrupted graphics'
  key('s');time.sleep(.5);key('Escape');time.sleep(1);shot('lab-exit.png')
  assert 'FIDELITY LAB ENDED' in (o/'keyboard-lab.log').read_text(errors='replace'),'exit failed'
 finally:
  p.terminate()
  try:p.wait(timeout=5)
  except sp.TimeoutExpired:p.kill();p.wait()
with wave.open(str(o/'keyboard-lab.wav'))as f:
 a=np.frombuffer(f.readframes(f.getnframes()),'<i2').astype(float)
 assert np.sqrt(np.mean(a*a))>20,'audio silent'
print('Normal PRG: native-resolution pixels, selection, PCM, music, stop and clean exit PASS')
