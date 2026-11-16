#include "world.h"
#include "flipper.h"
#include "plunger.h"
#ifdef __CX16__
static void out(char c){*(volatile char*)0x9fbb=c;}
static uint32_t cycles(){return *(volatile uint32_t*)0x9fb8;}
static void reset_cycles(){*(volatile char*)0x9fb8=0;}
#else
#include <stdio.h>
static void out(char c){putchar(c);}
static uint32_t cycles(){return 0;}
static void reset_cycles(){}
#endif
static void text(const char*s){while(*s)out(*s++);}
static void hex(uint32_t n){for(int i=7;i>=0;--i)out("0123456789abcdef"[(n>>(i*4))&15]);}
static void number(float n){union{float f;uint32_t u;}v;v.f=n;hex(v.u);out(' ');}
static unsigned tests=0;
static void check(bool ok,const char* description){text(ok?"ok - ":"not ok - ");text(description);out('\n');++tests;}
static void record(unsigned id){text("# MECHANISMS ");hex(id);out(' ');number(world::ball.Position.X);number(world::ball.Position.Y);number(world::ball.Speed);number(plunger::instance.Boost);number(plunger::instance.Threshold);number(flippers::edges[0].CurrentAngle);number(flippers::edges[1].CurrentAngle);out('\n');}
int main(){
 text("# TAP BEGIN\n");
 check(world::load(),"world loads");world::start();
 for(unsigned i=0;i<57;++i)world::tick();
 check(!world::ball.ActiveFlag,"960 ms feed delay");world::tick();
 check(world::ball.ActiveFlag,"ball feed");
 for(unsigned i=0;i<120;++i)world::tick();
 check(world::ball.Position.Y>plunger_y-.01f&&world::ball.Position.Y<plunger_y+.01f,"plunger settling");record(0);
 world::input(false,false,true);float first=plunger::instance.Boost;
 world::input(false,false,true);check(first==plunger::instance.Boost,"held pullback");
 for(unsigned i=0;i<210;++i)world::tick();
 check(plunger::instance.Boost==100,"full charge");record(1);
 world::input(false,false,false);check(plunger::instance.Threshold==0,"release impulse");
 uint32_t maximum=0;bool cleared=false;
 for(unsigned i=0;i<240;++i){
  reset_cycles();world::tick();uint32_t elapsed=cycles();if(elapsed>maximum)maximum=elapsed;
  if(world::ball.Position.X>4&&world::ball.Position.Y<-5)cleared=true;
  if(!(i&15))record(i+2);
 }
 check(cleared,"launch clears chute");
 check(plunger::instance.Threshold==1e9f&&plunger::instance.Boost==0,"release expiry");
 // Integrated swept contact from an initially stationary ball at both flippers.
 for(unsigned char side=0;side<2;++side){
  world::start();auto& e=flippers::edges[side];auto& b=world::ball;
  b.ActiveFlag=true;b.CollisionMask=1;float t=.6f;
  b.Position={e.LineA.Origin.X+(e.LineA.End.X-e.LineA.Origin.X)*t+e.LineA.PerpendicularC.X*.02f,e.LineA.Origin.Y+(e.LineA.End.Y-e.LineA.Origin.Y)*t+e.LineA.PerpendicularC.Y*.02f};b.Direction={0,0};b.Speed=0;
  world::input(side==0,side==1,false);reset_cycles();world::tick();uint32_t elapsed=cycles();if(elapsed>maximum)maximum=elapsed;
  check(b.Speed>1,"swept flipper strike");record(300+side);
 }
 check(!timer::exhausted,"timer capacity");
 text("# MAX_MECHANISMS_CYCLES ");hex(maximum);out('\n');
 text("1..");out('0'+tests/10);out('0'+tests%10);out('\n');
#ifdef __CX16__
 *(volatile char*)0x9fb4=0;asm volatile("jmp $ffff");
#endif
 return 0;
}
