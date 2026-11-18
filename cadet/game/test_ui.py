from pathlib import Path
import subprocess as sp,time,os,wave,json
import numpy as np
from PIL import Image,ImageChops
r=Path(__file__).resolve().parents[2];o=r/'cadet/play-build'
with (o/'ui.log').open('w')as f:
 p=sp.Popen(['/opt/x16emu-r49/x16emu','-c02','-rom','/opt/x16emu-r49/rom.bin','-ram','512','-mhz','8','-scale','1','-echo','raw','-fsroot',str(o),'-prg',str(o/'CADET.PRG'),'-run','-wav',str(o/'ui.wav')+',auto'],stdout=f,stderr=f,env=dict(os.environ,SDL_AUDIODRIVER='dummy'))
 try:
  w=sp.check_output(['xdotool','search','--sync','--onlyvisible','--name','Commander X16'],timeout=10).decode().splitlines()[0]
  sp.run(['xdotool','windowfocus',w],check=True)
  deadline=time.monotonic()+30
  while '# PLAY READY'not in (o/'ui.log').read_text(errors='replace'):
   assert time.monotonic()<deadline;time.sleep(.2)
  time.sleep(.5)
  def action(cmd,key):sp.run(['xdotool',cmd,'--window',w,key],check=True)
  def shot(n):
   dest=o/(n+'.png');sp.run(['import','-window',w,str(dest)],check=True);return Image.open(dest).convert('RGB')
  ready=shot('ready')
  packed=Image.open(o/'x16-layout.png').convert('RGB')
  assert ImageChops.difference(ready.crop((0,0,320,340)),packed.crop((0,0,320,340))).getbbox()is None,'background differs from packed pixels'
  action('keydown','space');time.sleep(2);pulled=shot('pulled')
  assert ImageChops.difference(ready.crop((320,375,370,470)),pulled.crop((320,375,370,470))).getbbox(),'plunger not animated'
  action('keyup','space');time.sleep(.8);shot('launched')
  action('keydown','z');action('keydown','slash');time.sleep(.3);raised=shot('flippers')
  assert ImageChops.difference(ready.crop((120,355,260,420)),raised.crop((120,355,260,420))).getbbox(),'flippers not animated'
  action('keyup','z');action('keyup','slash');time.sleep(8);shot('playing')
  action('key','F2');time.sleep(.5);shot('new-game')
  action('key','m');time.sleep(.3);action('key','Escape');time.sleep(.4)
  assert '# DONE'in(o/'ui.log').read_text(errors='replace'),'exit failed'
 finally:
  p.terminate()
  try:p.wait(timeout=5)
  except sp.TimeoutExpired:p.kill();p.wait()
with wave.open(str(o/'ui.wav'))as f:
 a=np.frombuffer(f.readframes(f.getnframes()),'<i2').astype(float)
 report={'audio_rms':float(np.sqrt(np.mean(a*a))),'peak':float(np.max(np.abs(a))),'samples':len(a)}
assert report['audio_rms']>20,report
(o/'ui-test.json').write_text(json.dumps(report,indent=2)+'\n')
print('UI test PASS',report)
