#include "flipper.h"
#ifdef __CX16__
static void out(char c){*(volatile char*)0x9fbb=c;}
#else
#include <stdio.h>
static void out(char c){putchar(c);}
#endif
static void text(const char*s){while(*s)out(*s++);}
static void hex(uint32_t n){for(int i=7;i>=0;--i)out("0123456789abcdef"[(n>>(i*4))&15]);}
static void number(float n){union{float f;uint32_t u;}v;v.f=n;hex(v.u);out(' ');}
static void record(unsigned id,TBall& b,TFlipperEdge& e){text("# FLIPPER ");hex(id);out(' ');number(e.CurrentAngle);number(e.AngleRemainder);number(e.T1.X);number(e.T1.Y);number(b.Position.X);number(b.Position.Y);number(b.Direction.X);number(b.Direction.Y);number(b.Speed);out('\n');}
int main(){
 text("# TAP BEGIN\n");
 unsigned id=0;unsigned contacts=0;bool endpoints=true;
 for(unsigned char side=0;side<2;++side){
  flippers::reset();auto& e=flippers::edges[side];
  // Complete extension/retraction without a ball contact, then reverse mid-motion.
  TBall b;b.Position={30,30};
  for(unsigned mode=0;mode<4;++mode){
   flippers::set(side,!(mode&1));
   unsigned count=mode<2?12:2;
   for(unsigned frame=0;frame<count;++frame){float delta=0;int n=flippers::steps(side,1.0f/60,delta);for(int k=0;k<n;++k)flippers::advance(side,delta,b);if(e.ControlPointDirtyFlag)e.set_control_points(e.CurrentAngle);record(id++,b,e);}
   if(mode==0)endpoints=endpoints && e.CurrentAngle==e.AngleMax;
   if(mode==1)endpoints=endpoints && e.CurrentAngle==0;
  }
  // Original ray contact and rebound at rest, extending, held and retracting.
  for(unsigned mode=0;mode<4;++mode){
   flippers::reset();
   if(mode){e.CurrentAngle=e.AngleMax*.5f;e.set_control_points(e.CurrentAngle);}
   if(mode==1)flippers::set(side,true);if(mode==3)flippers::set(side,false);
   for(unsigned k=1;k<=3;++k){
    float t=k*.25f;vector2 p{e.LineA.Origin.X+(e.LineA.End.X-e.LineA.Origin.X)*t,e.LineA.Origin.Y+(e.LineA.End.Y-e.LineA.Origin.Y)*t};
    ray_type ray{};ray.Origin={p.X+e.LineA.PerpendicularC.X*.3f,p.Y+e.LineA.PerpendicularC.Y*.3f};ray.Direction={-e.LineA.PerpendicularC.X,-e.LineA.PerpendicularC.Y};ray.MaxDistance=1;ray.MinDistance=.002f;
    float d=e.FindCollisionDistance(ray);b.Position={ray.Origin.X,ray.Origin.Y};b.Direction={ray.Direction.X,ray.Direction.Y};b.Speed=4;
    if(d<1e9f){e.EdgeCollision(&b,d);++contacts;}
    record(id++,b,e);
   }
  }
  // Swept flipper can strike an otherwise motionless ball.
  for(unsigned sample=0;sample<8;++sample){
   flippers::reset();flippers::set(side,true);
   float t=.3f+sample*.07f;
   b.Position={e.LineA.Origin.X+(e.LineA.End.X-e.LineA.Origin.X)*t+e.LineA.PerpendicularC.X*.02f,e.LineA.Origin.Y+(e.LineA.End.Y-e.LineA.Origin.Y)*t+e.LineA.PerpendicularC.Y*.02f};b.Direction={0,0};b.Speed=0;
   float delta=0;int n=flippers::steps(side,1.0f/60,delta);for(int k=0;k<n;++k)flippers::advance(side,delta,b);
   if(b.Speed>0)++contacts;
   record(id++,b,e);
  }
 }
 text(endpoints?"ok - both flippers reach original travel endpoints\n":"not ok - flipper travel endpoints\n");
 text("# CONTACTS ");hex(contacts);out('\n');
 text(contacts>=24?"ok - original flipper contact scenarios\n":"not ok - flipper contacts missing\n");
 text("1..2\n");
#ifdef __CX16__
 *(volatile char*)0x9fb4=0;asm volatile("jmp $ffff");
#endif
 return 0;
}
