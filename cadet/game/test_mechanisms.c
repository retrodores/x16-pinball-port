/* Original single-ball rule contracts: control.cpp, TRollover.cpp,
 * TKickback.cpp, TKickout.cpp and TSink.cpp. This exercises production
 * events/timers AND real swept contacts; it is not a random soak oracle. */
#include "engine.c"
#include <stdio.h>
static unsigned checks,failures;
#define CHECK(x) do{++checks;if(!(x)){++failures;printf("# FAIL %u\n",(unsigned)__LINE__);}}while(0)
static uint32_t score(void){return (uint32_t)game.score[0]|((uint32_t)game.score[1]<<8)|((uint32_t)game.score[2]<<16)|((uint32_t)game.score[3]<<24);}
static Edge object(uint16_t original,uint8_t exit){
 Edge e={0};for(uint16_t i=0;i<edge_count;++i){e=*edge(i);if(original_groups[e.group]==original&&((e.flags&8)!=0)==exit)return e;}CHECK(false);return e;
}
static void hit(uint16_t original){Edge e=object(original,0);game.flash[e.group]=0;event(&e);}
static void timers(uint16_t n){while(n--)rules_tick();}
static void lane(uint16_t original){Edge e=object(original,0),out=object(original,1);event(&e);event(&out);game.disabled[e.group]=0;}
static void contact(uint16_t original){
 Edge e=object(original,0);CHECK(!(e.flags&1));game_place(e.x+(e.ex-e.x)/4+e.nx/64,(e.y+e.ey)/2+e.ny/64,-e.nx*8,-e.ny*8,e.mask);
 move(-e.nx/64,-e.ny/64,1);
}
static void lanes(void){
 game_start();CHECK(game_pose(501)==1&&game_pose(502)==1);CHECK(game_lamp(147)==1);timers(300);CHECK(game_lamp(147)==1&&game_lamp(227)==0);
 lane(522);CHECK(rules.lane_bits[0]==1);CHECK(score()==2000);lane(522);CHECK(rules.lane_bits[0]==0);CHECK(score()==4000);
 lane(522);rules_shift(1);CHECK(rules.lane_bits[0]==2);rules_shift(0);CHECK(rules.lane_bits[0]==1);
 lane(521);lane(520);CHECK(rules.lane_bits[0]==0&&rules.lane_flash[0]==600);CHECK(rules.bumper_level[0]==1);CHECK(game_pose(372)==3);timers(6);CHECK(game_pose(372)==2);
 lane(522);CHECK(rules.lane_bits[0]==0);timers(294);CHECK(rules.lane_flash[0]==0);
 for(uint8_t level=1;level<4;++level){lane(522);lane(521);lane(520);CHECK(rules.bumper_level[0]==(level<3?level+1:3));timers(300);}
 CHECK(rules.bumper_level[0]==3);timers(3300);CHECK(rules.bumper_level[0]==2);
 game_start();lane(528);lane(529);lane(530);CHECK(score()==1500);CHECK(rules.bumper_level[1]==1);CHECK(game_pose(405)==3);CHECK(game.last_sound==SoundLane&&original_groups[game.last_group]==530&&game.last_kind==Sensor);
 /* Entry/exit geometry is selected by rollover state, and only entry scores. */
 game_start();Edge e=object(522,0),out=object(522,1);CHECK((e.flags&4)&&!(e.flags&8)&&(out.flags&8));
 event(&e);CHECK(game.lamps[e.group]==1&&score()==2000);event(&out);CHECK(game.lamps[e.group]==0&&score()==2000&&game.disabled[e.group]==12);
}
static void kickbacks(void){
 for(uint8_t side=0;side<2;++side){
  uint16_t kick=side?507:505,gate=side?502:501;
  game_start();contact(kick);CHECK(rules.kick_phase[side]==1&&rules.kick_timer[side]==84);CHECK(game_pose(kick)==0);
  timers(41);CHECK(rules.kick_phase[side]==1);timers(1);CHECK(rules.kick_phase[side]==2&&rules.kick_timer[side]==12);CHECK(game.last_sound==SoundKickback&&game_pose(kick)==1);
  Edge e=object(kick,0);contact(kick);CHECK(rules.kick_phase[side]==3);CHECK(dot(game.vx,game.vy,e.nx,e.ny)>10000);
  timers(6);CHECK(rules.kick_phase[side]==0&&game_pose(gate)==0);CHECK(game.last_sound==SoundGateClose);
  for(uint8_t i=0;i<3;++i)hit(454+side*6+i*2);CHECK(rules.hazard_bits[side]==7&&game_pose(gate)==1);CHECK(score()==2250);
  timers(120);CHECK(rules.hazard_bits[side]==0);CHECK(game_pose(gate)==1);
 }
}
/* Each shot starts above its outlane rollover. After that, the normal
 * frame loop alone must carry it into the kicker and back up the table. */
