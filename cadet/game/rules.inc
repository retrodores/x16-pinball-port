/* Source-derived single-ball mechanisms: control.cpp, TRollover, TBumper,
 * TKickback, TSink and TKickout. Bank 61 is selected by unbanked wrappers. */
#ifdef __CX16__
#define RULE_FN __attribute__((section(".rules"),noinline))
#define RULE_DATA __attribute__((section(".rules.rodata")))
#else
#define RULE_FN
#define RULE_DATA
#endif
static RULE_FN void rule_sound(uint8_t id,uint8_t group,uint8_t kind){game.last_group=group;game.last_kind=kind;sound(id);}
static RULE_FN uint16_t countdown(uint16_t n){return n>2?n-2:0;}
static RULE_FN void rule_reset(void){memset(&rules,0,sizeof rules);rules.blink=1;++game.visual_epoch;}
static RULE_FN void rule_gate(uint8_t side,bool open){rules.gate[side]=open;rules.gate_flash[side]=open?600:0;rules.gate_alert[side]=0;++game.visual_epoch;rule_sound(open?SoundGateOpen:SoundGateClose,side?GROUP_502:GROUP_501,Gate);}
static RULE_FN void rule_upgrade(uint8_t bank){
 if(rules.bumper_level[bank]<3){++rules.bumper_level[bank];++game.visual_epoch;
  for(uint8_t i=bank?4:0;i<(bank?7:4);++i)rules.bumper_fire[i]=12;
  game.sound_value=bank;rule_sound(SoundUpgrade,bank?GROUP_405:GROUP_372,Bumper);
 }
 rules.bumper_decay[bank]=7200;
}
static RULE_FN void rule_tick(void){
 if(++rules.blink_clock==6){rules.blink_clock=0;rules.blink^=1;if(rules.lane_flash[0]||rules.lane_flash[1]||rules.hazard_clear[0]||rules.hazard_clear[1]||rules.wormhole_timer||rules.destination_flash||rules.gravity||rules.gate_flash[0]||rules.gate_flash[1]||rules.gate_alert[0]||rules.gate_alert[1])++game.visual_epoch;for(uint8_t i=0;i<6;++i)if(rules.hazard_flash[i]){++game.visual_epoch;break;}}
 for(uint8_t i=0;i<7;++i)if(rules.bumper_fire[i]){rules.bumper_fire[i]-=2;if(!rules.bumper_fire[i])++game.visual_epoch;}
 for(uint8_t side=0;side<2;++side){
  if(rules.lane_flash[side]){rules.lane_flash[side]=countdown(rules.lane_flash[side]);if(!rules.lane_flash[side])++game.visual_epoch;}
  if(rules.gate_flash[side]){rules.gate_flash[side]=countdown(rules.gate_flash[side]);if(!rules.gate_flash[side])++game.visual_epoch;}
  if(rules.hazard_clear[side]){rules.hazard_clear[side]=countdown(rules.hazard_clear[side]);if(!rules.hazard_clear[side]){rules.hazard_bits[side]=0;++game.visual_epoch;}}
  if(rules.bumper_decay[side]){rules.bumper_decay[side]=countdown(rules.bumper_decay[side]);if(!rules.bumper_decay[side]){if(rules.bumper_level[side]){--rules.bumper_level[side];++game.visual_epoch;for(uint8_t b=side?4:0;b<(side?7:4);++b)rules.bumper_fire[b]=12;}rules.bumper_decay[side]=7200;}}
  if(rules.kick_timer[side]){rules.kick_timer[side]=countdown(rules.kick_timer[side]);if(!rules.kick_timer[side]){
   if(rules.kick_phase[side]==1||rules.kick_phase[side]==2){rules.kick_phase[side]=2;++game.visual_epoch;rules.kick_timer[side]=12;rule_sound(SoundKickback,side?GROUP_507:GROUP_505,Kickback);}
   else{rules.kick_phase[side]=0;++game.visual_epoch;rule_gate(side,false);}
  }}
 }
 for(uint8_t i=0;i<6;++i)if(rules.hazard_flash[i]){rules.hazard_flash[i]=countdown(rules.hazard_flash[i]);if(!rules.hazard_flash[i])++game.visual_epoch;}
 if(rules.wormhole_timer){rules.wormhole_timer=countdown(rules.wormhole_timer);if(!rules.wormhole_timer)++game.visual_epoch;}
 if(rules.destination_flash){rules.destination_flash=countdown(rules.destination_flash);if(!rules.destination_flash)++game.visual_epoch;}
 if(rules.hyper_timer){rules.hyper_timer=countdown(rules.hyper_timer);if(!rules.hyper_timer&&rules.hyper_count){--rules.hyper_count;if(rules.hyper_count)rules.hyper_timer=7200;}}
}
static RULE_FN void rule_lane(uint16_t original){
 uint8_t bank=original>=528,bit=bank?(original-528):(522-original);
 if(!rules.lane_flash[bank]){
  rules.lane_bits[bank]^=(uint8_t)(1u<<bit);
  if(rules.lane_bits[bank]==7){rules.lane_bits[bank]=0;rules.lane_flash[bank]=600;rule_upgrade(bank);}
 }
}
static RULE_FN void rule_shift_lanes(uint8_t side){
 for(uint8_t i=0;i<2;++i){uint8_t b=rules.lane_bits[i];if(side)rules.lane_bits[i]=((b<<1)|(b>>2))&7;else rules.lane_bits[i]=((b>>1)|(b<<2))&7;}
}
static RULE_FN void rule_hazard(uint16_t original){
 uint8_t i=(original-454)/2,side=i/3,bit=i%3;rules.hazard_bits[side]|=(uint8_t)(1u<<bit);rules.hazard_flash[i]=240;
 game.sound_value=rules.hazard_bits[side]==7;rule_sound(SoundHazard,game.last_group,Target);
 if(rules.hazard_bits[side]==7){rules.hazard_clear[side]=240;rule_gate(side,true);}
}
static RULE_FN void rule_destination(bool force){
 if(force||rules.wormhole_dest){rules.wormhole_dest=rules.wormhole_dest==3?1:rules.wormhole_dest+1;rules.destination_flash=force?360:rules.destination_flash;}
}
static RULE_FN void rule_award_large(uint32_t n){
 if(game.overflow)return;
 /* Preflight the entire award before committing any 50000-point chunks.
  * Overflow must preserve both the binary score and its decimal digits. */
 uint32_t carry=n;
 for(uint8_t i=0;i<16&&carry;++i){uint16_t sum=game.score[i]+(carry&255);carry=(carry>>8)+(sum>>8);}
 if(carry){game.score_dirty=true;game.overflow=true;return;}
 while(n>=50000){add_score(50000);n-=50000;}if(n)add_score((uint16_t)n);
}
static RULE_FN void rule_capture(const Edge*e){
 uint16_t original=original_groups[e->group];rules.capture_group=e->group;rules.exit_group=e->group;rules.original_z=game.z;rules.original_mask=game.mask;
 game.captured=e->kind;game.param=e->param;game.state=Captured;game.wait=metadata[e->param].delay;game.vx=game.vy=0;game.remx=game.remy=game.accx=game.accy=0;
 game.sound_value=0;
 if(e->kind==Sink){
  if(original==338||original==340||original==342){
   uint8_t entry=(original-338)/2,exit=rules.wormhole_dest?rules.wormhole_dest-1:entry;
   if(rules.wormhole_dest){if(exit==entry){add_score(5000);rules.replay=1;}else add_score(7500);rules.wormhole_dest=0;rules.destination_flash=0;}
   else add_score(2500);
   static const uint8_t group[3] RULE_DATA={GROUP_338,GROUP_340,GROUP_342};
   static const uint8_t param[3] RULE_DATA={META_338,META_340,META_342};
   rules.exit_group=group[exit];game.param=param[exit];rules.wormhole_exit=exit;rules.wormhole_timer=game.wait;
  }
 }else if(e->kind==Kickout){
  const Meta*m=&metadata[e->param];game.x=m->x;game.y=m->y;game.z=m->az;
  if(original==514)add_score(20000);
  else if(original==510){add_score(50000);rules.gravity=0;game.wait=286;}
  else if(original==512){
   static const uint16_t hold[5] RULE_DATA={211,367,211,140,306};
   static const uint32_t award[5] RULE_DATA={10000,20000,20000,50000,150000};
   uint8_t level=rules.hyper_count;game.sound_value=level;rule_award_large(award[level]);game.wait=hold[level];rules.hyper_count=(level+1)%5;rules.hyper_timer=7200;
   if(level==4)rules.gravity=1;
  }
 }
 rule_sound(SoundCapture,e->group,e->kind);
}
static RULE_FN void rule_release(void){
 const Meta*m=&metadata[game.param];game.state=InPlay;game.ramp=false;game.remx=game.remy=game.accx=game.accy=0;
 if(game.captured==Hole){game.mask=m->mask;game.z=m->az;game.vx=0;game.vy=256;}
 else{game.x=m->x;game.y=m->y;game.vx=m->vx;game.vy=m->vy;game.mask=game.captured==Kickout?rules.original_mask:1;game.z=game.captured==Kickout?rules.original_z:77;}
 /* A kickout resets only itself after 0.05 s. A sink receives one integration
    step of exclusion, matching throw_ball's collision-disabled release step. */
 game.disabled[rules.exit_group]=game.captured==Kickout?6:2;touch(rules.exit_group);
 ++game.returns;rule_sound(SoundRelease,rules.exit_group,game.captured);
}
static RULE_FN uint8_t rule_lamp(uint16_t gid){
 if(gid>=128&&gid<=130){uint8_t b=gid-128;return rules.lane_flash[0]?rules.blink:(rules.lane_bits[0]>>b)&1;}
 if(gid>=214&&gid<=216){uint8_t b=gid-214;return rules.lane_flash[1]?rules.blink:(rules.lane_bits[1]>>b)&1;}
 if(gid>=185&&gid<=190){uint8_t i=gid-185;return rules.hazard_clear[i/3]||rules.hazard_flash[i]?rules.blink:(rules.hazard_bits[i/3]>>(i%3))&1;}
 if(gid==148||gid==147){uint8_t side=gid==147;return rules.gate[side]?(rules.gate_flash[side]||rules.gate_alert[side]?rules.blink:1):0;}
 if(gid==228||gid==227){uint8_t side=gid==227;return rules.gate[side]&&(rules.gate_flash[side]||rules.gate_alert[side])?rules.blink:0;}
 if(gid==168)return rules.gravity?rules.blink:0;
 if(gid==191)return rules.wormhole_dest?(rules.destination_flash?rules.blink:1):0;
 uint8_t i;if(gid>=125&&gid<=127){i=gid-125;if(rules.wormhole_timer)return i==rules.wormhole_exit?rules.blink:0;return rules.wormhole_dest!=0;}
 if(gid==122)i=0;else if(gid==116)i=1;else if(gid==119)i=2;else return 0;
 if(rules.wormhole_timer)return i==rules.wormhole_exit&&rules.blink?3-i:0;
 return rules.wormhole_dest?4-rules.wormhole_dest:0;
}
static RULE_FN uint8_t rule_pose(uint16_t gid){
 uint8_t b=255;if(gid>=372&&gid<=396&&(gid-372)%8==0)b=(gid-372)/8;else if(gid>=405&&gid<=421&&(gid-405)%8==0)b=4+(gid-405)/8;
 if(b<7)return 2*rules.bumper_level[b>=4]+(rules.bumper_fire[b]!=0);
 if(gid==501||gid==502)return rules.gate[gid-501];
 if(gid==505||gid==507)return rules.kick_phase[(gid-505)/2]>=2;
 return 0;
}
