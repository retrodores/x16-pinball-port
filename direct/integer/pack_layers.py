#!/usr/bin/env python3
"""Pack original walls, seven bumpers, and ramp layer-transition records."""
from pathlib import Path
import json,math,struct
root=Path(__file__).resolve().parents[1]
j=json.loads((root/'data/layers.json').read_text())
edges=[e for e in j['edges'] if e['active'] and e['class'] in ['5TWall','11TTableLayer','7TBumper','8TPlunger','6TDrain','5TRamp']]
bumper_ids=[372,380,388,396,405,413,421]
grid=[[] for _ in range(768)];records=[];bounds=[]
def q(v):return max(-2147483647,min(2147483647,round(v*4096)))
for idx,e in enumerate(edges):
 kind={'8TPlunger':1,'6TDrain':2,'5TRamp':10}.get(e['class'],0)
 if e['class']=='7TBumper':kind=3+bumper_ids.index(e['component'])
 if 'line' in e:
  x,y,ex,ey=e['line'];dx,dy=ex-x,ey-y;length=math.hypot(dx,dy);dx/=length;dy/=length
  lo,hi=sorted((x,ex) if abs(dx)>=1e-9 else (y,ey))
  if abs(dx)<1e-9:dx=0
  shape=[dy,-dx,dx,dy,x,y,ex,ey,lo,hi,0,0];typ=0
  lx,hx=sorted((x,ex));ly,hy=sorted((y,ey))
 else:
  x,y,r2=e['circle'];r=math.sqrt(r2);shape=[x,y,r2]+[0]*9;typ=1
  lx,hx=x-r,x+r;ly,hy=y-r,y+r
 values=list(map(q,[e['elasticity'],e['smoothness'],e['threshold'],e['boost'],*shape]))
 plane=(values[4]*values[8]+values[5]*values[9])//4096 if typ==0 else 0
 rec=struct.pack('<BBH17i',typ|(e['mask']<<1),kind,e['component']&65535,*values,plane)
 if kind==10:
  m=e['ramp'];rec+=struct.pack('<4B7i',m['action'],m['mask'],m['zflag'],0,*map(q,[*m['plane'],*m['force'],m['drag'],m['z']]))
 records.append(rec.ljust(128,b'\0'))
 bounds.append([math.floor(lx*256)-1,math.floor(ly*256)-1,math.ceil(hx*256)+1,math.ceil(hy*256)+1])
 for gx in range(max(0,math.floor(lx-.151)+12),min(23,math.floor(hx+.151)+12)+1):
  for gy in range(max(0,math.floor(ly-.151)+16),min(31,math.floor(hy+.151)+16)+1):grid[gx+gy*24].append(idx)
assert len(edges)<1024 and max(map(len,grid))<=63
blob=bytearray(b''.join(struct.pack('<64H',len(ids),*ids,*([65535]*(63-len(ids)))) for ids in grid)+b''.join(records))
blob[126:128]=b'CY' # version distinguishes the layered integer record layout
off=(len(blob)+8191)//8192*8192;blob.extend(b'\0'*(off-len(blob)))
blob.extend(b''.join(struct.pack('<4h',*b) for b in bounds))
(root/'build/integer/WORLD.BIN').write_bytes(blob)
(root/'build/integer/src/edge_bounds.h').write_text('#pragma once\nconstexpr unsigned char edge_bounds_bank=%d;\n'%(32+off//8192))
(root/'build/integer/layers-manifest.json').write_text(json.dumps({'edges':len(edges),'bumper_ids':bumper_ids,'ramp_edges':sum(e['class']=='5TRamp' for e in edges),'max_candidates':max(map(len,grid)),'bounds_bank':32+off//8192,'bytes':len(blob)},indent=2)+'\n')

fixtures=[]
for idx,e in enumerate(edges):
 if 'ramp' not in e:continue
 m=e['ramp']
 if m['action'] in [2,3] or (m['action']==1 and e['mask']!=2):
  fixtures.append('{%d,%d,%d,%d,{%s}}'%(idx,m['action'],e['mask'],m['mask'],','.join(str(q(v)) for v in e['line'])))
(root/'build/integer/src/ramp-fixtures.h').write_text('struct RampFixture{uint16_t id;uint8_t action,from,to;int32_t line[4];};\nstatic const RampFixture ramps[]={'+','.join(fixtures)+'};\n')
