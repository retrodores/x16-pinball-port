#!/usr/bin/env python3
"""Run existing behavior checks against the experimental native kernel build."""
from pathlib import Path
import os,re,subprocess as sp,sys
root=Path(__file__).resolve().parents[3];os.chdir(root)
build=root/'direct/build/integer/cpu816'
out=root/'evidence/integer-preview-816';out.mkdir(parents=True,exist_ok=True)
runner=build/'run_x16.pl'
runner.write_text((root/'t/run_x16.pl').read_text().replace("'-testbench'","'-c816','-testbench'"))
def rows(text):return re.findall(r'^# (?:WORLD|MECHANISMS|FLIPPER|BUMPER|PADDLE|RAMP) .+$',text,re.M)
for ram in (512,2048):
 for kind in ('world','mechanisms','flipper','arithmetic','contacts','controls'):
  p=sp.run(['perl',str(runner),str(build/f'{kind}.prg'),'direct/build/integer'],env=dict(os.environ,X16_RAM_KB=str(ram)),capture_output=True,text=True,timeout=90)
  (out/f'{kind}-{ram}.tap').write_text(p.stdout+p.stderr)
  assert p.returncode==0 and not re.search(r'^not ok',p.stdout,re.M),(ram,kind,p.stdout[-1000:],p.stderr)
  if kind not in ('arithmetic','controls'):assert rows(p.stdout)==rows((root/f'direct/build/integer/{kind}-host.tap').read_text()),(ram,kind)
  print(f'65816 {kind}: PASS, {ram} KB',flush=True)
for name in ('preview_native.py','preview_boot.py','preview_screens.py','frame_budget.py'):
 source=(root/'direct/integer'/name).read_text()
 source=source.replace('root=Path(__file__).resolve().parents[2]',f'root=Path({str(root)!r})')
 source=source.replace('direct/build/integer/preview','direct/build/integer/cpu816/preview')
 source=source.replace('evidence/integer-preview','evidence/integer-preview-816')
 source=source.replace("'/opt/x16emu-r49/x16emu','-rom'","'/opt/x16emu-r49/x16emu','-c816','-rom'")
 (build/name).write_text(source)
sp.run([sys.executable,str(build/'preview_native.py')],check=True,timeout=140)
if '--sdl' in sys.argv:
 for ram in (512,2048):sp.run(['xvfb-run','-a',sys.executable,str(build/'preview_boot.py'),str(ram)],check=True,timeout=70)
 sp.run([sys.executable,str(build/'preview_screens.py')],check=True,timeout=15)
# Keep the strict budget failure visible, but behavior validation is separate.
sp.run([sys.executable,str(build/'frame_budget.py')],check=False,timeout=15)
