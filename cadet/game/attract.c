#include "attract.h"

/* Bank 62 contains the controller; only its trampoline is always resident. */
#define PHYSICS __attribute__((section(".physics"),noinline))
#define IDLE_TICKS 900u
static uint16_t idle_since, ball_since;
static uint8_t previous_buttons;
static bool idle_allowed=true, idle_started, was_serving;
uint8_t attract_caption;

/* TDemo's recovered trigger edges in 1/32 table units, in the original order.
 * The short, quantized approach edges keep the intersection test small.
 * The first edge on each side arms a delayed flip. The other three fire it. */
static const int16_t edge[2][4][4] __attribute__((section(".physics.rodata")))={
 {{65,345,83,370},{21,409,8,375},{8,375,65,344},{65,344,21,409}},
 {{-84,372,-67,346},{-66,347,-5,374},{-5,374,-20,410},{-20,410,-66,347}}
};
static uint16_t armed_at[2], release_at[2];
static uint8_t armed, held, random_state, launch_ticks;
static bool tracking;
static Vec previous_ball;

static PHYSICS uint8_t next_delay(uint8_t base,uint8_t spread){
 random_state=(random_state>>1)^((random_state&1)?0xb8:0);
 return base+random_state%spread;
}

static PHYSICS bool crosses(const int16_t *line,Vec from,Vec to){
 int16_t x=line[0],y=line[1],ex=line[2],ey=line[3];
 if((from.x<x&&to.x<x&&from.x<ex&&to.x<ex)||
    (from.x>x&&to.x>x&&from.x>ex&&to.x>ex)||
    (from.y<y&&to.y<y&&from.y<ey&&to.y<ey)||
    (from.y>y&&to.y>y&&from.y>ey&&to.y>ey))return false;
 int16_t dx=ex-x,dy=ey-y;
 int16_t a=dx*(from.y-y)-dy*(from.x-x);
 int16_t b=dx*(to.y-y)-dy*(to.x-x);
 if((a<0&&b<0)||(a>0&&b>0)||!a)return false;
 dx=to.x-from.x;dy=to.y-from.y;
 a=dx*(y-from.y)-dy*(x-from.x);
 b=dx*(ey-from.y)-dy*(ex-from.x);
 return (a<=0&&b>=0)||(a>=0&&b<=0);
}

static PHYSICS uint8_t flip_input(uint16_t now){
 if(game.state!=InPlay||game.mask!=1||game.ramp){
  held=armed=0;tracking=false;return 0;
 }
 Vec pos={game.x>>3,game.y>>3};
 bool approaching=tracking&&game.vy>0&&pos.y>=345&&previous_ball.y<=410&&pos.y>previous_ball.y;
 for(uint8_t side=0;side<2;++side){
  uint8_t bit=1u<<side;
  if(held&bit){
   if((int16_t)(now-release_at[side])>=0)held&=~bit;
   continue; /* The release must reach the engine before a new press. */
  }
  bool immediate=false;
  if(approaching){
   const int16_t (*lines)[4]=edge[side];
   if(!(armed&bit)&&crosses(lines[0],previous_ball,pos)){
    armed|=bit;armed_at[side]=now+next_delay(6,13);
   }
   immediate=crosses(lines[1],previous_ball,pos)||crosses(lines[2],previous_ball,pos)||
       crosses(lines[3],previous_ball,pos);
  }
  if(immediate||((armed&bit)&&(int16_t)(now-armed_at[side])>=0)){
   armed&=~bit;held|=bit;release_at[side]=now+next_delay(12,25);
  }
 }
 tracking=true;previous_ball=pos;
 return held;
}

static PHYSICS uint8_t controls(uint8_t buttons, uint16_t now){
 uint8_t pressed=buttons & ~previous_buttons;
 previous_buttons=buttons;
 bool terminal=game.state==GameOver;
 if(buttons&DemoNew || (attract_caption&&(buttons&15 || pressed&DemoToggle))){
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
  bool at_start=game.state==Ready||(game.state==Serving&&game.ball_number==1&&!game.events);
  if(((terminal||at_start)&&(pressed&DemoToggle)) ||
     ((terminal||idle_allowed)&&(uint16_t)(now-idle_since)>=IDLE_TICKS)){
   attract_caption=DemoActive;
   was_serving=tracking=false;held=armed=0;
   random_state=0x5d;
   return DemoReset;
  }
  return 0;
 }
 if(terminal){
  if(attract_caption!=DemoFinalScore){
   attract_caption=DemoFinalScore;
   ball_since=now;
  }
  if((uint16_t)(now-ball_since)<300u)return 0;
  attract_caption=DemoActive;
  was_serving=tracking=false;held=armed=0;
  return DemoReset;
 }
 bool serving=game.state==Serving;
 if(serving&&!was_serving){ball_since=now;launch_ticks=next_delay(120,61);}
 was_serving=serving;
 if(serving){
  held=armed=0;tracking=false;
  uint16_t age=now-ball_since;
  return age>=12&&age<12u+launch_ticks?DemoLaunch:0;
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
