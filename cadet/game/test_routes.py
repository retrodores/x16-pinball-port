"""Check original gateways/rails and stationary grazing tips on host/native 65C02."""
from pathlib import Path
import subprocess as sp,os,time,re,json
from build_native import build_native
r=Path(__file__).resolve().parents[2];o=r/'cadet/play-build'
arithmetic=['wireframe/widemul.s','wireframe/sqrt.s','wireframe/narrowmul_shared.s','cadet/game/signedmul.s','cadet/game/fraction.s','cadet/game/ratio.s','cadet/game/bounds.s']
reports=[]
for name,source in [('ROUTES','test_routes.c'),('TIP','test_routes_tip.c')]:
 source='cadet/game/'+source
 host_exe=o/(name.lower()+'-host')
 sp.run(['cc','-O2','-fsanitize=address,undefined','-Icadet/play-build',source,'-o',str(host_exe)],cwd=r,check=True)
 host=sp.check_output([str(host_exe)],cwd=r,text=True)
 build_native(name,[*arithmetic,source])
 for ram in ('512','2048'):
  log=o/f'{name.lower()}-{ram}.log'
  with log.open('w')as f:
   p=sp.Popen(['/opt/x16emu-r49/x16emu','-c02','-rom','/opt/x16emu-r49/rom.bin','-ram',ram,'-warp','-echo','raw','-fsroot',str(o),'-prg',str(o/(name+'.PRG')),'-run'],stdout=f,stderr=f,env=dict(os.environ,SDL_VIDEODRIVER='dummy',SDL_AUDIODRIVER='dummy'))
   try:
    deadline=time.monotonic()+60
    while '# DONE'not in log.read_text(errors='replace'):
     assert p.poll()is None and time.monotonic()<deadline,'native routes timeout'
     time.sleep(.1)
   finally:
    p.terminate()
    try:p.wait(timeout=5)
    except sp.TimeoutExpired:p.kill();p.wait()
  native=log.read_text(errors='replace')
  a=re.findall(r'# '+name+r' .*',host);b=re.findall(r'# '+name+r' .*',native)
  assert len(a)==1 and a==b and a[0].endswith(' PASS'),(host,native)
  row={'fixture':name,'ram_kb':int(ram),'result':a[0],'host_native_equal':True};reports.append(row)
  print(row,flush=True)
(o/'routes-results.json').write_text(json.dumps(reports,indent=2)+'\n')
