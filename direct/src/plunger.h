#pragma once
#include "flipper.h"
class TEdgeSegment;
struct BitmapCount {unsigned count=8;unsigned size() const{return count;}};
class TPlunger {
public:
 NativeTable* PinballTable=nullptr;
 BitmapCount bitmaps;
 BitmapCount* ListBitmap=&bitmaps;
 float Boost=0,Threshold=1e9f,Elasticity=.5f,Smoothness=.5f;
 int HardHitSoundId=0,SoundIndexP1=0,SoundIndexP2=0;
 int PullbackTimer_=0,BallFeedTimer_=0;
 float MaxPullback=100,PullbackIncrement=1,PullbackDelay=.025f;
 bool PullbackStartedFlag=false;
 int SomeCounter=0;
 unsigned sprite=0;
 void SpriteSet(int index){sprite=index;}
 void Collision(TBall* ball,vector2* nextPosition,vector2* direction,float distance,TEdgeSegment* edge);
 #ifdef __CX16__
 __attribute__((always_inline))
 #endif
 int Message(MessageCode code,float value);
 static void BallFeedTimer(int timerId,void* caller);
 static void PullbackTimer(int timerId,void* caller);
 static void ReleasedTimer(int timerId,void* caller);
};
namespace timer {
using Callback=void(*)(int,void*);
int set(float delay,void* caller,Callback callback);
int kill(int id);
int kill(Callback callback);
void reset();
void advance(uint16_t milliseconds);
extern uint32_t now;
extern bool exhausted;
}
namespace loader {void play_sound(int,void*,const char*);}
namespace control {void handler(MessageCode,void*);}
float RandFloat();
#define assertm(condition,message) do {if(!(condition))return 0;} while(0)
namespace plunger {
extern TPlunger instance;
extern unsigned sound_events,control_events;
void reset(TBall& ball);
void input(bool pressed);
void feed();
void advance_frame();
}
