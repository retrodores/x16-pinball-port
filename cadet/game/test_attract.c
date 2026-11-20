/* Compile with cc -O2 -Icadet/play-build cadet/game/{test_attract,engine}.c. */
#include <assert.h>
#include <stdio.h>
#include "attract.c"

static void transitions(void){
 game.state=Serving;game.ball_number=1;
 assert(controls(0,65000)==0);
 assert(controls(0,363)==0);
 assert(controls(0,364)==DemoReset);
 assert(attract_caption==DemoActive);
 assert(controls(0,365)==0);
 assert(controls(0,377)==DemoLaunch);
 assert(controls(0,558)==0);
 game.state=GameOver;
 assert(controls(0,600)==0);
 assert(attract_caption==DemoFinalScore);
 assert(controls(0,899)==0);
 assert(controls(0,900)==DemoReset);
 assert(controls(DemoLeft,901)==(DemoReset|DemoLeft));
 assert(!attract_caption);
}

static void approaches(void){
 random_state=0x5d;
 game_place(300,2750,0,1100,1);
 assert(flip_input(65530)==0);
 game.y=2950;
 assert(flip_input(65532)==DemoLeft);
 assert(flip_input(3)==DemoLeft);
 assert(flip_input(40)==0);
 assert(flip_input(41)==0); /* Sitting in the region cannot re-arm. */
 game_place(-300,2750,0,800,1);
 assert(flip_input(42)==0);
 game.y=2950;
 assert(flip_input(43)==DemoRight);
 game.state=Captured;
 assert(flip_input(44)==0);
 game_place(900,2750,0,800,1);
 assert(flip_input(45)==0);
 game.y=3100;
 assert(flip_input(46)==0);
}

int main(void){
 transitions();approaches();
 idle_allowed=true;idle_started=false;previous_buttons=0;
 assert(game_load());game_start();
 unsigned completed=0,contacts=0,flips=0,missions=0;
 uint8_t before=0;
 for(unsigned frame=0;frame<180000;++frame){
  uint8_t input=controls(0,(uint16_t)frame);
  if(input&DemoReset){
   if(game.state==GameOver){++completed;assert(!game.escapes);}
   game_start();
  }
  uint16_t hits=game.flipper_hits;
  bool active=game.mission>=Practice;
  game_frame(input&DemoLeft,input&DemoRight,input&DemoLaunch,input&DemoNudge);
  if(game.flipper_hits!=hits)++contacts;
  if(!active&&game.mission>=Practice)++missions;
  if((input&~before)&3)++flips;
  before=input;
 }

 printf("%u demos, %u presses, %u contact frames, %u missions\n",completed,flips,contacts,missions);
 assert(completed>=2&&contacts>0&&flips>0&&missions>0);
 return 0;
}
