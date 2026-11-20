#include "attract.h"

/* Bank 62 contains the controller; only its trampoline is always resident. */
#define PHYSICS __attribute__((section(".physics"),noinline))
#define IDLE_TICKS 900u
static uint16_t idle_since, ball_since, ramp_start;
static uint8_t previous_buttons, goal;
static bool idle_allowed=true, idle_started, was_serving;
uint8_t attract_caption;

static PHYSICS uint8_t controls(uint8_t buttons, uint16_t now){
 uint8_t pressed=buttons & ~previous_buttons;
 previous_buttons=buttons;
 bool terminal=game.state==GameOver;
 if(pressed&DemoNew || (attract_caption&&(buttons&15 || pressed&DemoToggle))){
  attract_caption=0;
  idle_allowed=false;
  idle_started=false;
  return (buttons&15)|DemoReset;
 }
 if(!attract_caption){
  if(buttons&15){
   idle_allowed=false;
   idle_started=false;
   return buttons&15;
  }
  if((terminal||idle_allowed)&&!idle_started){
   idle_started=true;
   idle_since=now;
  }
  bool at_start=game.state==Serving&&game.ball_number==1&&!game.events;
  if(((terminal||at_start)&&(pressed&DemoToggle)) ||
     ((terminal||idle_allowed)&&(uint16_t)(now-idle_since)>=IDLE_TICKS)){
   attract_caption=DemoBumpers+3;
   was_serving=false;
   goal=0;
   return DemoReset;
  }
  return 0;
 }
 if(terminal){
  if(attract_caption!=DemoFinalScore){
   attract_caption=DemoFinalScore;
   ball_since=now;
  }
  if((uint16_t)(now-ball_since)<180u)return 0;
  attract_caption=DemoBumpers+3;
  was_serving=false;
  goal=0;
  return DemoReset;
 }
 if(!goal&&game.bumper_hits>=4){
  goal=1;
  ramp_start=game.ramp_entries;
 }
 if(!goal)attract_caption=DemoBumpers+3-game.bumper_hits;
 else if(goal==1){
  uint16_t ramps=game.ramp_entries-ramp_start;
  if(ramps>=2)goal=2;
  else attract_caption=DemoRamps+1-ramps;
 }
 if(goal==2)attract_caption=DemoTourComplete;
 bool serving=game.state==Serving;
 if(serving&&!was_serving)ball_since=now;
 was_serving=serving;
 if(serving){
  uint16_t age=now-ball_since;
  return age>=48&&age<90+(uint8_t)(game.ball_number*11)?DemoLaunch:0;
 }
 /* React to descending balls near the flippers. Short, staggered pulses
    elsewhere keep lanes moving without relocating the ball or adding points. */
 uint8_t pulse=(uint8_t)now;
 if(game.vy>0&&game.y>1570&&game.y<2800)
  return game.x<0?DemoRight:DemoLeft;
 return ((pulse&31)<7?DemoLeft:0) | (((pulse+12)&31)<7?DemoRight:0);
}

__attribute__((noinline)) uint8_t attract_input(uint8_t buttons, uint16_t now){
 volatile uint8_t *const bank=(volatile uint8_t*)0;
 uint8_t saved=*bank;
 *bank=62;
 __asm__ volatile("":::"memory");
 uint8_t result=controls(buttons,now);
 __asm__ volatile("":::"memory");
 *bank=saved;
 return result;
}