static void outlane_returns(void){
 static const int16_t x[2]={1685,-1580},vx[2]={-900,0},vy[2]={5000,3000};
 for(uint8_t side=0;side<2;++side){
  uint16_t gate=side?502:501;
  uint8_t entry=0,armed=0,boosted=0,closed=0;
  game_start();
  game_place(x[side],1935,vx[side],vy[side],1);
  for(uint8_t frame=1;frame<=120&&game.state==InPlay;++frame){
   game_frame(0,0,0,0);
   if(!entry&&rules.gate_alert[side])entry=frame;
   if(!armed&&rules.kick_phase[side]==1)armed=frame;
   if(!boosted&&rules.kick_phase[side]==3){
    boosted=frame;
    CHECK(game.vy<-10000);
   }
   if(boosted&&!game_pose(gate)){closed=frame;break;}
  }
  CHECK(entry&&entry<armed);
  CHECK(boosted&&boosted-armed>=42);
  CHECK(closed>boosted&&closed-boosted<=6);
  CHECK(game.state==InPlay&&game.escapes==0&&game.balls==3);
  CHECK(game_pose(side?501:502)==1);
 }
}
static void captures(void){
 static const uint16_t sink[3]={338,340,342};
 for(uint8_t entry=0;entry<3;++entry)for(uint8_t dest=0;dest<4;++dest){
  game_start();game.state=InPlay;
  for(uint8_t i=0;i<dest;++i)rules_destination(true);
  hit(sink[entry]);uint8_t exit=dest?dest-1:entry;
  CHECK(game.state==Captured&&game.captured==Sink);CHECK(game.wait==240);CHECK(original_groups[rules.exit_group]==sink[exit]);
  CHECK(score()==(dest?(exit==entry?5000:7500):2500));CHECK(game.last_sound==SoundCapture);CHECK(rules.wormhole_dest==0);
  if(dest&&exit==entry){CHECK(rules.replay==1);timers(600);CHECK(rules.replay==1);}
  uint16_t guard=0;while(game.state==Captured&&guard++<121)game_frame(0,0,0,0);
  CHECK(guard==120&&game.state==InPlay);const Meta*m=&metadata[game.param];CHECK(game.x==m->x&&game.y==m->y&&game.vx==m->vx&&game.vy==(exit==1?-7168:m->vy));
  CHECK(game.last_sound==SoundRelease&&game.last_group==rules.exit_group);CHECK(game.ignore==0);
  for(uint8_t k=0;k<6;++k)game_frame(0,0,0,0);CHECK(game.returns==1);
 }
 /* Exercise the recorded repeat through the real sweep and timers. */
 game_start();game.state=InPlay;hit(340);
 for(uint16_t i=0;i<450&&game.state!=Between;++i)game_frame(0,0,0,0);
 CHECK(game.state==InPlay||game.state==Between);
 CHECK(game.returns==1&&game.escapes==0);
 game_start();game_place(1007,-69,0,0,1);game.z=123;CHECK(well_force());CHECK(game.state==Captured&&game.z==0&&game.wait==180);CHECK(score()==20000);
 for(uint8_t i=0;i<89;++i)game_frame(0,0,0,0);CHECK(game.state==Captured);game_frame(0,0,0,0);CHECK(game.state==InPlay&&game.z==123&&game.vx==-8960&&game.vy==-8960);CHECK(game.disabled[GROUP_514]==6);
 game_start();static const uint16_t holds[5]={211,367,211,140,306};static const uint32_t awards[5]={10000,20000,20000,50000,150000};
 for(uint8_t level=0;level<5;++level){game.state=InPlay;uint32_t before=score();hit(512);CHECK(game.wait==holds[level]&&game.sound_value==level);CHECK(score()-before==awards[level]);rules_release();}
 CHECK(rules.gravity==1&&rules.hyper_count==0);game_place(0,1536,0,0,1);CHECK(well_force());CHECK(game.state==Captured&&game.z==77&&rules.gravity==0);
 game_start();rules_destination(true);hit(338);rules_release();drain();CHECK(game.balls==3);game.state=InPlay;drain();CHECK(game.balls==2);
}
static void mission_rings(void){
 game_start();
 CHECK(game_ring_lamp(0)&&!game_ring_lamp(2));
 for(uint8_t i=0;i<72;++i)rules_tick();
 CHECK(game_ring_lamp(18)==1&&game_ring_lamp(19)==0);
 Edge ramp={0};
 for(uint16_t i=0;i<edge_count;++i){ramp=*edge(i);if(ramp.kind==Ramp&&original_groups[ramp.group]==101&&metadata[ramp.param].action==1)break;}
 CHECK(ramp.kind==Ramp&&original_groups[ramp.group]==101);
 for(uint8_t tour=0;tour<3;++tour){
  hit(448);CHECK(game.mission==SelectLaunch);
  event(&ramp);CHECK(game.mission==LaunchTraining&&game.mission_left==3);
  CHECK(game_ring_lamp(0)&&game_ring_lamp(1));
  for(uint8_t t=0;t<5;++t)rules_tick();
  CHECK(game_ring_lamp(17)&&game_ring_lamp(0)&&!game_ring_lamp(1));
  for(uint8_t i=0;i<3;++i)event(&ramp);
  CHECK(game.mission==NoMission);
 }
 CHECK(game.rank==2&&game.rank_progress==0&&game.ring_flash==300);
 for(uint16_t t=0;t<300;++t)rules_tick();
 CHECK(!game_ring_lamp(0)&&game_ring_lamp(19));
 game_start();hit(452);event(&ramp);
 CHECK(game.mission==Practice&&game.mission_left==8);
 for(uint8_t i=0;i<8;++i)mission_advance();
 CHECK(game.mission==NoMission&&game.rank_progress==6&&game_ring_lamp(5)&&!game_ring_lamp(6));
}

int main(void){
 if(!game_load()){puts("# LOAD FAIL\n# DONE");return 1;}
 mission_rings();
#ifndef TEST_PART
#define TEST_PART 0
#endif
#if TEST_PART==0 || TEST_PART==1
 lanes();
#endif
#if TEST_PART==0 || TEST_PART==2
 kickbacks();
 outlane_returns();
#endif
#if TEST_PART==0 || TEST_PART==3
 captures();
#endif
 printf("# MECHANISMS %s %u %u\n",failures?"FAIL":"PASS",checks,failures);
 puts("# DONE");return failures!=0;
}
