/* Source contracts for OBS feedback: lower rebounders and mechanical inputs.
 * TWall.cpp, TCollisionComponent.cpp, control.cpp FlipperRebounderControl1/2,
 * TPlunger.cpp, and TFlipper::Message (not ball-contact sounds).
 */
#include "engine.c"
#include <stdio.h>
static unsigned failures,checks;
#define CHECK(x) do{++checks;if(!(x)){++failures;printf("# FAIL %u\n",(unsigned)__LINE__);}}while(0)
static uint32_t score(void){return game.score[0]|((uint32_t)game.score[1]<<8)|((uint32_t)game.score[2]<<16);}
static Edge wall(uint16_t original){
 Edge chosen={0};uint16_t longest=0;
 for(uint16_t i=0;i<edge_count;++i){Edge e=*edge(i);if(original_groups[e.group]!=original||(e.flags&1))continue;
  uint16_t length=ax(e.ex-e.x)+ax(e.ey-e.y);if(length>longest){longest=length;chosen=e;}
 }
 CHECK(longest!=0);return chosen;
}
static void contact(Edge*e,int16_t speed){
 game_place((e->x+e->ex)/2+e->nx/32,(e->y+e->ey)/2+e->ny/32,-mul(e->nx,speed)/256,-mul(e->ny,speed)/256,1);
 game.last_sound=255;move_time(-e->nx/16,-e->ny/16,1,0);
 CHECK(game.last_group==e->group);
}
static void slingshots(void){
 for(uint8_t side=0;side<4;++side){
  game_start();Edge e=wall(469+side);CHECK(e.threshold==256&&e.boost==18);
  contact(&e,128);CHECK(score()==0&&game_pose(469+side)==0);CHECK(game.last_sound==6);
  contact(&e,1024);CHECK(score()==500&&game_pose(469+side)==1);CHECK(game.last_sound==2);if(side<2)CHECK(game_lamp(180+side)==1);
  uint8_t epoch=game.visual_epoch;for(uint8_t f=0;f<5;++f)rules_tick();CHECK(game_pose(469+side)==1);
  rules_tick();CHECK(game_pose(469+side)==0&&game.visual_epoch!=epoch);if(side<2)CHECK(game_lamp(180+side)==0);
  contact(&e,1024);for(uint8_t f=0;f<3;++f)rules_tick();contact(&e,1024);
  CHECK(score()==1500&&rules.rebounder_fire[side]==12);
 }
}
static void input_events(void){
 game_start();CHECK(game.last_sound==SoundFeed&&original_groups[game.last_group]==473&&game.last_kind==Plunger);
 game.last_sound=255;game_frame(0,0,1,0);CHECK(game.charge==1&&game.last_sound==4&&original_groups[game.last_group]==473);
 game.last_sound=255;game_frame(0,0,1,0);CHECK(game.charge==1&&game.last_sound==255);
 game_frame(0,0,1,0);CHECK(game.charge==3&&game.last_sound==255);
 game_frame(0,0,1,0);CHECK(game.charge==5);
 for(uint8_t i=0;i<73;++i)game_frame(0,0,1,0);CHECK(game.charge==100&&game.last_sound==255);
 game_frame(0,0,0,0);CHECK(game.state==InPlay&&game.last_sound==3&&original_groups[game.last_group]==473);
 /* Source extend/retract cues follow input transitions, including reversal
    before an endpoint and while the ball is held by a wormhole. */
 game.state=Captured;game.wait=240;
 game.last_sound=255;game_frame(1,0,0,0);CHECK(game.last_sound==0&&game.phase[0]==50);
 game.last_sound=255;game_frame(0,0,0,0);CHECK(game.last_sound==1&&game.phase[0]==25);
 game.last_sound=255;game_frame(1,0,0,0);CHECK(game.last_sound==0&&game.phase[0]==75);
 game.last_sound=255;game_frame(1,0,0,0);CHECK(game.last_sound==255&&game.phase[0]==120);
 game.last_sound=255;game_frame(0,0,0,0);CHECK(game.last_sound==1&&game.phase[0]==95);
 game.last_sound=255;game_frame(0,0,0,0);CHECK(game.last_sound==255);
 /* Plunger input/visual latch is independent of ball position in 3DPB. */
 game_start();game_place(0,0,0,0,1);game.last_sound=255;game_frame(0,0,1,0);
 CHECK(game.state==InPlay&&(game.flags&1)&&game.charge==1&&game.last_sound==4);
 game_frame(0,0,0,0);CHECK(game.state==InPlay&&!(game.flags&1)&&game.last_sound==3&&game.vy>=0);
 game.state=Captured;game.wait=240;game_frame(0,0,1,0);
 CHECK(game.state==Captured&&(game.flags&1)&&game.charge==1&&game.last_sound==4);
 for(uint8_t i=0;i<30;++i)game_frame(0,0,1,0);CHECK(game.charge==41&&game.state==Captured);
 game_frame(0,0,0,0);CHECK(game.state==Captured&&!(game.flags&1)&&game.last_sound==3);
 /* A ball returning while the user is still pulling retains the held charge. */
 game.state=InPlay;game_frame(0,0,1,0);game.charge=40;game.charge_clock=1;
 Edge plunger=wall(473);event(&plunger);CHECK(game.state==Serving&&(game.flags&1)&&game.charge==40&&game.charge_clock==1);
 game.last_sound=255;game_frame(0,0,1,0);CHECK(game.charge==42&&game.last_sound==255);
 game_frame(0,0,0,0);CHECK(game.state==InPlay&&game.vy==-42*256&&game.last_sound==3);
 game_start();CHECK(!(game.flags&1)&&game.charge==0&&game.flipper_keys==0);
 /* Existing powered impulse remains, but does not replay the input cue. */
 game_start();game.state=InPlay;game.mask=1;game.phase[0]=25;
 Vec p=pivots[0],t=tips[0][25];int16_t ux=t.x-p.x,uy=t.y-p.y;uint16_t len=isqrt(mul(ux,ux)+mul(uy,uy));int16_t nx=normal(-uy,len),ny=normal(ux,len);
 game.x=t.x+mul(nx,80)/256;game.y=t.y+mul(ny,80)/256;game.vx=game.vy=0;game.last_sound=255;paddle(0,0);
 CHECK(game.flipper_hits==1&&dot(game.vx,game.vy,nx,ny)>256&&game.last_sound==255);
}
static void spinners(void){
 for(uint8_t side=0;side<2;++side){
  uint16_t id=side?489:481;
  Edge spinner[2];
  uint8_t found=0;
  uint16_t first=0;
  for(uint16_t i=0;i<edge_count;++i){
   Edge e=*edge(i);
   if(original_groups[e.group]!=id)continue;
   CHECK(e.kind==Spinner&&e.param==found);
   if(found<2)spinner[found]=e;
   if(!found)first=i;
   ++found;
  }
  CHECK(found==2);
  for(uint8_t reverse=0;reverse<2;++reverse){
   for(uint8_t fast=0;fast<2;++fast){
    game_start();
    rules.wormhole_dest=1;
    Edge*e=spinner+reverse;
    game_place((e->x+e->ex)/2+e->nx/32,(e->y+e->ey)/2+e->ny/32,
               0,fast?15360:256,1);
#ifdef __CX16__
    uint8_t saved=11;
    *(volatile uint8_t*)0=saved;
#endif
    CHECK(!event(e));
#ifdef __CX16__
    CHECK(*(volatile uint8_t*)0==saved);
#endif
    CHECK(game_pose(id)==(reverse?7:1)&&game.last_kind==Spinner);
    CHECK(score()==500&&rules.wormhole_dest==1&&game.last_sound==6);
    for(uint8_t f=0;f<48;++f)rules_tick();
    CHECK(!rules.spinner[side].interval);
    CHECK(score()==(fast?6500:2000));
    CHECK(rules.wormhole_dest==(fast?2:1));
    CHECK(game_pose(id)==(fast?(reverse?3:5):4));
    game_start();
    CHECK(!game_pose(id));
   }
  }
  /* Exercise the geometry and pass-through path with both directed edges. */
  for(uint8_t reverse=0;reverse<2;++reverse){
   game_start();
   Edge*e=spinner+reverse;
   game_place((e->x+e->ex)/2+e->nx/32,(e->y+e->ey)/2+e->ny/32,
              -2*e->nx,-2*e->ny,1);
   Hit hit;
   CHECK(nearest(-e->nx/16,-e->ny/16,&hit)&&hit.id==first+reverse);
   move_time(-e->nx/16,-e->ny/16,1,0);
   CHECK(game.last_kind==Spinner&&score()==500);
   CHECK(game_pose(id)==(reverse?7:1));
  }
 }
}
static void opening_cross(void){
 game.tick=0;
 game_begin(true);
 uint8_t transitions=0;
 bool was=false;
 for(uint16_t i=0;i<StartupFrames;++i){
  bool on=game_lamp(OpeningCrossLamp);
  if(on!=was){++transitions;was=on;}
  if(game.wait<=StartupReadyFrames)CHECK(!on);
  game_frame(false,false,false,false);
 }
 CHECK(transitions>=4);
 CHECK(game.state==Serving&&!game_lamp(OpeningCrossLamp));
}
int main(void){if(!game_load()){puts("# LOAD FAIL\n# DONE");return 1;}slingshots();input_events();spinners();opening_cross();printf("# FEEDBACK %s %u %u\n",failures?"FAIL":"PASS",checks,failures);puts("# DONE");return failures!=0;}
