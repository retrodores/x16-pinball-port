#pragma once
#include <stdint.h>
namespace pin {
enum Kind:uint8_t {Wall,Bumper,Plunger,Drain,Ramp,Target,Drop,Sensor,Spinner,Gate,Kickback,Sink,Kickout,Hole,Pass};
enum State:uint8_t {Ready,Serving,InPlay,Captured,Between,GameOver};
struct Vec {int16_t x,y;};
struct Edge {int16_t x,y,ex,ey,nx,ny,r,xlo,ylo,xhi,yhi;uint16_t group;uint8_t kind,mask,elastic,boost,param,flags;int16_t threshold;};
static_assert(sizeof(Edge)==32,"edge record");
struct Meta {int16_t x,y,vx,vy,fx,fy,ax,ay,az;uint16_t delay;uint8_t action,mask,zflag;};
struct Game {
 int16_t x,y,z,vx,vy,remx,remy,accx,accy,fx,fy;uint16_t tick,wait,ignore,contacts;
 uint8_t mask,phase[2],charge,balls,state,last_sound,flash[160],score[16],digits[40];
 uint16_t disabled[160];uint8_t lamps[160];uint8_t captured,param,flags,multiplier,nudges;bool ramp,overflow,score_dirty;
 uint16_t bumper_hits,flipper_hits,target_hits,returns,drains,guard_hits,escapes;
};
extern Game game;
bool load();void start();void frame(bool left,bool right,bool pull,bool nudge=false);void add_score(uint16_t n);void sound(uint8_t id);
#ifdef PIN_TEST
void place(int16_t x,int16_t y,int16_t vx,int16_t vy,uint8_t mask=1);
#endif
}
