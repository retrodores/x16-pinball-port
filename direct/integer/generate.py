#!/usr/bin/env python3
"""Generate a separate fixed-point adaptation; never edit reference methods."""
from pathlib import Path
import re,struct,json,math
r=Path(__file__).resolve().parents[1]
out=r/'build/integer/src';out.mkdir(parents=True,exist_ok=True)
names=['maths.h','world.h','world.cpp','world_params.h','edge_bounds.h','flipper.h','flipper.cpp','flipper_params.h','plunger.h','plunger.cpp','plunger_params.h','original_math.cpp','original_flipper.cpp','original_flipper_control.cpp','original_plunger.cpp','preview.cpp']
def literals(s):
 def quant(m):
  v=m[0]
  if v.startswith(('"',"'",'//','/*')):return v
  return 'Fixed::bits(%d)'%max(-2147483647,min(2147483647,round(float(v.rstrip('fF'))*4096)))
 token=r'"(?:\\.|[^"\\])*"|\'(?:\\.|[^\'\\])*\'|//[^\n]*|/\*[\s\S]*?\*/|(?<![\w.])(?:\d+\.\d*(?:[eE][+-]?\d+)?|\.\d+(?:[eE][+-]?\d+)?|\d+[eE][+-]?\d+)[fF]?'
 return re.sub(token,quant,s)
