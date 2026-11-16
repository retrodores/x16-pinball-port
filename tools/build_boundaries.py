#!/usr/bin/env python3
"""Bake original base-layer wall polygons into a radius-aware collision field."""
from pathlib import Path
import json,math
import numpy as np
from scipy.ndimage import distance_transform_edt,gaussian_filter
from PIL import Image,ImageDraw
root=Path(__file__).resolve().parents[1]
j=json.loads(Path('/opt/spacecadet-x16-analysis/evidence/inventory.json').read_text())
camera=next(e['values'] for e in j['groups'][3]['entries'] if e['type']==11)
def project(x,y,z=0):
 r=[camera[i]*x+camera[i+1]*y+camera[i+2]*z+camera[i+3] for i in (0,4,8)]
 return (8+(r[0]*camera[12]/r[2]+183)/2,2+(r[1]*camera[12]/r[2]+238)/2)
wallobjects=next(e['values'][1:] for e in j['groups'][540]['entries'] if e['type']==10)
mask=Image.new('L',(192,224),1);draw=ImageDraw.Draw(mask)
draw.polygon([(52,8),(146,8),(190,224),(8,224)],fill=0)
used=[]
for kind,gid in zip(wallobjects[::2],wallobjects[1::2]):
 if kind not in (1000,1010):continue
 entries=j['groups'][gid]['entries']
 ints=[e['values'] for e in entries if e['type']==10]
 if any(v[:2]==[602,2] for v in ints):continue
 shapes=[e['values'] for e in entries if e['type']==11 and e['values'][0]==600]
 if not shapes:continue
 vals=shapes[0];count=int(vals[1]);v=vals[2:]
 if count==1:
  cx,cy=project(v[0],v[1]);px,py=project(v[0]+abs(v[2]),v[1]);radius=max(.5,abs(px-cx))
  draw.ellipse((cx-radius,cy-radius,cx+radius,cy+radius),fill=1)
 elif count>=3:
  pts=[project(v[i*2],v[i*2+1]) for i in range(count)]
  draw.polygon(pts,fill=1)
 else:continue
 used.append(gid)
solid=np.array(mask,dtype=bool)
outside,nearest=distance_transform_edt(~solid,return_indices=True)
inside,free=distance_transform_edt(solid,return_indices=True)
yy,xx=np.indices(solid.shape)
dx=np.where(solid,free[1]-xx,xx-nearest[1])
dy=np.where(solid,free[0]-yy,yy-nearest[0])
gy,gx=np.gradient(gaussian_filter(outside-inside,1.3))
angle=np.mod(np.rint(np.arctan2(gy,gx)/(math.pi/8)).astype(int),16)
field=np.where(outside<=2.6,angle+1,0).astype('uint8')
(root/'assets/WALLS.BIN').write_bytes(field.tobytes())
im=Image.new('RGB',mask.size)
im.putdata([(235,70,70) if n else (15,35,40) for n in field.flat])
im.resize((768,896),Image.Resampling.NEAREST).save(root/'evidence/boundary-field.png')
np.save(root/'evidence/boundary-field.npy',field)
print('wall groups',len(used),'field bytes',field.size,'solid pixels',int(np.count_nonzero(field)))
print('launcher free',[(x,y) for y in [186,188,192,200] for x in range(166,177) if field[y,x]==0])
(root/'evidence/boundaries.json').write_text(json.dumps({'groups':used,'width':192,'height':224,'ball_radius':2.6,'format':'0 free; 1..16 outward normal in 22.5 degree sectors','bank_start':8},indent=2))
