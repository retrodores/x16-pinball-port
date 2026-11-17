#include "world.cpp"
#include "ramp-fixtures.h"
#ifdef __CX16__
static void out(char c){*(volatile char*)0x9fbb=c;}
#else
#include <stdio.h>
static void out(char c){putchar(c);}
#endif
static void text(const char*s){while(*s)out(*s++);}
static void hex(uint32_t n){for(int i=7;i>=0;--i)out("0123456789abcdef"[(n>>(i*4))&15]);}
static unsigned total=0;
static void check(bool ok,const char*s){++total;text(ok?"ok - ":"not ok - ");text(s);out('\n');}
static const int32_t centers[7][3]={{33,-15237,1731},{-5642,-27107,1731},{5124,-24414,1731},{23632,-44872,1731},{21627,16384,1239},{29245,14336,1239},{26425,20103,1239}};
static const int8_t nx[4]={1,0,-1,0},ny[4]={0,1,0,-1};
int main(){
 text("# TAP BEGIN\n");check(world::load(),"layered collision and flipper assets load");
 for(uint8_t b=0;b<7;++b){
  uint8_t hits=0,rebounds=0;bool primitives=true,masked=true;
  circle_type c{{Fixed::bits(centers[b][0]),Fixed::bits(centers[b][1])},Fixed::bits(centers[b][2])};
  Fixed r=sqrt(c.RadiusSq);
  for(uint8_t side=0;side<4;++side){
   world::start();world::ball.ActiveFlag=true;
   ray_type ray{};ray.Origin={c.Center.X+Fixed(nx[side])*(r+Fixed(.03)),c.Center.Y+Fixed(ny[side])*(r+Fixed(.03))};
   ray.Direction={Fixed(-nx[side]),Fixed(-ny[side])};ray.MinDistance=Fixed(.002);ray.MaxDistance=Fixed(.15);ray.CollisionMask=b<4?1:4;
   Fixed d=maths::ray_intersect_circle(ray,c);primitives=primitives&&d>=0&&d<ray.MaxDistance;
   d=world::nearest(ray);bool hit=d<Fixed::bits(INT32_MAX)&&world::best_flipper==255&&world::best_edge.kind==3+b;
   if(hit){
    ++hits;world::ball.Position={ray.Origin.X,ray.Origin.Y,Fixed(.3)};world::ball.Direction={ray.Direction.X,ray.Direction.Y};world::ball.Speed=8;world::ball.CollisionMask=ray.CollisionMask;
    world::frame(Fixed::bits(34));
    Fixed outward=world::ball.Direction.X*Fixed(nx[side])+world::ball.Direction.Y*Fixed(ny[side]);
    if(outward>0&&world::ball.Speed>8&&world::bumper_flash[b])++rebounds;
    else {text("# MISS ");hex(b);out(' ');hex(side);out(' ');hex(world::contacts);out(' ');hex(world::ball.Speed.raw);out(' ');hex(outward.raw);out(' ');hex(world::bumper_flash[b]);out(' ');hex(world::ball.Position.X.raw);out(' ');hex(world::ball.Position.Y.raw);out('\n');}
   }
   ray.CollisionMask=b<4?4:1;d=world::nearest(ray);
   masked=masked&&(d==Fixed::bits(INT32_MAX)||world::best_flipper!=255||world::best_edge.kind!=3+b);
  }
  text("# BUMPER ");hex(b);out(' ');hex(hits);out(' ');hex(rebounds);out('\n');
  check(primitives,"all cardinal rays intersect bumper circle");check(hits==4&&rebounds==4,"integrated bumper rebounds and flashes");check(masked,"bumper rejects the other playfield layer");
 }
 for(uint8_t side=0;side<2;++side){
  unsigned resting=0,swept=0;
  for(uint8_t k=0;k<6;++k){
   world::start();auto&e=flippers::edges[side];Fixed t=Fixed(.25)+Fixed(k)*Fixed(.1);
   vector2 p{e.LineA.Origin.X+(e.LineA.End.X-e.LineA.Origin.X)*t,e.LineA.Origin.Y+(e.LineA.End.Y-e.LineA.Origin.Y)*t};
   world::ball.ActiveFlag=true;world::ball.CollisionMask=1;world::ball.Position={p.X+e.LineA.PerpendicularC.X*Fixed(.03),p.Y+e.LineA.PerpendicularC.Y*Fixed(.03),Fixed(.3)};
   world::ball.Direction={0,1};world::ball.Speed=8;world::frame(Fixed::bits(34));
   if(flippers::contacts&&world::ball.Direction.Y<0)++resting;
   world::start();auto&f=flippers::edges[side];world::ball.ActiveFlag=true;world::ball.CollisionMask=1;
   world::ball.Position={p.X+f.LineA.PerpendicularC.X*Fixed(.02),p.Y+f.LineA.PerpendicularC.Y*Fixed(.02),Fixed(.3)};
   world::ball.Direction={0,0};world::ball.Speed=0;world::input(side==0,side==1,false);world::frame(Fixed::bits(34));
   if(flippers::contacts&&world::ball.Speed>1&&world::ball.Direction.Y<0)++swept;
  }
  text("# PADDLE ");hex(side);out(' ');hex(resting);out(' ');hex(swept);out('\n');
  check(resting==6,"falling balls rebound from the resting paddle");check(swept==6,"moving paddle strikes stationary balls upward");
 }
 for(const auto& fixture:ramps){
  world::start();line_type line{};maths::line_init(line,Fixed::bits(fixture.line[0]),Fixed::bits(fixture.line[1]),Fixed::bits(fixture.line[2]),Fixed::bits(fixture.line[3]));
  vector2 mid{(line.Origin.X+line.End.X)/2,(line.Origin.Y+line.End.Y)/2};
  world::ball.ActiveFlag=true;world::ball.CollisionMask=fixture.from;
  world::ball.Position={mid.X+line.PerpendicularC.X*Fixed(.01),mid.Y+line.PerpendicularC.Y*Fixed(.01),Fixed(.3)};
  world::ball.Direction={-line.PerpendicularC.X,-line.PerpendicularC.Y};world::ball.Speed=20;
  world::frame(Fixed::bits(34));
  text("# RAMP ");hex(fixture.id);out(' ');hex(world::ball.CollisionMask);out(' ');hex(world::ball.Position.Z.raw);out('\n');
  check(world::ball.CollisionMask==fixture.to&&world::ball.on_ramp==(fixture.action==1),"original ramp entry/exit switches collision layer");
 }
 text("1..33\n");
#ifdef __CX16__
 *(volatile char*)0x9fb4=0;asm volatile("jmp $ffff");
#endif
}
