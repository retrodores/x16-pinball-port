from pathlib import Path
import subprocess as sp,time,os,wave,json,hashlib,re
import numpy as np
from PIL import Image,ImageChops,ImageDraw
r=Path(__file__).resolve().parents[1];o=Path(os.environ['CADET_RELEASE_DIR'])
ram=os.environ.get('CADET_RAM','512');tag=''if ram=='512'else'-'+ram
prg=os.environ.get('CADET_TEST_PRG','CADET')
score_digits=os.environ.get('CADET_TEST_SCORE_DIGITS')=='1'
inputs={prg+suffix:hashlib.sha256((o/(prg+suffix)).read_bytes()).hexdigest()
        for suffix in ('.PRG','.RUL','.PHY')}
def output(name):
 p=Path(name);return o/(p.stem+tag+p.suffix)
with (output('ui.log')).open('w')as f:
 p=sp.Popen(['/opt/x16emu-r49/x16emu','-c02','-rom','/opt/x16emu-r49/rom.bin','-ram',ram,'-mhz','8','-scale','1','-echo','raw','-fsroot',str(o),'-prg',str(o/(prg+'.PRG')),'-run','-wav',str(output('ui.wav'))+',auto'],stdout=f,stderr=f,env=dict(os.environ,SDL_AUDIODRIVER='dummy'))
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
  def purple_glyphs(image,box):
   red,green,blue=np.asarray(image.crop(scaled(box)),dtype=np.int16).transpose(2,0,1)
   return np.count_nonzero((blue>=green+25)&(red>=green+20)&(blue>=red+20))
  large_messages=os.environ.get('CADET_TEST_LARGE_MESSAGES')=='1'
  split_panes=os.environ.get('CADET_TEST_SPLIT_PANES')=='1'
  message=(405,306,570,378) if split_panes else (405,244,555,288) if large_messages else (405,248,565,270)
  player=(405,244,570,288)
  ready=shot('ready')
  if split_panes:
   assert purple_glyphs(ready,player)>60,'Player 1 is missing from upper pane'
   assert purple_glyphs(ready,(405,268 if score_digits else 261,570,288))==0,'upper pane has extra message rows'
   for top in ((309,332,355) if score_digits else (306,324,342)):
    assert purple_glyphs(ready,(405,top,570,top+15))>25,('launch message row missing',top)
   blank_top=374 if score_digits else 361
   assert ready.crop(scaled((405,blank_top,570,387))).getbbox() is None,'controls legend remains'
   if score_digits:
    # The upper box digit and BALL count use the same 16x32 tile.
    def violet(box):
     r,g,b=np.asarray(ready.crop(scaled(box)),dtype=np.int16).transpose(2,0,1)
     return (b>r+40)&(r>g+15)
    player_one=violet((482,244,498,268))
    ball_one=violet((553,152,569,176))
    assert min(player_one.sum(),ball_one.sum())>=40
    assert abs(int(player_one.sum())-int(ball_one.sum()))<=12,'numeric glyph differs from BALL counter'
  elif large_messages:
   for top in (244,259,274):
    assert purple_glyphs(ready,(405,top,555,top+14))>25,('launch message row missing',top)
  assert purple_glyphs(ready,message)>40,'plunger status is missing purple text'
  margin=480-ready.crop((0,0,400,480)).getbbox()[3]
  assert 4<=margin<=12,('cabinet bottom margin',margin)
  if not split_panes:assert ready.crop(scaled((405,308,530,379))).getbbox(), 'controls panel is empty'
  assert ready.crop(scaled((398,407,583,433))).getbbox() is None, 'stray footer text'
  packed=Image.open(r/'cadet/play-build/dynamic-rest.png').convert('RGB')
  # Original new-ball gate lamps flash; compare the static region independently.
  actual=ready.crop((0,0,340,372))
  x=np.arange(340)*119//128;y=np.arange(372)*117//128
  expected=Image.fromarray(np.asarray(packed)[y[:,None],x])
  blink_boxes=[scaled(box) for box in ((298,348,311,363),(51,328,64,343),(290,210,300,221),(50,257,61,269))]
  for box in blink_boxes:
   ImageDraw.Draw(actual).rectangle(box,fill=0);ImageDraw.Draw(expected).rectangle(box,fill=0)
  assert ImageChops.difference(actual,expected).getbbox()is None,'static background differs from packed pixels'
  flashed=set()
  for i in range(12):
   time.sleep(.06);lamp=shot('lamp-'+str(i))
   for index,box in enumerate(blink_boxes):
    if ImageChops.difference(ready.crop(box),lamp.crop(box)).getbbox()is not None:
     flashed.add(index)
   if len(flashed)==len(blink_boxes):break
  assert len(flashed)==len(blink_boxes),('new-ball gate lamps did not all animate',sorted(flashed))
  # Check the real idle entry, an actual auto-play score, and two ways to exit.
  if os.environ.get('CADET_TEST_DEMO')=='1':
   caption=scaled(message)
   score=scaled((438,197,566,227))
   def changed(reference,current,box):
    return ImageChops.difference(reference.crop(box),current.crop(box)).getbbox() is not None
   deadline=time.monotonic()+(90 if split_panes else 45)
   while True:
    time.sleep(.4);attract=shot('attract')
    if changed(ready,attract,caption):break
    assert time.monotonic()<deadline,'idle demo did not appear'
   assert purple_glyphs(attract,message)>40,'demo caption is missing purple text'
   goal=scaled((405,329,570,350) if score_digits else (405,324,570,340) if split_panes else (405,259,555,274) if large_messages else (405,260,565,270))
   deadline=time.monotonic()+35
   while True:
    time.sleep(.4);playing_demo=shot('attract-playing')
    if changed(ready,playing_demo,score) and changed(attract,playing_demo,goal):break
    assert time.monotonic()<deadline,'demo never scored and advanced an objective through normal play'
   action('key','F2');time.sleep(.4);manual=shot('attract-f2')
   assert not changed(ready,manual,caption) and not changed(ready,manual,score),'F2 did not reset demo'
   action('key','F3');time.sleep(.4);manual_demo=shot('attract-f3')
   assert changed(ready,manual_demo,caption),'F3 did not start demo'
   action('keydown','z');time.sleep(.4);takeover=shot('attract-takeover')
   action('keyup','z')
   assert not changed(ready,takeover,caption),'flipper did not end demo'
   if split_panes:
    for scene in (attract,playing_demo,manual,manual_demo,takeover):
     assert not changed(ready,scene,scaled(player)),'demo modified Player 1 pane'
  action('keydown','space');time.sleep(2);pulled=shot('pulled')
  assert ImageChops.difference(ready.crop(scaled((320,375,370,437))),pulled.crop(scaled((320,375,370,437)))).getbbox(),'plunger not animated'
  action('keyup','space');time.sleep(.8);launched=shot('launched')
  assert purple_glyphs(launched,message)>30,'in-play status is missing purple text'
  if split_panes:
   assert purple_glyphs(launched,(405,324,570,378))==0,'stale lower pane rows during play'
   assert ImageChops.difference(ready.crop(scaled(player)),launched.crop(scaled(player))).getbbox() is None,'launch modified Player 1 pane'
  elif large_messages:
   assert purple_glyphs(launched,(405,259,555,288))==0,'stale launch glyphs after ball entered play'
  action('keydown','z');action('keydown','slash');time.sleep(.3);raised=shot('flippers')
  assert ImageChops.difference(ready.crop(scaled((120,355,260,420))),raised.crop(scaled((120,355,260,420)))).getbbox(),'flippers not animated'
  action('keyup','z');action('keyup','slash');time.sleep(8);shot('playing')
  action('key','F2');time.sleep(.5);shot('new-game')
  music_restart_seconds=None
  if not split_panes:
   music_on=shot('music-on')
   action('key','m');time.sleep(.3);music_off=shot('music-off')
   box=scaled((533,372,557,380))
   assert purple_glyphs(music_off,(533,372,557,380))>15,'music status is missing purple text'
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
