#include "plunger.h"
#include "plunger_params.h"
#include "world_params.h"
namespace pb {bool FullTiltMode=false;void tilt_no_more(){MainTable->TiltLockFlag=false;}}
int NativeTable::BallCountInRect(const vector2& pos,float margin){
 TBall* b=BallList[0];return b&&b->ActiveFlag&&b->Position.X>=pos.X-margin&&b->Position.X<=pos.X+margin&&b->Position.Y>=pos.Y-margin&&b->Position.Y<=pos.Y+margin;
}
TBall* NativeTable::AddBall(vector2 pos){
 TBall* b=BallList[0];if(!b||b->ActiveFlag)return nullptr;
 *b=TBall{};b->Position={pos.X,pos.Y,ball_radius};return b;
}
// Fixed-size ownership replaces heap-linked timers. Preserve millisecond expiry,
// insertion ordering and original check()'s two-callback plus overdue policy.
namespace timer {
struct Entry {uint32_t target,order;void* caller;Callback callback;uint16_t id;};
static Entry entries[8];static uint16_t serial=1;static uint32_t sequence=0;
uint32_t now=0;bool exhausted=false;
void reset(){for(auto& e:entries)e.id=0;serial=1;sequence=0;now=0;exhausted=false;}
int set(float delay,void* caller,Callback cb){
 for(auto& e:entries)if(!e.id){
  e.target=now+(uint32_t)(delay*1000);e.order=sequence++;e.caller=caller;e.callback=cb;e.id=serial++;
  if(serial>32767)serial=1;return e.id;
 }
 exhausted=true;return 0;
}
int kill(int id){for(auto& e:entries)if(e.id==id&&id){e.id=0;return id;}return 0;}
int kill(Callback cb){int n=0;for(auto& e:entries)if(e.id&&e.callback==cb){e.id=0;++n;}return n;}
void advance(uint16_t ms){
 now+=ms;unsigned calls=0;
 for(unsigned guard=0;guard<16;++guard){
  Entry* first=nullptr;
  for(auto& e:entries)if(e.id&&(!first||e.target<first->target||(e.target==first->target&&e.order<first->order)))first=&e;
  if(!first||first->target>now||(calls>=2&&now-first->target<100))break;
  auto cb=first->callback;auto caller=first->caller;auto id=first->id;first->id=0;++calls;if(cb)cb(id,caller);
 }
}
}
namespace loader {void play_sound(int,void*,const char*){++plunger::sound_events;}}
namespace control {void handler(MessageCode,void*){++plunger::control_events;}}
// Deliberate deterministic test adapter; presentation/game RNG is not connected yet.
float RandFloat(){return .5f;}
namespace plunger {
TPlunger instance;
unsigned sound_events=0,control_events=0;
static uint8_t phase=0;
void reset(TBall& b){
 timer::reset();phase=0;sound_events=control_events=0;
 b=TBall{};b.ActiveFlag=false;b.CollisionMask=0;pb::MainTable->BallList[0]=&b;
 pb::MainTable->PlungerPosition={serve_x,serve_y};pb::MainTable->CollisionCompOffset=ball_radius;
 pb::MainTable->MultiballCount=0;pb::MainTable->BallInDrainFlag=1;pb::MainTable->TiltLockFlag=false;
 instance=TPlunger{};instance.ListBitmap=&instance.bitmaps;instance.PinballTable=pb::MainTable;initialize_plunger(instance);
}
void input(bool pressed){instance.Message(pressed?MessageCode::PlungerInputPressed:MessageCode::PlungerInputReleased,0);}
void feed(){instance.Message(MessageCode::PlungerStartFeedTimer,0);}
void advance_half_frame(){phase+=1;uint16_t ms=8;if(phase>=3){++ms;phase-=3;}timer::advance(ms);}
void advance_frame(){phase+=2;uint16_t ms=16;if(phase>=3){++ms;phase-=3;}timer::advance(ms);}
}
