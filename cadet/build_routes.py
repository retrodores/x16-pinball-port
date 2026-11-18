#!/usr/bin/env python3
"""Derive native route fixtures directly from initialized original table geometry."""
from pathlib import Path
import json,math,hashlib,csv
r=Path(__file__).resolve().parents[1];o=r/'cadet/build';source=r/'wireframe/recovered-table.json'
a=json.loads(source.read_text());rows=[];catalog=[]
for index,e in enumerate(a['edges']):
 cls=e['class'].lstrip('0123456789')
 if 'line'not in e or cls not in ('TOneway','TRamp','TWall','TTableLayer'):continue
 ax,ay,bx,by=e['line'];dx=bx-ax;dy=by-ay;length=math.hypot(dx,dy)
 assert length>.001
 # Positive clockwise face: original ray must move toward the left normal.
 nx=-dy/length*.125;ny=dx/length*.125;mx=(ax+bx)/2;my=(ay+by)/2
 sx,sy,tx,ty=mx-nx,my-ny,mx+nx,my+ny
 # Independent original float ray formula, including projected segment limits.
 def original(sx,sy,tx,ty):
  vx,vy=tx-sx,ty-sy;den=-dx*vy+dy*vx
  if den>=0:return False
  t=(dx*(sy-ay)-dy*(sx-ax))/den
  if not 0<=t<=1:return False
  px,py=sx+t*vx,sy+t*vy
  test,lo,hi=(px,min(ax,bx),max(ax,bx))if dx else(py,min(ay,by),max(ay,by))
  return lo<=test<=hi
 assert original(sx,sy,tx,ty)and not original(tx,ty,sx,sy)
 q=lambda x:round(x*256)
 kind=3 if cls=='TRamp'else(2 if e.get('pass')else 1)
 ramp=e.get('ramp',{});action=ramp.get('action',0);target=ramp.get('mask',e['mask'])
 plane=ramp.get('plane',[0,0,0]);force=ramp.get('force',[0,0]);zflag=ramp.get('zflag',0)
 fields=[*map(q,[ax,ay,bx,by]),e['mask'],e['active'],kind,action,target,zflag,round(plane[0]*4096),round(plane[1]*4096),q(plane[2]),q(ramp.get('z',0)),*map(q,force)]
 expkind=0 if not e['active']else(4 if kind==3 and action==0 else kind)
 expmask=target if e['active']and kind==3 and action else e['mask']
 expz=1000
 if e['active']and kind==3:
  if action==1:expz=round((q(mx)/256*plane[0]+q(my)/256*plane[1]+plane[2])*256)+77
  elif action and zflag:expz=77+q(ramp['z'])
 rows.append('{ {'+','.join(map(str,fields))+'}, {'+','.join(map(str,map(q,[sx,sy,tx,ty])))+'}, '+','.join(map(str,[q(mx),q(my),expkind,expmask,expz]))+' }')
 catalog.append({'edge':index,'component':e['component'],'class':cls,'source_mask':e['mask'],'active':e['active'],'role':'ramp_'+str(action)if kind==3 else('pass'if kind==2 else'block'),'target_mask':target,'coordinates':e['line'],'ramp':ramp})
(o/'route-fixtures.h').write_text('typedef struct {cadet_edge edge;int16_t shot[4],mx,my;uint8_t result,mask;int16_t z;} fixture;\nstatic const fixture fixtures[]={\n'+',\n'.join(rows)+'\n};\n#define FIXTURE_COUNT '+str(len(rows))+'\n')
(o/'routes.json').write_text(json.dumps({'source':str(source.relative_to(r)),'sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'edges_total':len(a['edges']),'tested_directed_lines':len(rows),'routes':catalog},indent=2)+'\n')
with(o/'routes.csv').open('w',newline='')as f:
 w=csv.writer(f);w.writerow(['edge','component','class','source_mask','active','role','target_mask','x0','y0','x1','y1'])
 for e in catalog:w.writerow([e[k]for k in ['edge','component','class','source_mask','active','role','target_mask']]+e['coordinates'])
print('original directed-line fixtures',len(rows))
