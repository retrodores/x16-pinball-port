/* From the repo root:
 * cc -O2 -Wall -Wextra -Icadet/play-build cadet/game/test_attract.c \
 *    cadet/game/engine.c -o /tmp/test-attract && /tmp/test-attract
 */
#include <assert.h>
#include <stdio.h>
#include "attract.c"

static void transitions(void){
 game.state=Serving;
 game.ball_number=1;

 /* The idle interval crosses the 16-bit video clock wrap. */
 assert(controls(0,65000)==0);
 assert(controls(0,363)==0);
 assert(controls(0,364)==DemoReset);
 assert(attract_caption==DemoBumpers+3);
 assert(controls(0,365)==0);
 assert(controls(0,413)==DemoLaunch);
 assert(controls(0,466)==0);

 game.state=InPlay;
 game.bumper_hits=3;
 controls(0,467);
 assert(attract_caption==DemoBumpers);
 game.bumper_hits=4;
 game.ramp_entries=5;
 controls(0,468);
 assert(attract_caption==DemoRamps+1);
 game.ramp_entries=7;
 controls(0,469);
 assert(attract_caption==DemoTourComplete);

 /* A ball can return to the shooter lane without changing the ball number. */
 game.state=Serving;
 assert(controls(0,480)==0);
 assert(controls(0,528)==DemoLaunch);
 assert(controls(0,590)==0);

 game.state=GameOver;
 assert(controls(0,600)==0);
 assert(attract_caption==DemoFinalScore);
 assert(controls(0,779)==0);
 assert(controls(0,780)==DemoReset);

 game.state=Serving;
 game.bumper_hits=game.ramp_entries=0;
 assert(controls(DemoLeft,781)==(DemoReset|DemoLeft));
 assert(!attract_caption);
 assert(controls(0,2500)==0);

 /* A midway serve cannot be taken over by the computer. */
 game.ball_number=2;
 assert(controls(DemoToggle,2501)==0);
 assert(controls(0,2502)==0);
 game.ball_number=1;
 assert(controls(DemoToggle,2503)==DemoReset);
 assert(controls(DemoNew,2504)==DemoReset);
 assert(!attract_caption);
}

int main(void){
 transitions();
 idle_allowed=true;
 idle_started=false;
 previous_buttons=0;
 assert(game_load());
 game_start();
 unsigned completed=0,tours=0;
 for(unsigned frame=0;frame<90000;++frame){
  bool finished_tour=goal==2;
  uint8_t input=controls(0,(uint16_t)frame);
  if(input&DemoReset){
   if(game.state==GameOver){
    ++completed;
    if(finished_tour)++tours;
    assert(!game.escapes);
   }
   game_start();
  }
  game_frame(input&DemoLeft,input&DemoRight,input&DemoLaunch,input&DemoNudge);
 }
 assert(completed>=2&&tours>=2);
 printf("%u complete demos, %u complete objective tours\n",completed,tours);
 return 0;
}
