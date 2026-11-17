#!/usr/bin/env python3
from pathlib import Path
import json,struct,math
r=Path(__file__).resolve().parent;o=r/'build';o.mkdir(exist_ok=True)
j=json.loads((r/'table.json').read_text());src=[e for e in j['edges'] if e['class'] not in ('5TDemo','8TBlocker')]
classes={'5TWall':0,'11TTableLayer':0,'7TBumper':1,'8TPlunger':2,'6TDrain':3,'5TRamp':4,'11TSoloTarget':5,'12TPopupTarget':6,'9TRollover':7,'14TLightRollover':7,'9TTripwire':7,'12TFlagSpinner':8,'5TGate':9,'9TKickback':10,'5TSink':11,'8TKickout':12,'5THole':13,'7TOneway':0}
ids=list(dict.fromkeys(e['component'] for e in src));groups={v:k for k,v in enumerate(ids)}
assert len(ids)<=160
metas=[];meta_lookup={};records=[];bounds=[];occupancy=bytearray(3*24576);grid=[[]for _ in range(3072)]
def q(x):return max(-32767,min(32767,round(x*256)))
def meta(m):
 key=tuple(m)
 if key not in meta_lookup:meta_lookup[key]=len(metas);metas.append(key)
 return meta_lookup[key]
# Vertex circles contribute only the convex exterior arc between their two walls.
# Store those bounding normals in the circle record's otherwise-unused line bounds.
arcs={}
for i,e in enumerate(src):
 if 'circle'not in e or e['class']!='5TWall':continue
 cx,cy,radius_sq=e['circle'];radius=math.sqrt(radius_sq);incoming=[];outgoing=[]
 for line in src:
  if 'line'not in line or line['component']!=e['component']:continue
  x,y,ex,ey=line['line'];length=math.hypot(ex-x,ey-y);nx,ny=(ey-y)/length,(x-ex)/length
  if math.hypot(x-nx*radius-cx,y-ny*radius-cy)<.004:outgoing.append((nx,ny))
  if math.hypot(ex-nx*radius-cx,ey-ny*radius-cy)<.004:incoming.append((nx,ny))
 if len(incoming)==len(outgoing)==1:
  (a,b),(c,d)=incoming[0],outgoing[0]
  if a*d-b*c>0:arcs[i]=[q(a),q(b),q(c),q(d)]
# Approximate only wall corner arcs with <=30-degree facets. Maximum chord
# error at the 0.3-world-unit ball radius is <0.011 world units (<0.13 pixel).
# Bumpers, capture circles and target endcaps retain exact swept circles.
facets=0;expanded=[]
for i,e in enumerate(src):
 if i not in arcs:expanded.append(e);continue
 a,b,c,d=arcs[i];angle=math.atan2(a*d-b*c,a*c+b*d)
 x,y,r2=e['circle'];radius=math.sqrt(r2);start=math.atan2(b,a)
 count=max(1,math.ceil(angle/math.radians(30)))
 for k in range(count):
  u=start+angle*k/count;v=start+angle*(k+1)/count
  f=dict(e);del f['circle'];f['line']=[x+radius*math.cos(u),y+radius*math.sin(u),x+radius*math.cos(v),y+radius*math.sin(v)]
  expanded.append(f);facets+=1
