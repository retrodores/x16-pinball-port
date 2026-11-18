from pathlib import Path
import json,struct,random,subprocess as sp,os,time,sys
import numpy as np
r=Path(__file__).resolve().parents[2];o=r/'cadet/play-build'
inv=json.loads(Path('/opt/spacecadet-x16-analysis/evidence/inventory.json').read_text())
dat=Path('/opt/spacecadet-x16-analysis/input/game/PINBALL.DAT').read_bytes()
e=next(e for e in inv['groups'][107]['entries']if e['type']==12)
q=(np.frombuffer(dat[e['offset']+14:e['offset']+e['bytes']],'<u2').reshape(470,368)[::-1,:365]>>8).astype('B')
rng=random.Random(16502);cases=[]
for i in range(384):
 if i<96:x=rng.choice([-16,-1,0,1,48,49,63,64,127,128,319,320,348,349,350,364,365]);y=rng.choice([-16,-1,0,1,15,16,453,454,455,469,470])
 else:x=rng.randrange(350);y=rng.randrange(455)
 d=rng.choice([0,255,int(q[min(469,max(0,y)),min(364,max(0,x))]),rng.randrange(256)])
 masks=[sum(1<<px for px in range(16)if not(0<=x+px<365 and 0<=y+py<470)or int(q[y+py,x+px])>d)for py in range(16)]
 cases.append(struct.pack('<hhBB16H',x,y,d,0,*masks))
for i in range(2):(o/f'DEPCA{i}.BIN').write_bytes(b''.join(cases[i*192:(i+1)*192]))
cc='/opt/llvm-mos-sdk-23.4.0/llvm-mos/bin/mos-cx16-clang'
sp.run([cc,'-Os',str(r/'cadet/game/depth.c'),str(r/'cadet/game/depth_rect.s'),str(r/'cadet/game/test_depth.c'),'-o',str(o/'DEPTH-TEST.PRG')],check=True)
ram=sys.argv[1]if len(sys.argv)>1 else '512';log=o/f'depth-test-{ram}.log'
with log.open('w')as f:
 p=sp.Popen(['/opt/x16emu-r49/x16emu','-c02','-rom','/opt/x16emu-r49/rom.bin','-ram',ram,'-mhz','8','-warp','-echo','raw','-fsroot',str(o),'-prg',str(o/'DEPTH-TEST.PRG'),'-run'],stdout=f,stderr=f,env=dict(os.environ,SDL_VIDEODRIVER='dummy',SDL_AUDIODRIVER='dummy'))
 try:
  deadline=time.monotonic()+90
  while '# DONE'not in log.read_text(errors='replace'):
   assert p.poll()is None
   assert time.monotonic()<deadline
   time.sleep(.1)
 finally:
  p.terminate()
  try:p.wait(timeout=5)
  except sp.TimeoutExpired:p.kill();p.wait()
s=log.read_text(errors='replace');assert '# DEPTH PASS'in s,s
print('Depth native PASS',ram,'KB: 384 rectangles, 6144 rows, bank preservation')
