#!/usr/bin/env python3
from pathlib import Path
import json,math,struct
r=Path(__file__).resolve().parents[1]
j=json.loads((r/'build/table.json').read_text())
# First integration stage: base-plane physical walls, bumpers, plunger and drain.
# Preserve the full export for ramps, targets, gates and the rules-engine stage.
edges=[e for e in j['edges'] if e['mask']&1 and e['active'] and e['class'] in ['5TWall','11TTableLayer','7TBumper','8TPlunger','6TDrain']]
grid=[[] for _ in range(24*32)];records=[];bounds=[]
for idx,e in enumerate(edges):
 kind={'8TPlunger':1,'6TDrain':2,'7TBumper':3}.get(e['class'],0)
 if 'line' in e:
  x,y,ex,ey=e['line'];dx=ex-x;dy=ey-y;length=math.hypot(dx,dy);dx/=length;dy/=length
  # Same line_init data; runtime mutates only RayIntersect.
  minimum,maximum=sorted((x,ex) if abs(dx)>=1e-9 else (y,ey))
  if abs(dx)<1e-9:dx=0
  shape=[dy,-dx,dx,dy,x,y,ex,ey,minimum,maximum,0,0];typ=0
  loX,hiX=sorted((x,ex));loY,hiY=sorted((y,ey))
 else:
  x,y,r2=e['circle'];radius=math.sqrt(r2);shape=[x,y,r2]+[0]*9;typ=1
  loX=x-radius;hiX=x+radius;loY=y-radius;hiY=y+radius
 bounds.append([math.floor(loX*256)-1,math.floor(loY*256)-1,math.ceil(hiX*256)+1,math.ceil(hiY*256)+1])
 rec=struct.pack('<BBH16f',typ,kind,e['component']&65535,e['elasticity'],e['smoothness'],e['threshold'],e['boost'],*shape)
 records.append(rec.ljust(128,b'\0'))
 # Expand each box by one half-ball step; one cell suffices for that ray.
 for gx in range(max(0,math.floor(loX-.151)+12),min(23,math.floor(hiX+.151)+12)+1):
  for gy in range(max(0,math.floor(loY-.151)+16),min(31,math.floor(hiY+.151)+16)+1):
   grid[gx+gy*24].append(idx)
assert max(map(len,grid))<=63
blob=b''.join(struct.pack('<64H',len(ids),*ids,*([65535]*(63-len(ids)))) for ids in grid)+b''.join(records)
blob=bytearray(blob);blob[126:128]=b'CX'
# Bounds live in their own bank; only the current cell's small bounds cache is unbanked.
bounds_offset=(len(blob)+8191)//8192*8192
blob.extend(b'\0'*(bounds_offset-len(blob)))
blob.extend(b''.join(struct.pack('<4h',*b) for b in bounds))
(r/'build/WORLD.BIN').write_bytes(blob)
(r/'src/edge_bounds.h').write_text('// Conservative Q8.8 banked broad-phase bounds.\n#pragma once\nconstexpr unsigned char edge_bounds_bank=%d;\nconstexpr unsigned char max_cell_edges=%d;\n'%(32+bounds_offset//8192,max(map(len,grid))))
def f(v):
 s=format(v,'.9g')
 if '.' not in s and 'e' not in s:s+='.0'
 return s+'f'
(r/'src/world_params.h').write_text('#pragma once\n'+
 'constexpr float ball_radius='+f(j['radius'])+';\n'+
 'constexpr float gravity_x='+f(j['gravity'][0])+',gravity_y='+f(j['gravity'][1])+',drag='+f(j['gravity'][2])+';\n'+
 'constexpr float serve_x='+f(j['plunger'][0])+',plunger_y='+f(next(e['line'][1] for e in edges if e['class']=='8TPlunger'))+';\n')
(r/'src/world_manifest.json').write_text(json.dumps({'scope':'base-plane physical geometry; not the complete rules engine','full_export_edges':len(j['edges']),'included_edges':len(edges),'max_candidates':max(map(len,grid)),'bytes':len(blob),'start_bank':32,'edge_bank':44,'grid_origin':[-12,-16],'grid_size':[24,32]},indent=2)+'\n')
print(len(edges),'edges;',len(blob),'banked bytes')
