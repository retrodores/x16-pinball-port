#include "world.h"
#include <stdio.h>
// Regression for a real UI failure: 60 Hz could let the original 25 ms release
// timer expire between contacts with a ball resting on the plunger.
int main(){
 if(!world::load())return 1;
 for(int hold=200;hold<240;++hold){
  world::start();bool cleared=false;
  for(int frame=0;frame<900;++frame){
   if(frame==170)world::input(false,false,true);
   if(frame==170+hold)world::input(false,false,false);
   world::preview_tick();
   if(world::ball.Position.X>4&&world::ball.Position.Y<-5)cleared=true;
  }
  printf("%s - launch after %d held frames\n",cleared?"ok":"not ok",hold);
  if(!cleared)return 1;
 }
 puts("1..40");return 0;
}
