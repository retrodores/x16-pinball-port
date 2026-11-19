from pathlib import Path
import subprocess as sp,time,os,wave,json,hashlib,re
import numpy as np
from PIL import Image,ImageChops,ImageDraw
r=Path(__file__).resolve().parents[2];o=r/'cadet/play-build'
ram=os.environ.get('CADET_RAM','512');tag=''if ram=='512'else'-'+ram
inputs={n:hashlib.sha256((o/n).read_bytes()).hexdigest()for n in('CADET.PRG','CADET.RUL','CADET.PHY')}
def output(name):
 p=Path(name);return o/(p.stem+tag+p.suffix)
with (output('ui.log')).open('w')as f:
 p=sp.Popen(['/opt/x16emu-r49/x16emu','-c02','-rom','/opt/x16emu-r49/rom.bin','-ram',ram,'-mhz','8','-scale','1','-echo','raw','-fsroot',str(o),'-prg',str(o/'CADET.PRG'),'-run','-wav',str(output('ui.wav'))+',auto'],stdout=f,stderr=f,env=dict(os.environ,SDL_AUDIODRIVER='dummy'))
 try:
  w=sp.check_output(['xdotool','search','--sync','--onlyvisible','--name','Commander X16'],timeout=10).decode().splitlines()[0]
  sp.run(['xdotool','windowfocus',w],check=True)
  deadline=time.monotonic()+30
  while '# PLAY READY'not in (output('ui.log')).read_text(errors='replace'):
   assert time.monotonic()<deadline;time.sleep(.2)
  time.sleep(.5)
  def action(cmd,key):sp.run(['xdotool',cmd,'--window',w,key],check=True)
  def shot(n):
   dest=output(n+'.png');sp.run(['import','-window',w,str(dest)],check=True);return Image.open(dest).convert('RGB')
  def scaled(box):
   x1,y1,x2,y2=box
   return x1*128//119,y1*128//117,x2*128//119,y2*128//117
  ready=shot('ready')
  margin=480-ready.crop((0,0,400,480)).getbbox()[3]
  assert 4<=margin<=12,('cabinet bottom margin',margin)
  packed=Image.open(o/'dynamic-rest.png').convert('RGB')
  # Original new-ball gate lamps flash; compare the static region independently.
  actual=ready.crop((0,0,340,372))
  x=np.arange(340)*119//128;y=np.arange(372)*117//128
  expected=Image.fromarray(np.asarray(packed)[y[:,None],x])
  blink_boxes=[scaled(box) for box in ((298,348,311,363),(51,328,64,343),(290,210,300,221),(50,257,61,269))]
  for box in blink_boxes:
   ImageDraw.Draw(actual).rectangle(box,fill=0);ImageDraw.Draw(expected).rectangle(box,fill=0)
  assert ImageChops.difference(actual,expected).getbbox()is None,'static background differs from packed pixels'
  flashed=False
  for i in range(6):
   time.sleep(.06);lamp=shot('lamp-'+str(i))
   flashed|=any(ImageChops.difference(ready.crop(box),lamp.crop(box)).getbbox()is not None for box in blink_boxes)
  assert flashed,'original new-ball gate lamps do not animate'
  action('keydown','space');time.sleep(2);pulled=shot('pulled')
  assert ImageChops.difference(ready.crop(scaled((320,375,370,437))),pulled.crop(scaled((320,375,370,437)))).getbbox(),'plunger not animated'
  action('keyup','space');time.sleep(.8);shot('launched')
  action('keydown','z');action('keydown','slash');time.sleep(.3);raised=shot('flippers')
  assert ImageChops.difference(ready.crop(scaled((120,355,260,420))),raised.crop(scaled((120,355,260,420)))).getbbox(),'flippers not animated'
  action('keyup','z');action('keyup','slash');time.sleep(8);shot('playing')
  action('key','F2');time.sleep(.5);shot('new-game')
  music_on=shot('music-on')
  action('key','m');time.sleep(.3);music_off=shot('music-off')
  box=scaled((530,421,554,429))
  assert ImageChops.difference(music_on.crop(box),music_off.crop(box)).getbbox(),'music OFF indicator unchanged'
  restart_started=time.monotonic();action('key','m')
  while True:
   time.sleep(.1);music_again=shot('music-restarted')
   if ImageChops.difference(music_on.crop(box),music_again.crop(box)).getbbox()is None:break
   assert time.monotonic()-restart_started<5,'music ON indicator did not recover within five seconds'
  music_restart_seconds=time.monotonic()-restart_started
  action('key','Escape');time.sleep(.4)
  assert '# DONE'in(output('ui.log')).read_text(errors='replace'),'exit failed'
 finally:
  p.terminate()
  try:p.wait(timeout=5)
  except sp.TimeoutExpired:p.kill();p.wait()
with wave.open(str(output('ui.wav')))as f:
 a=np.frombuffer(f.readframes(f.getnframes()),'<i2').astype(float)
 report={'ram_kb':int(ram),'music_restart_seconds':music_restart_seconds,'audio_rms':float(np.sqrt(np.mean(a*a))),'peak':float(np.max(np.abs(a))),'samples':len(a)}
assert report['audio_rms']>20,report
report['inputs_sha256']=inputs
result=re.findall(r'# RESULT ([0-9a-f ]+)',output('ui.log').read_text(errors='replace'))
if result:
 values=[int(v,16)for v in result[-1].split()]
 report.update(reported_frame=values[0],worst_cycles=values[1],mean_cycles=values[2])
(output('ui-test.json')).write_text(json.dumps(report,indent=2)+'\n')
print('UI test PASS',report)