for n in names:
 s=(r/'src'/n).read_text();s=re.sub(r'\bfloat\b','Fixed',s)
 if n.startswith('original_'):s='// Generated fixed-point adaptation; original source remains under direct/src.\n'+s
 if n=='preview.cpp':
  s=s.replace('return (uint8_t)(e.CurrentAngle/e.AngleMax*7+.5f);', 'if(e.CurrentAngle==0)return 0;if(e.CurrentAngle==e.AngleMax)return 7;return (uint8_t)(e.CurrentAngle/e.AngleMax*7+.5f);')
  s=s.replace('int main(){','#ifdef __CX16__\n__attribute__((minsize))\n#endif\nint main(){').replace('static void project(){','__attribute__((noinline)) static void project(){')
  s=s.replace('static void inject(uint8_t code){', 'static void hexout(uint32_t n){for(int i=7;i>=0;--i)*(volatile uint8_t*)0x9fbb="0123456789abcdef"[(n>>(i*4))&15];}\nstatic void inject(uint8_t code){')
  s=s.replace('unsigned test_frame=0;','uint32_t max_cycles=0,total_cycles=0;unsigned over_budget=0;\n unsigned test_frame=0;')
  s=s.replace('if(test_frame==30)inject', '*(volatile uint8_t*)0x9fb8=0;\n  if(test_frame==30)inject')
  s=s.replace('if(test_frame==29||', 'uint32_t elapsed=*(volatile uint32_t*)0x9fb8;total_cycles+=elapsed;if(elapsed>max_cycles)max_cycles=elapsed;if(elapsed>133333UL)++over_budget;\n  if(test_frame==29||')
  s=s.replace('log("# EXIT\\n");', 'log("# CYCLES ");hexout(max_cycles);log(" ");hexout(total_cycles/760);log(" ");hexout(over_budget);log("\\n");log("# EXIT\\n");')
 if n=='maths.h':
  s=s.replace('#pragma once','#pragma once\n#include "fixed.h"').replace('vector2 RayIntersect;', 'vector2 RayIntersect;\n Fixed PlaneC;')
 if n=='world.h':s=s.replace('sizeof(Edge)==68','sizeof(Edge)==72')
 if n=='world.cpp':
  # Q12 -> Q8.8 is an exact truncating division by 16. Avoid constructing
  # Fixed(256) and passing through the general fixed multiply for each ray.
  s=s.replace('(int16_t)(ray.Origin.X*256)', '(int16_t)(ray.Origin.X.raw/16)').replace('(int16_t)(ray.Origin.Y*256)', '(int16_t)(ray.Origin.Y.raw/16)')
  # Positive ceil(travel/half), in raw units. Preserve the old quotient and
  # remainder semantics without a Q12 division followed by a fixed multiply.
  s=s.replace('steps=(int)(travel/half);if(steps*half<travel)++steps;', 'steps=(int)(travel.raw/half.raw);if((int32_t)steps*half.raw<travel.raw)++steps;')
  # Four direct-mapped records retain adjacent candidates across ray substeps.
  # This only changes data reuse, not candidate order or intersection math.
  s=s.replace('static Edge cache;', 'static Edge cache[4];')
  s=s.replace('static uint16_t cache_id=65535;', 'static uint16_t cache_id[4]={65535,65535,65535,65535};')
  s=s.replace('cache_id=65535;', 'for(uint8_t i=0;i<4;++i)cache_id[i]=65535;')
  s=s.replace('if(cache_id!=id){read_record(44+(id>>6),(id&63)*128,&cache,sizeof edge);cache_id=id;}\n  Edge& candidate=cache;', 'uint8_t slot=id&3;\n  if(cache_id[slot]!=id){read_record(44+(id>>6),(id&63)*128,&cache[slot],sizeof edge);cache_id[slot]=id;}\n  Edge& candidate=cache[slot];')
  s=s.replace('force.X*dt','time_product(force.X,dt)').replace('force.Y*dt','time_product(force.Y,dt)').replace('travel=ball.Speed*dt','travel=time_product(ball.Speed,dt)')
  s=s.replace('direct/build/WORLD.BIN','direct/build/integer/WORLD.BIN')
  s=s.replace('return ok;', 'return ok&&load_integer_geometry();')
  s='extern bool load_integer_geometry();\n'+s
  s=s.replace('static Fixed nearest(ray_type& ray) {','static Fixed nearest(ray_type& ray) {PROFILE_SCOPE(3);')
  s=s.replace('for(uint8_t i=0;i<cell[0];++i) {','''#ifdef __CX16__
 uint8_t saved_bank=*(volatile uint8_t*)0;*(volatile uint8_t*)0=edge_bounds_bank;
#endif
 for(uint8_t i=0;i<cell[0];++i) {''')
  s=s.replace('uint16_t id=cell[i+1];int16_t b[4];read_record(edge_bounds_bank,id*8,b,8);','''uint16_t id=cell[i+1];
#ifdef __CX16__
 const int16_t* b=(const int16_t*)(0xa000+id*8);
#else
 int16_t b[4];read_record(edge_bounds_bank,id*8,b,8);
#endif''')
  s=s.replace('best_flipper=255;\n if(mechanisms)','''#ifdef __CX16__
 *(volatile uint8_t*)0=saved_bank;
#endif
 best_flipper=255;
 if(mechanisms)''')
 if n=='plunger.cpp':s=s.replace('(uint32_t)(delay*1000)','(uint32_t)(delay*1000+Fixed(.5))')
 if n=='original_flipper.cpp':
  s=s.replace('MoveSpeed * timeDelta','time_product(MoveSpeed,timeDelta)')
  a=s.index('void TFlipperEdge::set_control_points(');b=s.index('Fixed TFlipperEdge::flipper_angle_delta',a)
  s=s[:a]+'extern void integer_control_points(TFlipperEdge*,Fixed);\nvoid TFlipperEdge::set_control_points(Fixed angle){integer_control_points(this,angle); }\n'+s[b:]
 if n=='original_math.cpp':
  s=s.replace('Fixed mag = sqrt(vec.X * vec.X + vec.Y * vec.Y);','Fixed mag=fixed_hypot(vec.X,vec.Y);')
 if n=='original_math.cpp':
  s=s.replace('line.MaxCoord = std::max(lineStart, lineEnd);','line.MaxCoord = std::max(lineStart, lineEnd);\n line.PlaneC=maths::DotProduct(line.PerpendicularC,line.Origin);')
  a=s.index('Fixed maths::ray_intersect_line(');b=s.index('void maths::cross(',a)
  s=s[:a]+(r/'integer/line.inc').read_text()+'\n'+s[b:]
 (out/n).write_text(literals(s))
