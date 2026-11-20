/* Run with cc -std=c99 -Wall -Wextra cadet/game/test_attract.c -o /tmp/test-attract. */
#include <assert.h>
#include "attract.c"

Game game;

int main(void){
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
 controls(0,468);
 assert(attract_caption==DemoRamps+1);
 game.ramp_entries=2;
 controls(0,469);
 assert(attract_caption==DemoTourComplete);

 game.state=GameOver;
 assert(controls(0,500)==0);
 assert(attract_caption==DemoFinalScore);
 assert(controls(0,679)==0);
 assert(controls(0,680)==DemoReset);

 game.state=Serving;
 game.bumper_hits=game.ramp_entries=0;
 assert(controls(DemoLeft,681)==(DemoReset|DemoLeft));
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
 return 0;
}
