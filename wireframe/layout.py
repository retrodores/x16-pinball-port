#!/usr/bin/env python3
"""Build an original, sparse wireframe table; preserve the recovered table input."""
from pathlib import Path
import json,math
r=Path(__file__).resolve().parent
old=r/'recovered-table.json'
if not old.exists():old.write_bytes((r/'table.json').read_bytes())
j=json.loads(old.read_text());edges=[]
def line(c,cls,a,b,mask=1,boost=0,elastic=.65,inflate=False,**extra):
 x,y=a;ex,ey=b
 if inflate:
  n=math.hypot(ex-x,ey-y);nx=(ey-y)/n*.3;ny=(x-ex)/n*.3;x+=nx;y+=ny;ex+=nx;ey+=ny
 e=dict(component=c,**{'class':cls},mask=mask,active=1,elasticity=elastic,smoothness=.95,threshold=1,boost=boost,line=[x,y,ex,ey]);e.update(extra);edges.append(e)
def circle(c,cls,x,y,radius,mask=1,boost=0,**extra):
 e=dict(component=c,**{'class':cls},mask=mask,active=1,elasticity=.7,smoothness=.95,threshold=1,boost=boost,circle=[x,y,radius*radius]);e.update(extra);edges.append(e)
def joined(c,points,closed=False,**kw):
 # Intersect adjacent offset lines so every joint shares one identical endpoint.
 segments=[]
 pairs=list(zip(points,points[1:]+points[:1])) if closed else list(zip(points,points[1:]))
 for a,b in pairs:
  x,y=a;ex,ey=b;n=math.hypot(ex-x,ey-y);nx=(ey-y)/n*.3;ny=(x-ex)/n*.3
  segments.append([[x+nx,y+ny],[ex+nx,ey+ny]])
 for k in range(len(segments) if closed else len(segments)-1):
  v=segments[k];w=segments[(k+1)%len(segments)];a,b=v;c0,d=w
  ux,uy=b[0]-a[0],b[1]-a[1];vx,vy=d[0]-c0[0],d[1]-c0[1];cross=ux*vy-uy*vx
  if abs(cross)<1e-9:joint=b
  else:
   t=((c0[0]-a[0])*vy-(c0[1]-a[1])*vx)/cross;joint=[a[0]+t*ux,a[1]+t*uy]
  v[1]=joint;w[0]=joint
 for k,(a,b)in enumerate(segments):
  if c==280 and k==6:line(106,'6TDrain',a,b,**kw)
  else:line(c+k,'5TWall',a,b,**kw)
# A continuous inset perimeter, including the corners. Only the marked bottom
# drain is open to a lost ball; side walls reach below it with no exit gap.
outline=[(8,13.5),(8,-10),(5,-13.5),(-5,-13.5),(-8,-10),(-8,13.5),(-.75,14.5),(.75,14.5)]
joined(280,outline,closed=True,mask=7)
# Shooter lane, open at its top. A thin two-sided rail separates it from play.
line(290,'5TWall',(-6.25,12),(-6.25,-9.1),inflate=True)
line(291,'5TWall',(-6.25,-9.1),(-6.25,12),inflate=True)
circle(292,'5TWall',-6.25,-9.1,.3)
line(102,'8TPlunger',(-7.7,12),(-6.55,12),inflate=True)
# Inlanes and sling faces lead toward the existing two flipper pivots.
line(300,'5TWall',(2.7,11.7),(7.3,9.8),inflate=True)
line(301,'5TWall',(-5.85,9.8),(-2.7,11.7),inflate=True)
slings=[]
for side in (-1,1):
 pts=[(side*3.8,8.8),(side*5.3,6.6),(side*5.3,9.8)]
 if side<0:pts.reverse()
 slings.append(pts)
 joined(310+(side==1)*3,pts,closed=True,boost=7)
# Five independent pop bumpers.
for k,(x,y)in enumerate(((0,-9.2),(3,-6.5),(-2.5,-6.4),(1.2,-3.4),(-1.2,-.5))):circle(380+k,'7TBumper',x,y,.7,boost=9)
# Three three-target banks: physical, individually retracting targets.
for bank,(x,y)in enumerate(((4.3,-10.7),(6.7,-4.5),(6.7,1.8))):
 for k in range(3):
  if bank==0:a=(x-k*.65,y);b=(x-k*.65-.5,y)
  else:a=(x,y+k*.75);b=(x,y+k*.75+.55)
  line(432+bank*3+k,'12TPopupTarget',a,b,boost=2,inflate=True)
# A standing target and a spinner, away from the bumper cluster.
line(458,'11TSoloTarget',(-4.6,2),(-4.6,3),boost=4,inflate=True)
line(520,'12TFlagSpinner',(-2.3,4),(-.7,4))
for k,(x,y)in enumerate(((-4,-11),(1,-11),(4.5,3.5))):line(521+k,'14TLightRollover',(x+.5,y),(x-.5,y))
# Gate opens for ten seconds after a bank is completed.
line(473,'5TGate',(4.9,-1),(6.8,-1),inflate=True)
# A straight raised ramp: entry, top exit, and rollback exit are distinct edges.
ramp_entry=dict(action=1,force=[0,4],plane=[0,-.25,-.9],z=0,mask=2,zflag=0)
ramp_exit=dict(action=2,force=[0,0],plane=[0,0,0],z=0,mask=1,zflag=1)
line(345,'5TRamp',(-3.5,-3.6),(-5.4,-3.6),ramp=ramp_entry)
line(345,'5TRamp',(-3.5,-10),(-5.4,-10),mask=2,ramp=ramp_exit)
line(345,'5TRamp',(-5.4,-3.6),(-3.5,-3.6),mask=2,ramp=ramp_exit)
line(346,'5TWall',(-5.4,-10),(-5.4,-3.6),mask=2,inflate=True)
line(347,'5TWall',(-3.5,-3.6),(-3.5,-10),mask=2,inflate=True)
# A timed side pocket and a bank-unlocked central well.
cap=dict(type=1,position=[5.5,-1.5],direction=[-.5,-.8660254],speed=18,delay=.75)
line(505,'5TSink',(5.4,-.25),(6.7,-.25),capture=cap)
cap=dict(type=2,position=[0,2.5],direction=[0,-1],speed=20,delay=.8,field_radius_sq=1.1**2)
circle(510,'8TKickout',0,2.5,.15,capture=cap)
# The outer return lanes provide two distinct automatic kickbacks.
line(469,'9TKickback',(6.7,12.5),(7.7,12.5),inflate=True)
line(470,'9TKickback',(-5.9,12.5),(-4.9,12.5),inflate=True)
j['outline']=outline;j['slings']=slings;j['edges']=edges;j['layout']='Original CmdrX wireframe practice table, version 0.2';j['plunger']=[-7.02093887,10.0848541]
(r/'table.json').write_text(json.dumps(j,indent=2)+'\n');print('Fresh table:',len(edges),'edges')
