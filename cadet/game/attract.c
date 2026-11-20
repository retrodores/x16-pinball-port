#include "attract.h"

/* Bank 62 contains the controller; only its trampoline is always resident. */
#define PHYSICS __attribute__((section(".physics"),noinline))
#define IDLE_TICKS 900u
static uint16_t idle_since, ball_since, ramp_start;
static uint8_t previous_buttons, goal;
static bool idle_allowed=true, idle_started, was_serving;
uint8_t attract_caption;

/* The reference has separate inner and outer approach triggers on each
 * side. Use their Q8 bounds, with the ball's heading to select the paddle. */
static uint16_t armed_at[2], release_at[2];
static uint8_t armed, held;

static PHYSICS uint8_t flip_input(uint16_t now){
 if(game.state!=InPlay||game.mask!=1||game.ramp){
  held=armed=0;return 0;
 }
 int16_t x=game.x;
 uint8_t side=x<0;
 if(side)x=-x;
 bool approaching=game.vy>0&&game.y>=2750&&game.y<3260;
 uint8_t bit=1u<<side;
 for(uint8_t i=0;i<2;++i){
  if((held&(1u<<i))&&(int16_t)(now-release_at[i])>=0)held&=~(1u<<i);
 }
 if(!approaching){armed=0;return held;}
 armed&=bit;
 if(held&bit)return held;
 if(x>=490&&x<=670&&game.y<=2990&&!armed){
  armed=bit;armed_at[side]=now+6+(uint8_t)now%13;
 }
 bool inner=x>=32&&x<=540&&game.y>=2890;
 if(inner||(armed&&(int16_t)(now-armed_at[side])>=0&&x<=690)){
  armed=0;held|=bit;release_at[side]=now+12+(uint8_t)now%25;
 }
 return held;
}

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
   was_serving=false;held=armed=0;
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
  was_serving=false;held=armed=0;
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
  held=armed=0;
  uint16_t age=now-ball_since;
  return age>=48&&age<90+(uint8_t)(game.ball_number*11)?DemoLaunch:0;
 }
 return flip_input(now);
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
