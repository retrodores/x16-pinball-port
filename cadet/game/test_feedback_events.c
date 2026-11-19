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
 game_frame(0,0,1,0);CHECK(game.charge==2&&game.last_sound==255);
 game_frame(0,0,1,0);CHECK(game.charge==3);
 for(uint8_t i=0;i<146;++i)game_frame(0,0,1,0);CHECK(game.charge==100&&game.last_sound==255);
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
 for(uint8_t i=0;i<30;++i)game_frame(0,0,1,0);CHECK(game.charge==21&&game.state==Captured);
 game_frame(0,0,0,0);CHECK(game.state==Captured&&!(game.flags&1)&&game.last_sound==3);
 /* A ball returning while the user is still pulling retains the held charge. */
 game.state=InPlay;game_frame(0,0,1,0);game.charge=40;game.charge_clock=1;
 Edge plunger=wall(473);event(&plunger);CHECK(game.state==Serving&&(game.flags&1)&&game.charge==40&&game.charge_clock==1);
 game.last_sound=255;game_frame(0,0,1,0);CHECK(game.charge==41&&game.last_sound==255);
 game_frame(0,0,0,0);CHECK(game.state==InPlay&&game.vy==-41*256&&game.last_sound==3);
 game_start();CHECK(!(game.flags&1)&&game.charge==0&&game.flipper_keys==0);
 /* Existing powered impulse remains, but does not replay the input cue. */
 game_start();game.state=InPlay;game.mask=1;game.phase[0]=25;
 Vec p=pivots[0],t=tips[0][25];int16_t ux=t.x-p.x,uy=t.y-p.y;uint16_t len=isqrt(mul(ux,ux)+mul(uy,uy));int16_t nx=normal(-uy,len),ny=normal(ux,len);
 game.x=t.x+mul(nx,80)/256;game.y=t.y+mul(ny,80)/256;game.vx=game.vy=0;game.last_sound=255;paddle(0,0);
 CHECK(game.flipper_hits==1&&dot(game.vx,game.vy,nx,ny)>256&&game.last_sound==255);
}
int main(void){if(!game_load()){puts("# LOAD FAIL\n# DONE");return 1;}slingshots();input_events();printf("# FEEDBACK %s %u %u\n",failures?"FAIL":"PASS",checks,failures);puts("# DONE");return failures!=0;}
