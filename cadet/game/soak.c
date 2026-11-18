#include "engine.h"
#include <stdio.h>
#include <stdlib.h>
int main(int argc,char**argv){
 if(!game_load()){puts("load failed");return 1;}
 unsigned runs=argc>1?atoi(argv[1]):20;unsigned escapes=0,drains=0,stalls=0,bumps=0,flips=0,ramps=0,guards=0,returns=0;
 uint32_t hash=2166136261u;
 for(unsigned seed=0;seed<runs;++seed){game_start();unsigned stationary=0;int16_t px=0,py=0;unsigned t;
  FILE*f=seed==0?fopen("cadet/play-build/trajectory.csv","w"):NULL;if(f)fprintf(f,"tick,x,y,z,vx,vy,mask,state,left,right,kind,component,events\n");
  for(t=0;t<18000&&game.state!=GameOver;++t){bool l=t%(41+seed%17)<12,rr=t%(61+seed%23)<14;bool pull=game.state==Serving&&game.charge<75+seed%26;
   game_frame(l,rr,pull,false);
   const uint8_t*bytes=(const uint8_t*)&game;
   for(unsigned i=0;i<sizeof game;++i)hash=(hash^bytes[i])*16777619u;
   if(f)fprintf(f,"%u,%d,%d,%d,%d,%d,%u,%u,%u,%u,%u,%u,%u\n",t,game.x,game.y,game.z,game.vx,game.vy,game.mask,game.state,game.phase[0],game.phase[1],game.last_kind,game.last_group,game.events);
   if(game.state==InPlay&&abs(game.x-px)+abs(game.y-py)<2)++stationary;else stationary=0;px=game.x;py=game.y;
   if(stationary>600){++stalls;break;}
  }
  if(f)fclose(f);escapes+=game.escapes;drains+=game.drains;bumps+=game.bumper_hits;flips+=game.flipper_hits;ramps+=game.ramp_entries;guards+=game.guard_hits;returns+=game.returns;
  if(seed<3)printf("run %u frames %u state %u pos %d,%d mask %u drains %u bumps %u flips %u ramps %u escapes %u guards %u\n",seed,t,game.state,game.x,game.y,game.mask,game.drains,game.bumper_hits,game.flipper_hits,game.ramp_entries,game.escapes,game.guard_hits);
 }
 printf("STATE HASH %08x\n",hash);
 printf("SUMMARY runs=%u drains=%u escapes=%u stalls=%u bumpers=%u flippers=%u ramp_entries=%u guards=%u returns=%u\n",runs,drains,escapes,stalls,bumps,flips,ramps,guards,returns);return escapes||stalls;
}
