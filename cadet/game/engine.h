#ifndef CADET_ENGINE_H
#define CADET_ENGINE_H
#include <stdint.h>
#include <stdbool.h>
enum Kind {Wall,Bumper,Plunger,Drain,Ramp,Target,Drop,Sensor,Spinner,Gate,Kickback,Sink,Kickout,Hole,Pass};
enum SoundEvent {SoundCapture=7,SoundRelease,SoundKickback,SoundGateOpen,SoundGateClose,SoundLane,SoundUpgrade,SoundHazard,SoundWormholeAdvance};
enum State {Ready,Serving,InPlay,Captured,Between,GameOver};
typedef struct {int16_t x,y;} Vec;
typedef struct {int16_t x,y,ex,ey,nx,ny,r,xlo,ylo,xhi,yhi;uint8_t group,smooth,kind,mask,elastic,boost,param,flags;int16_t threshold;} Edge;
typedef struct {int16_t x,y,vx,vy,fx,fy,ax,ay,az;uint16_t delay;uint8_t action,mask,zflag;} Meta;
typedef struct {
 int16_t x,y,z,vx,vy,remx,remy,accx,accy,fx,fy;uint16_t tick,wait,ignore,contacts;
 uint8_t mask,phase[2],charge,balls,state,last_sound,flash[160],score[16],digits[40];
 uint16_t disabled[160];uint8_t lamps[160];uint8_t captured,param,flags,multiplier,nudges;bool ramp,overflow,score_dirty;
 uint16_t bumper_hits,flipper_hits,target_hits,returns,drains,guard_hits,escapes;
 uint8_t last_group,last_kind,charge_clock,ball_number,sound_value,visual_epoch;uint16_t last_edge,events,ramp_entries,layer_changes;
} Game;
extern Game game;
bool game_load(void);void game_start(void);void game_frame(bool,bool,bool,bool);void add_score(uint16_t);void sound(uint8_t);
void game_place(int16_t,int16_t,int16_t,int16_t,uint8_t);
#endif


uint8_t game_lamp(uint16_t original_bitmap_group);
uint8_t game_pose(uint16_t original_component_group);
