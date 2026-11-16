#include "plunger.h"
#include "world_params.h"
#ifdef __CX16__
static void out(char c){*(volatile char*)0x9fbb=c;}
#else
#include <stdio.h>
static void out(char c){putchar(c);}
#endif
static void text(const char*s){while(*s)out(*s++);}
static unsigned count=0;
static void check(bool ok,const char*s){text(ok?"ok - ":"not ok - ");text(s);out('\n');++count;}
int main(){
 text("# TAP BEGIN\n");TBall b;auto& p=plunger::instance;
 plunger::reset(b);plunger::feed();timer::advance(959);check(!b.ActiveFlag,"feed delay");timer::advance(1);check(b.ActiveFlag,"feed expires at 960 ms");
 check(pb::MainTable->MultiballCount==1,"single feed count");
 plunger::feed();timer::advance(960);check(pb::MainTable->MultiballCount==1,"occupied lane prevents duplicate feed");
 b.ActiveFlag=false;timer::advance(999);check(!b.ActiveFlag,"occupied lane retries after one second");timer::advance(1);check(b.ActiveFlag,"blocked feed retry");
 plunger::reset(b);plunger::input(true);check(p.Boost==1,"pullback starts immediately");timer::advance(24);check(p.Boost==1,"charge waits 25 ms");timer::advance(1);check(p.Boost==2,"charge increment");
 plunger::input(false);check(p.Threshold==0&&!p.PullbackStartedFlag,"release enables boost");
 vector2 contact{serve_x,plunger_y},normal{0,-1};b.Position={serve_x,plunger_y};b.Direction={0,1};b.Speed=0;
 p.Collision(&b,&contact,&normal,0,nullptr);check(b.Speed>2.09f&&b.Speed<2.11f&&b.Direction.Y<-.99f,"partial charge gives original midpoint impulse");
 timer::advance(24);check(p.Boost==2,"release window");timer::advance(1);check(p.Boost==0&&p.Threshold==1e9f,"release expiry");
 plunger::input(true);for(unsigned i=0;i<120;++i)timer::advance(25);check(p.Boost==100,"charge clamps at original maximum");
 plunger::input(false);b.Direction={0,1};b.Speed=0;p.Collision(&b,&contact,&normal,0,nullptr);check(b.Speed>104.99f&&b.Speed<105.01f,"full charge gives original midpoint impulse");
 p.Message(MessageCode::Reset,0);plunger::feed();plunger::input(true);plunger::input(false);b.ActiveFlag=false;
 p.Message(MessageCode::Reset,0);timer::advance(2000);check(!b.ActiveFlag&&p.Boost==0&&p.Threshold==1e9f,"reset cancels feed, pullback and release timers");
 plunger::reset(b);p.Message(MessageCode::PlungerRelaunchBall,1);check(p.SomeCounter==1&&p.Boost==1,"relaunch starts fast pullback");timer::advance(5);check(p.Boost==1,"relaunch delay truncation");timer::advance(1);check(p.Boost==2,"relaunch charges at quarter delay");
 p.Message(MessageCode::SetTiltLock,0);check(p.SomeCounter==0,"tilt clears relaunch counter");
 plunger::reset(b);pb::MainTable->TiltLockFlag=true;b.Direction={0,1};b.Speed=0;p.Collision(&b,&contact,&normal,0,nullptr);check(b.Speed>104.99f&&b.Speed<105.01f,"tilt plunger follows original full-boost path");
 check(!timer::exhausted,"bounded timer pool");
 text("1..");out('0'+count/10);out('0'+count%10);out('\n');
#ifdef __CX16__
 *(volatile char*)0x9fb4=0;asm volatile("jmp $ffff");
#endif
 return 0;
}
