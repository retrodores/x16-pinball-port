"""Verify real lower-wall impacts become original six-frame VERA flashes."""
from pathlib import Path
import subprocess as sp,os,time,re,json,hashlib
from build_native import build_native
r=Path(__file__).resolve().parents[2];o=r/'cadet/play-build'
sources=['wireframe/widemul.s','wireframe/sqrt.s','wireframe/narrowmul_shared.s',
 'cadet/game/signedmul.s','cadet/game/fraction.s','cadet/game/ratio.s','cadet/game/bounds.s',
 'cadet/game/engine.c','cadet/game/dynamic.c','cadet/game/test_slingshot_render.c']
build_native('SLINGSHOT-TEST',sources)
report={'assets_sha256':{n:hashlib.sha256((o/n).read_bytes()).hexdigest()for n in ['TILES.BIN']+[f'DYN{i}.BIN'for i in range(4)]},'runs':[]}
for ram in ('512','2048'):
 log=o/f'slingshot-render-{ram}.log'
 with log.open('w')as f:
  p=sp.Popen(['/opt/x16emu-r49/x16emu','-c02','-rom','/opt/x16emu-r49/rom.bin','-ram',ram,'-mhz','8','-warp','-echo','raw','-fsroot',str(o),'-prg',str(o/'SLINGSHOT-TEST.PRG'),'-run'],stdout=f,stderr=f,env=dict(os.environ,SDL_VIDEODRIVER='dummy',SDL_AUDIODRIVER='dummy'))
  try:
   deadline=time.monotonic()+120
   while '# DONE'not in log.read_text(errors='replace'):
    assert p.poll()is None and time.monotonic()<deadline,'native slingshot-render timeout'
    time.sleep(.1)
  finally:
   p.terminate()
   try:p.wait(timeout=5)
   except sp.TimeoutExpired:p.kill();p.wait()
 s=log.read_text(errors='replace');match=re.search(r'# SLINGSHOT RENDER PASS ([0-9a-f]+) ([0-9a-f]+) ([0-9a-f]+)',s);assert match,s
 checks,errors,maximum=(int(x,16)for x in match.groups())
 report['runs'].append({'ram_kb':int(ram),'checks':checks,'errors':errors,'max_render_cycles':maximum,'first_display_call':True,'visible_frames':6})
 print(ram,match.group(),flush=True)
(o/'slingshot-render-test.json').write_text(json.dumps(report,indent=2)+'\n')
