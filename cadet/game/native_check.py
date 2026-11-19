"""CPU-helper and host/native state agreement checks on the actual r49 emulator."""
from pathlib import Path
import subprocess as sp,os,time,re,sys
r=Path(__file__).resolve().parents[2];o=r/'cadet/play-build'
cc='/opt/llvm-mos-sdk-23.4.0/llvm-mos/bin/mos-cx16-clang'
ram=sys.argv[1]if len(sys.argv)>1 else '512'
def run(name):
 log=o/f'{name}-{ram}.log'
 with log.open('w')as f:
  p=sp.Popen(['/opt/x16emu-r49/x16emu','-c02','-rom','/opt/x16emu-r49/rom.bin','-ram',ram,'-warp','-echo','raw','-fsroot',str(o),'-prg',str(o/(name+'.PRG')),'-run'],stdout=f,stderr=f,env=dict(os.environ,SDL_VIDEODRIVER='dummy',SDL_AUDIODRIVER='dummy'))
  try:
   deadline=time.monotonic()+180
   while '# DONE'not in log.read_text(errors='replace'):
    assert p.poll()is None and time.monotonic()<deadline
    time.sleep(.1)
  finally:
   p.terminate()
   try:p.wait(timeout=5)
   except sp.TimeoutExpired:p.kill();p.wait()
 return log.read_text(errors='replace')
math_sources=['wireframe/sqrt.s','wireframe/widemul.s','wireframe/narrowmul_shared.s','cadet/game/signedmul.s','cadet/game/fraction.s','cadet/game/ratio.s','cadet/game/test_math.c']
sp.run([cc,'-Os',*math_sources,'-o',str(o/'MATH3.PRG')],cwd=r,check=True)
s=run('MATH3');assert '# MATH PASS'in s,s;print('Native exact arithmetic PASS',ram,flush=True)
raw=(o/'THEME.ZSM').read_bytes()[16:]
for i,offset in enumerate(range(0,len(raw),65536)):(o/f'RAW{i}.BIN').write_bytes(raw[offset:offset+65536])
sp.run([cc,'-Os','cadet/game/audio.s','cadet/game/test_music_lz.c','-o',str(o/'MUSIC-LZ-TEST.PRG')],cwd=r,check=True)
s=run('MUSIC-LZ-TEST');assert '# MUSIC LZ PASS'in s,s;print('Native lossless music PASS',ram,'four exact stream comparisons, including buffered looping',flush=True)
sp.run([cc,'-Os','wireframe/sqrt.s','cadet/game/depth_quant.s','cadet/game/test_quant.c','-o',str(o/'QUANT-TEST.PRG')],cwd=r,check=True)
s=run('QUANT-TEST');assert '# QUANT PASS'in s,s;print('Native depth quantizer PASS',ram,flush=True)
sp.run([cc,'-Os','cadet/game/mask_pixels.s','cadet/game/test_pixels.c','-o',str(o/'PIXELS-TEST.PRG')],cwd=r,check=True)
s=run('PIXELS-TEST');assert '# PIXELS PASS'in s,s;print('Native pixel compositor PASS',ram,flush=True)
sp.run([cc,'-Os','cadet/game/bounds.s','cadet/game/test_bounds.c','-o',str(o/'BOUNDS-TEST.PRG')],cwd=r,check=True)
s=run('BOUNDS-TEST');assert '# BOUNDS PASS'in s,s;print('Native bounds PASS',ram,flush=True)
sp.run(['cc','-O2','-Icadet/play-build','cadet/game/engine.c','cadet/game/native_probe.c','-o',str(o/'probe-host')],cwd=r,check=True)
host=sp.check_output([str(o/'probe-host')],cwd=r,text=True);(o/'probe-host.log').write_text(host)
sources=['wireframe/widemul.s','wireframe/sqrt.s','wireframe/narrowmul_shared.s','cadet/game/signedmul.s','cadet/game/fraction.s','cadet/game/ratio.s','cadet/game/bounds.s','cadet/game/engine.c','cadet/game/native_probe.c']
from build_native import build_native
build_native('PROBE3',sources)
native=run('PROBE3')
a=re.findall(r'# STATE .*',host);b=re.findall(r'# STATE .*',native)
assert a==b,[(i,x,y)for i,(x,y)in enumerate(zip(a,b))if x!=y]
assert len(a)==50,len(a)
print('Native/host state PASS',ram,len(a),'checkpoints',flush=True)