(out/'fixed.h').write_bytes((r/'integer/fixed.h').read_bytes())
(out/'port_types.h').write_text('''#pragma once
#include "fixed.h"
#include "maths.h"
class TBall {public: vector3 Position{},Direction{};Fixed Speed=0;uint16_t CollisionMask=1;bool ActiveFlag=true;};
''')
blob=bytearray((r/'build/WORLD.BIN').read_bytes())
count=json.loads((r/'src/world_manifest.json').read_text())['included_edges']
for i in range(count):
 start=12*8192+i*128+4
 vals=struct.unpack_from('<16f',blob,start)
 values=[max(-2147483647,min(2147483647,round(v*4096))) for v in vals]
 struct.pack_into('<16i',blob,start,*values)
 typ=blob[start-4]
 c=(values[4]*values[8]+values[5]*values[9])//4096 if typ==0 else 0
 struct.pack_into('<i',blob,start+64,c)
(r/'build/integer/WORLD.BIN').write_bytes(blob)
# Quantize rotations of original initialized points offline.
j=json.loads((r/'data/table.json').read_text());packed=bytearray()
def line(a,b):
 x,y=a;ex,ey=b;dx,dy=ex-x,ey-y;length=math.hypot(dx,dy);dx/=length;dy/=length
 lo,hi=sorted((x,ex) if abs(dx)>1e-9 else (y,ey))
 if abs(dx)<1e-9:dx=0
 vals=[dy,-dx,dx,dy,x,y,ex,ey,lo,hi,0,0]
 q=[round(v*4096) for v in vals];q.append((q[0]*q[4]+q[1]*q[5])//4096)
 return q
for f in j['flippers']:
 for index in range(512):
  angle=f['AngleMax']*index/511;sn,cs=math.sin(angle),math.cos(angle);ox,oy=f['RotOrigin']
  def rot(key):
   x,y=f[key];return [(x-ox)*cs-(y-oy)*sn+ox,(x-ox)*sn+(y-oy)*cs+oy]
  vals=line(rot('A1Src'),rot('A2Src'))+line(rot('B1Src'),rot('B2Src'))+[round(v*4096) for v in rot('T1Src')]
  packed.extend(struct.pack('<28i',*vals).ljust(128,b'\0'))
(r/'build/integer/FLIP.BIN').write_bytes(packed)
(out/'geometry.cpp').write_bytes((r/'integer/geometry.cpp').read_bytes())
for n in ('world','mechanisms','flipper'):
 s=(r/'t'/f'{n}_probe.cpp').read_text();s=re.sub(r'\bfloat\b','Fixed',s)
 s=s.replace('union{Fixed f;uint32_t u;}v;v.f=n;hex(v.u);','hex((uint32_t)n.raw);')
 if n=='flipper':s=s.replace('int main(){','extern bool load_integer_geometry();\nint main(){load_integer_geometry();')
 if n=='world':
  s=s.replace('int main(){','''#ifdef PROFILE_INTEGER
uint32_t profile_cycles[4],profile_calls[4],max_cycles[4],max_calls[4];
#endif
int main(){''')
  s=s.replace('reset_cycles();world::frame','''#ifdef PROFILE_INTEGER
 for(int p=0;p<4;++p)profile_cycles[p]=profile_calls[p]=0;
#endif
 reset_cycles();world::frame''')
  s=s.replace('max_frame=i;','''max_frame=i;
#ifdef PROFILE_INTEGER
for(int p=0;p<4;++p){max_cycles[p]=profile_cycles[p];max_calls[p]=profile_calls[p];}
#endif
''')
  s=s.replace('text("ok - original-world launch trace completed','''#ifdef PROFILE_INTEGER
for(int p=0;p<4;++p){text("# PROFILE ");hex(p);out(' ');hex(max_cycles[p]);out(' ');hex(max_calls[p]);out('\\n');}
#endif
text("ok - original-world launch trace completed''')
 (out/f'{n}_probe.cpp').write_text(literals(s))