src=expanded;arcs={}
edge_bank=14;bounds_bank=edge_bank+(len(src)+255)//256;occupancy_bank=bounds_bank+(len(src)+511)//512
assert occupancy_bank+9<=56
for i,e in enumerate(src):
 kind=classes[e['class']];flags=0;param=0
 if e.get('pass'):kind=14
 if 'ramp'in e:
  m=e['ramp'];param=meta([0,0,0,0,*map(q,m['force']),q(m['plane'][0]),q(m['plane'][1]),q(m['plane'][2] if m['action']==1 else m['z']),0,m['action'],m['mask'],m['zflag']])
 if 'capture'in e:
  m=e['capture'];d=m['direction'];speed=min(60,m['speed']);param=meta([*map(q,m['position']),q(d[0]*speed),q(d[1]*speed),0,0,0,0,77,max(30,min(360,round(m['delay']*120))),0,1,1])
 if 'hole'in e:
  m=e['hole'];param=meta([0,0,0,0,0,0,0,0,q(m['z']),60,0,m['mask'],1])
 if 'line'in e:
  x,y,ex,ey=e['line'];ln=math.hypot(ex-x,ey-y);nx=(ey-y)/ln;ny=(x-ex)/ln;rad=0
  x,y,ex,ey,nx,ny=map(q,[x,y,ex,ey,nx,ny]);lo,hi=sorted((x,ex));yl,yh=sorted((y,ey));shape=[x,y,ex,ey,nx,ny,0]
 else:
  flags=1;x,y,r2=e['circle'];rad=math.sqrt(r2)
  if kind in (12,13):rad=max(rad,.13)
  x,y,rad=map(q,[x,y,rad]);assert rad<=181;rs=rad*rad
  shape=[x,y,rs&65535,rs>>16,0,0,rad];shape[2]=shape[2] if shape[2]<32768 else shape[2]-65536
  lo,hi,yl,yh=x-rad,x+rad,y-rad,y+rad
  if i in arcs:
   a,b,c,d=arcs[i];points=[(a,b),(c,d)]
   for ux,uy in ((256,0),(-256,0),(0,256),(0,-256)):
    if a*uy-b*ux>=0 and d*ux-c*uy>=0:points.append((ux,uy))
   lo=x+min(ux*rad//256 for ux,uy in points)-4;hi=x+max(ux*rad//256 for ux,uy in points)+4
   yl=y+min(uy*rad//256 for ux,uy in points)-4;yh=y+max(uy*rad//256 for ux,uy in points)+4
 group=groups[e['component']];mask=e['mask'];elastic=round(e['elasticity']*256);boost=round(e['boost']);threshold=q(min(e['threshold'],127))
 if i in arcs:flags|=2
 record=struct.pack('<11hH6Bh',*shape,*arcs.get(i,[lo,yl,hi,yh]),group,kind,mask,min(255,elastic),min(60,boost),param,flags,threshold)
 assert len(record)==32;records.append(record)
 bounds.append(struct.pack('<4h4H',lo-1,yl-1,hi+1,yh+1,mask|(kind<<8),group,0,0))
 # Exact shape/cell intersection removes long diagonal bounding-box false positives.
 def overlaps(a,b,c,d):
  if flags:
   nearx=max(a-x,0,x-c);neary=max(b-y,0,y-d)
   farx=max(abs(a-x),abs(c-x));fary=max(abs(b-y),abs(d-y))
   return nearx*nearx+neary*neary<=rad*rad and farx*farx+fary*fary>=rad*rad
  t0,t1=0.,1.
  for pp,qq in ((x-ex,x-a),(ex-x,c-x),(y-ey,y-b),(ey-y,d-y)):
   if pp==0:
    if qq<0:return False
   elif pp<0:t0=max(t0,qq/pp)
   else:t1=min(t1,qq/pp)
   if t0>t1:return False
  return True
 for gx in range(max(0,(lo-131+3072)//128),min(47,(hi+131+3072)//128)+1):
  for gy in range(max(0,(yl-131+4096)//128),min(63,(yh+131+4096)//128)+1):
   a=gx*128-3072;b=gy*128-4096
   if overlaps(a-131,b-131,a+128+131,b+128+131):grid[gx+gy*48].append(i)
 # A conservative 1/16-unit occupancy map cheaply rejects empty swept regions.
 for gx in range(max(0,(lo-4+3072)//16),min(383,(hi+4+3072)//16)+1):
  for gy in range(max(0,(yl-4+4096)//16),min(511,(yh+4+4096)//16)+1):
   a=gx*16-3072;b=gy*16-4096
   if overlaps(a-4,b-4,a+16+4,b+16+4):
    for layer,m in enumerate((1,2,4)):
     if mask&m:occupancy[layer*24576+gy*48+gx//8]|=1<<(gx&7)
assert max(map(len,grid))<127 and len(src)<4096
# Per-layer cell lists avoid scanning the two invisible collision layers.
index=[];lists=bytearray();shared={}
for mask in (1,2,4):
 for cell_index,candidates in enumerate(grid):
  cell=[i for i in candidates if src[i]['mask']&mask]
  cx=(cell_index%48)*.5-12+.25;cy=(cell_index//48)*.5-16+.25
  def distance(i):
   e=src[i]
   if 'circle'in e:
    x,y,r=e['circle'];return abs(math.hypot(cx-x,cy-y)-math.sqrt(r))
   x,y,ex,ey=e['line'];dx,dy=ex-x,ey-y;t=max(0,min(1,((cx-x)*dx+(cy-y)*dy)/(dx*dx+dy*dy)))
   return math.hypot(cx-x-t*dx,cy-y-t*dy)
  cell.sort(key=distance)
  row=struct.pack('<%dH'%(len(cell)+1),len(cell),*cell)
  if row in shared:index.append(shared[row]);continue
  if len(lists)%8192+len(row)>8192:lists.extend(bytes(8192-len(lists)%8192))
  shared[row]=len(lists);index.append(len(lists));lists.extend(row)
assert len(lists)<=8*8192
blob=bytearray(struct.pack('<%dH'%len(index),*index));blob.extend(bytes(3*8192-len(blob)));blob[-2:]=b'WF';blob.extend(lists)
blob.extend(bytes((14-3)*8192-len(blob)));blob.extend(b''.join(records));blob.extend(bytes((bounds_bank-3)*8192-len(blob)));blob.extend(b''.join(bounds));blob.extend(bytes((occupancy_bank-3)*8192-len(blob)));blob.extend(occupancy);(o/'MODEL.BIN').write_bytes(blob)
lines=['#pragma once','namespace pin {',f'constexpr uint8_t component_count={len(ids)},bounds_bank={bounds_bank},occupancy_bank={occupancy_bank};',f'constexpr uint16_t edge_count={len(src)};',f'constexpr int16_t serve_x={q(j["plunger"][0])},plunger_y={q(11.6749783)};']
lines+=['static const Meta metadata[]={'+','.join('{'+','.join(map(str,m))+'}' for m in metas)+'};']
pivots=[];tips=[];omega=[];length2=[]
for f in j['flippers']:
 ox,oy=f['RotOrigin'];tx,ty=f['T1Src'];pivots.append([q(ox),q(oy)]);pts=[]
 for k in range(13):
  a=f['AngleMax']*k/12;c,s=math.cos(a),math.sin(a);pts.append([q(ox+(tx-ox)*c-(ty-oy)*s),q(oy+(tx-ox)*s+(ty-oy)*c)])
 tips.append(pts);omega.append(q(f['AngleMax']*10));length2.append(round(((tx-ox)**2+(ty-oy)**2)*256*256))
wells=[]
for i,e in enumerate(src):
 if e['class'] not in ('5THole','8TKickout'):continue
 x,y,_=e['circle'];radius=math.sqrt(e.get('hole',e.get('capture',{})).get('radius_sq',e.get('capture',{}).get('field_radius_sq',.1)))
 wells.append([q(x),q(y),q(radius),e['mask'],records[i][28],groups[e['component']],classes[e['class']]])
lines+=['struct Well {int16_t x,y,r;uint8_t mask,param,group,kind;};','static const Well wells[]={'+','.join('{'+','.join(map(str,w))+'}'for w in wells)+'};',f'constexpr uint8_t center_group={groups[510]};','static const uint8_t drop_groups[]={'+','.join(str(groups[i])for i in range(432,441))+'};','static const uint8_t gate_groups[]={'+','.join(str(groups[e['component']])for e in src if e['class']=='5TGate')+'};']
lines+=['static const Vec pivots[2]={'+','.join('{%d,%d}'%tuple(v) for v in pivots)+'};','static const Vec tips[2][13]={'+','.join('{'+','.join('{%d,%d}'%tuple(v) for v in a)+'}' for a in tips)+'};','static const int16_t flipper_omega[2]={%d,%d};'%tuple(omega),f'constexpr int32_t flipper_length2={sum(length2)//2};','}']
(o/'model.h').write_text('\n'.join(lines)+'\n')
manifest={'subpixel_facets':facets,'arc_bounds':len(arcs),'edges':len(src),'components':len(ids),'component_ids':ids,'max_candidates':max(map(len,grid)),'bytes':len(blob),'banks':f'3..{occupancy_bank+8}','metadata':len(metas),'classes':{c:sum(e['class']==c for e in src) for c in classes}}
(o/'model.json').write_text(json.dumps(manifest,indent=2)+'\n');print(json.dumps(manifest)[:600])
