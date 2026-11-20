/* Integer C adaptation of the proven wireframe sweep/index implementation.
 * Geometry and component parameters are now from the initialized original table. */
#include "engine.h"
#include "model.h"
#include "awards.h"
#include <string.h>
#ifdef __CX16__
#include <cbm.h>
uint32_t fastmul8(uint16_t,uint8_t);
uint16_t fastsqrt(uint32_t);
uint32_t fastmul16(uint16_t,uint16_t);
void audio_effect(uint8_t);
void audio_stop();
#else
#include <stdio.h>
static uint8_t model[180000];
#endif

#ifdef CADET_PROFILE
uint32_t cost[3];
static uint32_t cycles(void){uint8_t a=*(volatile uint8_t*)0x9fb8,b=*(volatile uint8_t*)0x9fb9,c=*(volatile uint8_t*)0x9fba,d=*(volatile uint8_t*)0x9fbb;return(uint32_t)a|((uint32_t)b<<8)|((uint32_t)c<<16)|((uint32_t)d<<24);}
#endif
typedef struct {
 uint16_t interval, remaining; /* Q8 units of one 60 Hz frame */
 uint8_t pose, reverse;
} FlagSpinner;
typedef struct {
 FlagSpinner spinner[2];
 uint16_t lane_flash[2],hazard_clear[2],bumper_decay[2],kick_timer[2],gate_flash[2];
 uint16_t hazard_flash[6],wormhole_timer,destination_flash,replay,hyper_timer;
 int16_t original_z;
 uint8_t opening_random,cross_hold,gate_alert[2],blink,blink_clock,bumper_fire[7],rebounder_fire[4],bumper_level[2],lane_bits[2],hazard_bits[2],gate[2],kick_phase[2];
 uint8_t wormhole_dest,wormhole_exit,hyper_count,gravity,capture_group,exit_group,original_mask;
} RuleState;
static RuleState rules;
Game game;static uint16_t ramp_ignored[8];static uint8_t ramp_ignore_count;
/* Resident trampolines may switch away from the caller's bank. */
#define BANK_TRAMPOLINE __attribute__((section(".text.bank_trampolines"),noinline))
#ifdef __CX16__
#define MECHANIC_FN __attribute__((section(".mechanics"),noinline))
#define MECHANIC_ENTER uint8_t mechanic_saved=*(volatile uint8_t*)0; *(volatile uint8_t*)0=10; __asm__ volatile("":::"memory")
#define MECHANIC_LEAVE __asm__ volatile("":::"memory"); *(volatile uint8_t*)0=mechanic_saved
#else
#define MECHANIC_FN
#define MECHANIC_ENTER
#define MECHANIC_LEAVE
#endif
static BANK_TRAMPOLINE void rules_destination(bool);
static uint8_t active[160],active_flags[160],active_count;
static void touch(uint8_t c){if(!active_flags[c]){active_flags[c]=1;active[active_count++]=c;}}
#ifdef CADET_BRUTE
static uint16_t cell[edge_count+1],cell_id=65535;
typedef uint16_t CandidateIndex;
#else
static uint16_t cell[128],cell_id=65535;
typedef uint8_t CandidateIndex;
#endif
#ifndef __CX16__
static uint16_t cache_id[16];static Edge cache[16];
#endif
static int16_t ax(int16_t x){return x<0?-x:x;}
#ifdef __CX16__
int32_t signedmul(int16_t,int16_t);
#define mul signedmul
#else
static int32_t mul(int16_t a,int16_t b){return(int32_t)a*b;}
#endif
static uint32_t umul(uint16_t a,uint16_t b){
#ifdef __CX16__
 return fastmul16(a,b);
#else
 return (uint32_t)a*b;
#endif
}
static uint32_t wide_mul(uint32_t a,uint16_t b){return umul(a,b)+((uint32_t)((uint16_t)(a>>16)*b)<<16);}

// Exact signed division over the 16-bit input range, using reciprocal products.
static int16_t div60(int16_t v){uint16_t q=umul(v<0?-(int32_t)v:v,34953)>>21;return v<0?-q:q;}
static int16_t div120(int16_t v){uint16_t q=umul(v<0?-(int32_t)v:v,34953)>>22;return v<0?-q:q;}
static int16_t div300(int16_t v){uint16_t q=umul(v<0?-(int32_t)v:v,55925)>>24;return v<0?-q:q;}
static int16_t dot(int16_t x,int16_t y,int16_t nx,int16_t ny){if(!ny){if(nx==256)return x;if(nx== -256)return -x;}if(!nx){if(ny==256)return y;if(ny== -256)return -y;}return (mul(x,nx)+mul(y,ny))/256;}
// Exact floor(256*n/d), bounded to a unit fraction; no 32-bit division.
#ifdef __CX16__
uint16_t fraction8(uint16_t,uint16_t);
#define fraction fraction8
#else
__attribute__((noinline)) static uint16_t fraction(uint16_t n,uint16_t d){if(!n)return 0;if(n>=d)return 256;uint16_t q=0;for(uint8_t i=0;i<8;++i){n<<=1;q<<=1;if(n>=d){n-=d;++q;}}return q;}
#endif
#ifdef __CX16__
uint16_t fraction32(uint32_t,uint32_t);
static uint16_t fraction_wide(uint32_t n,uint32_t d){return n<32768&&d<32768?fraction(n,d):fraction32(n,d);}
#else
static uint16_t fraction_wide(uint32_t n,uint32_t d){if(n<32768&&d<32768)return fraction(n,d);if(n>=d)return 256;uint16_t q=0;for(uint8_t i=0;i<8;++i){n<<=1;q<<=1;if(n>=d){n-=d;++q;}}return q;}
#endif
static int16_t normal(int16_t n,uint16_t d){int16_t q=fraction(ax(n),d);return n<0?-q:q;}
static uint16_t isqrt(uint32_t n){
#ifdef __CX16__
 return fastsqrt(n);
#else
 uint32_t r=0,b=1UL<<30;while(b>n)b>>=2;while(b){if(n>=r+b){n-=r+b;r=(r>>1)+b;}else r>>=1;b>>=2;}return r;
#endif
}
static void read(uint8_t bank,uint16_t offset,void*d,uint16_t n){
#ifdef __CX16__
 uint8_t saved=*(volatile uint8_t*)0;*(volatile uint8_t*)0=bank;memcpy(d,(void*)(0xa000+offset),n);*(volatile uint8_t*)0=saved;
#else
 memcpy(d,model+(uint32_t)(bank-1)*8192+offset,n);
#endif
}
bool game_load(void){cell_id=65535;
#ifndef __CX16__
 for(uint8_t i=0;i<16;++i)cache_id[i]=65535;
#endif
#ifdef __CX16__
 uint8_t saved=*(volatile uint8_t*)0;bool ok=true;char name[]="GEOM0.BIN";
#ifndef RULES_FILE
#define RULES_FILE "CADET.RUL"
#endif
#ifndef PHYSICS_FILE
#define PHYSICS_FILE "CADET.PHY"
#endif
#ifndef MECHANICS_FILE
#define MECHANICS_FILE "CADET.MEC"
#endif
 *(volatile uint8_t*)0=62;cbm_k_setnam(PHYSICS_FILE);cbm_k_setlfs(1,8,2);ok=(uintptr_t)cbm_k_load(0,(void*)0xa000)>255;
 *(volatile uint8_t*)0=61;cbm_k_setnam(RULES_FILE);cbm_k_setlfs(1,8,2);ok=ok&&((uintptr_t)cbm_k_load(0,(void*)0xa000)>255);
 for(uint8_t i=0;i<3;++i){name[4]='0'+i;*(volatile uint8_t*)0=1+i*8;cbm_k_setnam(name);cbm_k_setlfs(1,8,2);ok=ok&&((uintptr_t)cbm_k_load(0,(void*)0xa000)>255);}
 *(volatile uint8_t*)0=10;cbm_k_setnam(MECHANICS_FILE);cbm_k_setlfs(1,8,2);
 ok=ok&&((uintptr_t)cbm_k_load(0,(void*)0xb608)>255);
 *(volatile uint8_t*)0=saved;return ok;
#else
 FILE*f=fopen("cadet/play-build/MODEL.BIN","rb");if(!f)return false;bool ok=fread(model,1,sizeof model,f)>0;fclose(f);return ok;
#endif
}
void sound(uint8_t id){game.last_sound=id;
#if defined(__CX16__) && defined(PIN_AUDIO)
 if(id==255)audio_stop();else audio_effect(id);
#endif
}
void add_score(uint16_t n){if(game.overflow)return;game.score_dirty=true;uint16_t carry=n;for(uint8_t i=0;i<16&&carry;++i){uint16_t sum=game.score[i]+(carry&255);carry=(carry>>8)+(sum>>8);}if(carry){game.overflow=true;return;}carry=n;for(uint8_t i=0;i<16&&carry;++i){uint16_t sum=game.score[i]+(carry&255);game.score[i]=sum;carry=(carry>>8)+(sum>>8);}if(carry){game.overflow=true;return;}carry=n;uint8_t digit=0;
 /* Known table awards have trailing zeros. Skip them without division; the
    generic path still accepts every uint16_t value and all 128 score bits. */
 switch(n){case 500:carry=5;digit=2;break;case 750:carry=75;digit=1;break;
 case 1000:carry=1;digit=3;break;case 1500:carry=15;digit=2;break;
 case 2000:carry=2;digit=3;break;case 2500:carry=25;digit=2;break;
 case 5000:carry=5;digit=3;break;case 10000:carry=1;digit=4;break;
 case 15000:carry=15;digit=3;break;case 20000:carry=2;digit=4;break;
 case 50000:carry=5;digit=4;break;default:break;}
 for(uint8_t i=digit;i<40&&carry;++i){uint8_t add;
 if(carry<10){add=carry;carry=0;}else{add=carry%10;carry/=10;}uint8_t d=game.digits[i]+add;if(d>=10){d-=10;++carry;}game.digits[i]=d;}}
#include "rules.inc"
/* All overlay calls enter from unbanked RAM. Helpers called by the overlay
 * either leave RAM_BANK unchanged or restore it before returning. Resident
 * wrappers must not inline into an overlay: changing banks there would replace
 * the instructions currently executing before the nested call can return. */
#ifdef __CX16__
#define RULE_ENTER uint8_t rule_saved=*(volatile uint8_t*)0; *(volatile uint8_t*)0=61; __asm__ volatile("":::"memory")
#define RULE_LEAVE __asm__ volatile("":::"memory"); *(volatile uint8_t*)0=rule_saved
#else
#define RULE_ENTER
#define RULE_LEAVE
#endif
static BANK_TRAMPOLINE void rules_spin(const Edge*e){
 MECHANIC_ENTER;rule_spin_start(e->group==GROUP_489,e->param);MECHANIC_LEAVE;
}
static BANK_TRAMPOLINE void rules_reset(void){RULE_ENTER;rule_reset();RULE_LEAVE;}
static MECHANIC_FN void ring_tick(void);
static BANK_TRAMPOLINE void rules_tick(void){
 RULE_ENTER;rule_tick();RULE_LEAVE;
 if(game.state==Ready||game.ring_flash||game.mission>=Practice||rules.spinner[0].interval||rules.spinner[1].interval){
  MECHANIC_ENTER;
  if(rules.spinner[0].interval||rules.spinner[1].interval)rule_spin_tick();
  ring_tick();
  MECHANIC_LEAVE;
 }
}
static BANK_TRAMPOLINE void rules_capture(const Edge*e){RULE_ENTER;rule_capture(e);++game.visual_epoch;RULE_LEAVE;}
static BANK_TRAMPOLINE void rules_release(void){RULE_ENTER;rule_release();++game.visual_epoch;RULE_LEAVE;}
static BANK_TRAMPOLINE void rules_lane(uint16_t n){RULE_ENTER;rule_lane(n);++game.visual_epoch;RULE_LEAVE;}
static BANK_TRAMPOLINE void rules_shift(uint8_t n){RULE_ENTER;rule_shift_lanes(n);++game.visual_epoch;RULE_LEAVE;}
static BANK_TRAMPOLINE void rules_hazard(uint16_t n){RULE_ENTER;rule_hazard(n);++game.visual_epoch;RULE_LEAVE;}
static BANK_TRAMPOLINE void rules_rebounder(uint8_t n){RULE_ENTER;rule_rebounder(n);RULE_LEAVE;}
static BANK_TRAMPOLINE void rules_destination(bool n){RULE_ENTER;rule_destination(n);++game.visual_epoch;RULE_LEAVE;}
/* Spread four interleaved phases across the available lamp inserts. */
static RULE_FN uint8_t startup_lamp(uint8_t group){
 if(game.wait<=StartupReadyFrames)return 0;
 return ((group^(group>>3)^game.ring_phase)&3u)<2;
}
BANK_TRAMPOLINE uint8_t game_lamp(uint16_t n){RULE_ENTER;uint8_t r=n==254?(game.state==Ready&&rules.cross_hold!=0):
  game.state==Ready?startup_lamp((uint8_t)n):rule_lamp(n);RULE_LEAVE;return r;}
BANK_TRAMPOLINE uint8_t game_pose(uint16_t n){RULE_ENTER;uint8_t r=rule_pose(n);RULE_LEAVE;return r;}
/* Rank steps persist across balls. The first-rank practice and launch
 * missions use the original target selection, counts and rank award. */
static BANK_TRAMPOLINE void mission_advance(void){
 if(--game.mission_left)return;
 game.mission=NoMission;
 game.rank_progress+=6;
 if(game.rank_progress>=18){
  game.rank_progress=0;
  if(game.rank<9)++game.rank;
  game.ring_flash=300;
 }
 /* 500,000 is ten exact awards; apply none if the sequence would overflow. */
 RULE_ENTER;
 rule_award_large(500000);
 RULE_LEAVE;
 ++game.visual_epoch;
}
__attribute__((noinline)) uint8_t game_ring_lamp(uint8_t index){
 if(game.state==Ready)return ((index+game.ring_phase)&7u)<4&&game.wait>StartupReadyFrames;
 if(index>=18)return index-18<game.rank;
 if(game.ring_flash)return 1u^((game.ring_flash>>4)&1u);
 if(game.mission>=Practice){
  uint8_t next=game.ring_phase+1;
  if(next==18)next=0;
  return index==game.ring_phase||index==next;
 }
 return index<game.rank_progress;
}
static void mission_ramp(void){
 if(game.mission==LaunchTraining){mission_advance();return;}
 if(game.mission==SelectPractice||game.mission==SelectLaunch){
  bool practice=game.mission==SelectPractice;
  game.mission=practice?Practice:LaunchTraining;
  game.mission_left=practice?8:3;
  game.ring_phase=0;game.ring_clock=0;
  add_score(10000);++game.visual_epoch;
 }
}
static MECHANIC_FN void ring_tick(void){
 if(game.state==Ready){
  if(game.wait==StartupFrames)sound(SoundStartup);
  --game.wait;
  if(rules.cross_hold)--rules.cross_hold;
  if(game.wait==StartupReadyFrames)rules.cross_hold=0;
  else if(game.wait>StartupReadyFrames&&game.wait%12u==11u){
   uint8_t random=rules.opening_random;
   random=(random>>1)^((random&1)?0xb8:0);
   rules.opening_random=random;
   if(random<75)rules.cross_hold=6u+(random>>1);
  }
  if(game.wait==StartupReadyFrames||(game.wait>StartupReadyFrames&&++game.ring_clock==15)){
   game.ring_clock=0;++game.ring_phase;++game.visual_epoch;
  }
  return;
 }
 if(game.ring_flash){
  if(!(--game.ring_flash&15))++game.visual_epoch;
 }
 if(game.mission>=Practice&&++game.ring_clock==5){
  game.ring_clock=0;
  game.ring_phase=game.ring_phase?game.ring_phase-1:17;
  ++game.visual_epoch;
 }
}
static void serve(){sound(255);rules.gate[0]=rules.gate[1]=1;rules.gate_flash[0]=rules.gate_flash[1]=600;++game.visual_epoch;game.ball_number=4-game.balls;game.state=Serving;game.x=serve_x;game.y=plunger_y-2;game.z=77;game.vx=game.vy=game.remx=game.remy=game.accx=game.accy=0;game.mask=1;game.ramp=false;game.charge=0;game.charge_clock=0;game.flags=0;game.nudges=0;game.last_group=GROUP_473;game.last_kind=Plunger;sound(SoundFeed);}
static RULE_FN void reset_game(void){
 uint8_t epoch=game.visual_epoch, spinner_epoch=game.spinner_epoch;
 active_count=0;memset(active_flags,0,sizeof active_flags);
 memset(&game,0,sizeof game);game.visual_epoch=epoch;game.spinner_epoch=spinner_epoch;
 game.balls=3;game.multiplier=1;game.rank=1;game.ball_number=1;game.score_dirty=true;
 rule_reset();
}
BANK_TRAMPOLINE void game_begin(bool show){
 uint8_t seed=(uint8_t)game.tick;
 RULE_ENTER;reset_game();rules.opening_random=seed?seed:1;RULE_LEAVE;
 if(show){game.wait=StartupFrames;sound(255);++game.visual_epoch;}else serve();
}
static void drain(){if(game.state!=InPlay)return;game.state=Between;game.mission=NoMission;game.mission_left=0;game.wait=120;game.vx=game.vy=0;game.mask=0;game.ramp=false;++game.drains;if(rules.replay)rules.replay=0;else if(game.balls)--game.balls;rules_reset();memset(game.lamps,0,sizeof game.lamps);memset(game.disabled,0,sizeof game.disabled);sound(5);}
#ifdef __CX16__
__attribute__((section(".physics"),noinline))
#endif
static void limit_core(){const int16_t cap=15360;int16_t m=ax(game.vx)>ax(game.vy)?ax(game.vx):ax(game.vy);if(m>cap){game.vx=(int32_t)game.vx*cap/m;game.vy=(int32_t)game.vy*cap/m;}}
static BANK_TRAMPOLINE void limit(void){
#ifdef __CX16__
 uint8_t saved=*(volatile uint8_t*)0;*(volatile uint8_t*)0=62;__asm__ volatile("":::"memory");
#endif
 limit_core();
#ifdef __CX16__
 __asm__ volatile("":::"memory");*(volatile uint8_t*)0=saved;
#endif
}

/* maths::basic_collision expressed in velocity coordinates, Q8. */
#ifdef __CX16__
uint16_t ratio12(uint16_t,uint16_t);
#else
static uint16_t ratio12(uint16_t n,uint16_t d){
 uint16_t whole=0,q=0;if(!d)return 0;
 while(n>=d){n-=d;whole+=4096;}
 for(uint8_t i=0;i<12;++i){n<<=1;q<<=1;if(n>=d){n-=d;++q;}}
 return whole+q;
}
#endif
static MECHANIC_FN int16_t rebound_core(int16_t nx,int16_t ny,uint8_t e,uint8_t smooth,uint8_t boost,int16_t inward){
 if(inward<=0)return 0;
 uint16_t speed=isqrt(mul(game.vx,game.vx)+mul(game.vy,game.vy));
 int16_t normal_part=(int16_t)(umul(inward,(uint16_t)smooth+e)>>8);
 int16_t tx=(mul(game.vx,smooth)+mul(nx,normal_part))/256;
 int16_t ty=(mul(game.vy,smooth)+mul(ny,normal_part))/256;
 uint16_t magnitude=isqrt(mul(tx,tx)+mul(ty,ty));
 int16_t final_speed=speed-(umul(inward,256-e)>>8);
 if(magnitude){uint16_t scale=ratio12(final_speed,magnitude);game.vx=mul(tx,scale)/4096;game.vy=mul(ty,scale)/4096;}
 else game.vx=game.vy=0;
 if(boost){game.vx+=mul(nx,boost);game.vy+=mul(ny,boost);}
 limit();return inward;
}
static BANK_TRAMPOLINE int16_t rebound(int16_t nx,int16_t ny,uint8_t e,uint8_t smooth,uint8_t boost,int16_t inward){
#ifdef CADET_PROFILE
 uint32_t before=cycles();
#endif
 MECHANIC_ENTER;
 int16_t result=rebound_core(nx,ny,e,smooth,boost,inward);
 MECHANIC_LEAVE;
#ifdef CADET_PROFILE
 cost[1]+=cycles()-before;
#endif
 return result;
}
typedef struct {uint16_t id;int16_t t,nx,ny,x,y;bool circle;} Hit;
static const Edge* edge(uint16_t id){
#ifdef __CX16__
 *(volatile uint8_t*)0=12+(id>>8);__asm__ volatile("":::"memory");return (const Edge*)(0xa000+(id&255)*32);
#else
 uint8_t slot=id&15;if(cache_id[slot]!=id){read(12+(id>>8),(id&255)*32,&cache[slot],32);cache_id[slot]=id;}return &cache[slot];
#endif
}

int16_t bound_query[4];
#ifdef __CX16__
extern const Edge* bounded_edge(uint16_t);
#else
static const Edge* bounded_edge(uint16_t id){const Edge*e=edge(id);return bound_query[1]<e->xlo||bound_query[3]<e->ylo||bound_query[0]>e->xhi||bound_query[2]>e->yhi?0:e;}
#endif
static uint32_t ray_a,ray_r2,ray_ar;static uint16_t circle_ids[24];static int16_t circle_distance[24];
__attribute__((noinline)) static bool circle_hit(uint16_t id,int16_t dx,int16_t dy,Hit*hit){const Edge*e=edge(id);int16_t t,nx,ny,px,py;
   int16_t sx=game.x-e->x,sy=game.y-e->y;
   uint32_t r2=(uint16_t)e->ex|((uint32_t)(uint16_t)e->ey<<16);
   int32_t projection=-(mul(sx,dx)+mul(sy,dy));if(projection<=0)return false;
   uint32_t oldsq=mul(sx,sx)+mul(sy,sy);
   if(oldsq<r2)return false;
   if(oldsq<=r2)t=0;
   else{
    // Discriminant identity: a*r*r - cross(s,v)^2. All circles are <=181 Q8
    // units and each movement component <=256: the products fit unsigned 32 bits.
    // A nonzero projection guarantees nonzero motion. Defer the squared
    // length until an actual circle candidate needs the discriminant.
    if(!ray_a)ray_a=mul(dx,dx)+mul(dy,dy);
    uint32_t a=ray_a;
    int32_t cross=mul(sx,dy)-mul(sy,dx);
    if(cross>65535||cross< -65535)return false;
    uint16_t cross_abs=cross<0?-cross:cross;if(ray_r2!=r2){ray_r2=r2;ray_ar=wide_mul(a,(uint16_t)r2);}uint32_t ar=ray_ar,cross2=umul(cross_abs,cross_abs);
    if(cross2>=ar)return false;
    uint32_t discriminant=ar-cross2;
    uint16_t bound=hit->t<255?hit->t+1:256;
    int32_t minimum=projection-(wide_mul(a,bound)>>8);
#ifndef PIN_REFERENCE
    if(minimum>65535||(minimum>0&&umul(minimum,minimum)>discriminant))return false;
#endif
    int32_t numerator=projection-isqrt(discriminant);
    if(numerator>0&&(uint32_t)numerator>a)return false;
    t=numerator<=0?0:fraction_wide(numerator,a);
   }
   if(t>hit->t||(t==hit->t&&id>=hit->id))return false;
   px=game.x+mul(dx,t)/256;py=game.y+mul(dy,t)/256;
   nx=normal(px-e->x,e->r);ny=normal(py-e->y,e->r);

 *hit=(Hit){id,t,nx,ny,px,py,true};return true;
}
__attribute__((noinline)) static bool nearest_core(int16_t dx,int16_t dy,Hit*hit){
 int16_t gx=(game.x+dx/2+3072)/128,gy=(game.y+dy/2+4096)/128;if(gx<0||gx>=48||gy<0||gy>=64)return false;
 uint16_t ci=gx+gy*48;if(game.mask==2)ci+=3072;else if(game.mask==4)ci+=6144;
#ifdef CADET_BRUTE
 cell[0]=edge_count;for(uint16_t i=0;i<edge_count;++i)cell[i+1]=i;
#else
 if(ci!=cell_id){uint16_t offset;read(1+(ci>>12),(ci&4095)*2,&offset,2);uint8_t bank=4+(offset>>13);offset&=8191;uint16_t count;read(bank,offset,&count,2);read(bank,offset,cell,(count+1)*2);cell_id=ci;}
#endif
 const int16_t xl=game.x+(dx<0?dx:0)-5,xh=game.x+(dx>0?dx:0)+5,yl=game.y+(dy<0?dy:0)-5,yh=game.y+(dy>0?dy:0)+5;const uint8_t layer=game.mask;
 bound_query[0]=xl;bound_query[1]=xh;bound_query[2]=yl;bound_query[3]=yh;
 bool found=false;hit->t=257;uint8_t circle_count=0;ray_a=0;ray_r2=0;
#ifdef __CX16__
 uint8_t saved=*(volatile uint8_t*)0;
#endif
 for(CandidateIndex i=0;i<cell[0];++i){uint16_t id=cell[i+1];
const Edge*e=bounded_edge(id);if(!e)continue;
  uint8_t mask=e->mask,kind=e->kind,group=e->group;
  if(e->flags&4){if((bool)(e->flags&8)!=(bool)game.lamps[group])continue;}
  else if(!(e->flags&2)&&group!=center_group)continue;
  if(kind==Gate&&rules.gate[group==GROUP_502])continue;
  if(!(mask&layer)||game.disabled[group])continue;
  if(kind==Ramp){bool ignored=false;for(uint8_t k=0;k<ramp_ignore_count;++k)if(ramp_ignored[k]==id)ignored=true;if(ignored)continue;}
  if(group==center_group&&!rules.gravity)continue;
  int16_t t,nx,ny,px,py;
  if(!(e->flags&1)){
   int16_t delta=dot(dx,dy,e->nx,e->ny);if(delta>=0)continue;
   int16_t d0=dot(game.x-e->x,game.y-e->y,e->nx,e->ny);if(d0< -3||d0+delta>0)continue;
   t=d0<=0?0:fraction(d0,-delta);if(t>256||t>hit->t||(t==hit->t&&id>=hit->id))continue;
   px=game.x+mul(dx,t)/256;py=game.y+mul(dy,t)/256;
   if(ax(e->ex-e->x)>=ax(e->ey-e->y)){if(px<e->xlo||px>e->xhi)continue;}else if(py<e->ylo||py>e->yhi)continue;
   nx=e->nx;ny=e->ny;
  }else{
   int16_t axx=ax(game.x-e->x),ayy=ax(game.y-e->y),distance=(axx>ayy?axx+ayy/2:ayy+axx/2)-e->r;
#ifdef PIN_REFERENCE
   if(circle_hit(id,dx,dy,hit))found=true;
#else
   if(circle_count<24){uint8_t at=circle_count++;while(at&&circle_distance[at-1]>distance){circle_ids[at]=circle_ids[at-1];circle_distance[at]=circle_distance[at-1];--at;}circle_ids[at]=id;circle_distance[at]=distance;}
   else if(circle_hit(id,dx,dy,hit))found=true;
#endif
   continue;

  }
  *hit=(Hit){id,t,nx,ny,px,py,(e->flags&1)!=0};found=true;
 }
 // An earlier wall/target hit shortens the sweep for all remaining circles.
 // One extra time quantum and four position units conservatively cover rounding.
 uint16_t clip_t=65535;int16_t cxl=0,cxh=0,cyl=0,cyh=0;
 for(uint8_t i=0;i<circle_count;++i){
#ifndef PIN_REFERENCE
  if(clip_t!=hit->t){clip_t=hit->t;uint16_t t=hit->t<255?hit->t+1:256;int16_t ex=mul(dx,t)/256,ey=mul(dy,t)/256;
   cxl=game.x+(ex<0?ex:0)-5;cxh=game.x+(ex>0?ex:0)+5;cyl=game.y+(ey<0?ey:0)-5;cyh=game.y+(ey>0?ey:0)+5;
   bound_query[0]=cxl;bound_query[1]=cxh;bound_query[2]=cyl;bound_query[3]=cyh;}
  uint16_t id=circle_ids[i];
if(!bounded_edge(id))continue;
#endif
  if(circle_hit(circle_ids[i],dx,dy,hit))found=true;
 }
#ifdef __CX16__
 *(volatile uint8_t*)0=saved;
#endif
 return found;
}
static bool nearest(int16_t dx,int16_t dy,Hit*hit){
#ifdef CADET_PROFILE
 uint32_t before=cycles();
#endif
 bool result=nearest_core(dx,dy,hit);
#ifdef CADET_PROFILE
 cost[0]+=cycles()-before;
#endif
 return result;
}
static uint8_t bumper_index(uint8_t group){uint16_t g=original_groups[group];return g>=405?4+(g-405)/8:(g-372)/8;}
#ifdef __CX16__
__attribute__((section(".physics"),noinline))
#endif
static bool event_core(const Edge*e){
 uint8_t c=e->group;bool fresh=!game.flash[c];touch(c);game.flash[c]=8;game.last_group=c;game.last_kind=e->kind;++game.events;
 uint16_t original=original_groups[c];
 if(e->kind==Ramp){const Meta*m=&metadata[e->param];uint8_t old=game.mask;
  if(m->action==1){game.ramp=true;game.param=e->param;game.mask=m->mask;++game.ramp_entries;if(original==101)mission_ramp();}
  else if(m->action>=2){game.ramp=false;game.mask=m->mask;if(m->zflag)game.z=m->az+77;}
  if(game.mask!=old)++game.layer_changes;return false;}
 if(e->kind==Spinner){
  rules_spin(e);
  return false;
 }
 if(e->kind==Pass||e->kind==Sensor){
  if(e->flags&4){
   if(e->flags&8){game.lamps[c]=0;game.disabled[c]=12;return false;}
   game.lamps[c]=1;fresh=true;
  }
  if(fresh){
   add_score(initial_award[c]);
   if((original>=520&&original<=522)||(original>=528&&original<=530))rules_lane(original);
   if(original==523||original==527){uint8_t side=original==527;if(rules.gate[side]){rules.gate_alert[side]=1;++game.visual_epoch;}}
   game.last_group=c;game.last_kind=e->kind;sound(e->kind==Sensor?SoundLane:6);
  }return false;
 }
 if(e->kind==Drain){drain();return false;}
 if(e->kind==Sink||e->kind==Kickout||e->kind==Hole){rules_capture(e);return false;}
 if(e->kind==Drop){game.disabled[c]=1200;if(fresh){++game.target_hits;add_score(initial_award[c]);sound(2);game.lamps[c]=1;}}
 else if(e->kind==Target&&fresh){++game.target_hits;add_score(initial_award[c]);
  if(original>=454&&original<=464)rules_hazard(original);
  else{
   sound(2);if(original==466)rules_destination(true);
   if(game.rank==1&&game.mission<Practice){
    if(original==452)game.mission=SelectPractice;
    if(original==448)game.mission=SelectLaunch;
    if(original==450)game.mission=NoMission;
   }
  }
 }
 else if(e->kind==Kickback){uint8_t s=c==GROUP_507;if(!rules.kick_phase[s]){rules.kick_phase[s]=1;rules.kick_timer[s]=84;}}
 else if(e->kind==Plunger){game.state=Serving;game.vx=game.vy=0;if(!(game.flags&1)){game.charge=0;game.charge_clock=0;}return true;}
 else if(e->kind!=Bumper&&fresh&&!(c>=GROUP_469&&c<=GROUP_472)){sound(6);}
 return true;
}
/* Callers copy the selected banked edge into unbanked RAM before dispatch.
 * Rules may temporarily select bank61; their wrappers restore our bank62. */
static BANK_TRAMPOLINE bool event(const Edge*e){
#ifdef __CX16__
 uint8_t saved=*(volatile uint8_t*)0;*(volatile uint8_t*)0=62;__asm__ volatile("":::"memory");
#endif
 bool result=event_core(e);
#ifdef __CX16__
 __asm__ volatile("":::"memory");*(volatile uint8_t*)0=saved;
#endif
 return result;
}
static int16_t scaled_step(int16_t v,int16_t remain,uint8_t steps){int16_t q=div60(v);uint32_t n=umul(ax(q),remain);int16_t result=(n>>8)/steps;return q<0?-result:result;}
static void move_time(int16_t dx,int16_t dy,uint8_t steps,uint16_t remaining){ramp_ignore_count=0;
 for(uint8_t guard=0;guard<5&&(dx||dy);++guard){Hit h;if(!nearest(dx,dy,&h)){game.x+=dx;game.y+=dy;return;}Edge copied=*edge(h.id);const Edge*e=&copied;game.x=h.x;game.y=h.y;++game.contacts;
  bool solid=event(e);if(game.state!=InPlay)return;
  remaining=remaining==256?256-h.t:((uint16_t)remaining*(uint16_t)(256-h.t))/256;
  if(!solid){if(e->kind==Ramp){if(ramp_ignore_count<8)ramp_ignored[ramp_ignore_count++]=h.id;}else if(!(e->flags&4))game.disabled[e->group]=2;game.x+=dx>0?1:dx<0?-1:0;game.y+=dy>0?1:dy<0?-1:0;}
  else{
   ramp_ignore_count=0;bool boosted=e->kind==Plunger;
   if(!boosted){uint8_t boost=e->boost;int16_t inward=-dot(game.vx,game.vy,h.nx,h.ny);
    if(inward<e->threshold)boost=0;
    if(e->kind==Bumper){uint8_t b=bumper_index(e->group);if(rules.bumper_fire[b])boost=0;
     if(boost){rules.bumper_fire[b]=12;++game.visual_epoch;++game.bumper_hits;if(b<4&&game.mission==Practice)mission_advance();uint8_t level=rules.bumper_level[b>=4];add_score(b>=4?1500+1000*level:500+500*level);sound(2);}
    }else if(e->kind==Kickback){uint8_t s=e->group==GROUP_507;if(rules.kick_phase[s]!=2||inward<=0)boost=0;else{boost=e->boost;rules.kick_phase[s]=3;}}
    if(e->group>=GROUP_469&&e->group<=GROUP_472){
     if(inward>e->threshold)rules_rebounder(e->group);else if(inward>51)sound(6);
    }
    rebound(h.nx,h.ny,e->elastic,e->smooth,boost,inward);
   }
   game.x+=h.nx/64;game.y+=h.ny/64;
  }
  dx=scaled_step(game.vx,remaining,steps);dy=scaled_step(game.vy,remaining,steps);

  if(guard==4)++game.guard_hits;
 }
}
static void move(int16_t dx,int16_t dy,uint8_t steps){move_time(dx,dy,steps,256);}
static RULE_FN void paddle_core(uint8_t side,uint8_t old){
 if(game.mask!=1||game.state!=InPlay)return;const Vec*p=&pivots[side];const Vec*t=&tips[side][game.phase[side]];
#ifndef PIN_REFERENCE
 // Reject outside the actual capsule before the closest-point division.
 // 158 is conservative: the maximum physical collision radius is 156 Q8.
 if(game.x<(p->x<t->x?p->x:t->x)-158||game.x>(p->x>t->x?p->x:t->x)+158||game.y<(p->y<t->y?p->y:t->y)-158||game.y>(p->y>t->y?p->y:t->y)+158)return;
#endif
 int16_t bx=game.x-p->x,by=game.y-p->y;if(ax(bx)>800||ax(by)>800)return;
 int16_t ux=t->x-p->x,uy=t->y-p->y;
 int32_t projection=mul(bx,ux)+mul(by,uy);int16_t f=projection<=0?0:projection>=flipper_length2?256:fraction_wide(projection,flipper_length2);
 int16_t cx=p->x+mul(ux,f)/256,cy=p->y+mul(uy,f)/256,dx=game.x-cx,dy=game.y-cy;
 int16_t radius=156-((30*f)>>8);uint32_t sq=mul(dx,dx)+mul(dy,dy);if(sq>=(uint32_t)radius*radius)return;
 uint16_t len=isqrt(sq);int16_t nx=len?normal(dx,len):0,ny=len?normal(dy,len):-256;
 game.x=cx+mul(radius+2,nx)/256;game.y=cy+mul(radius+2,ny)/256;
 int16_t phase_delta=(int16_t)game.phase[side]-old;
 uint8_t boost=0,elastic=192;
 if(phase_delta){
  int32_t cross=mul(p->x-t->x,game.y-t->y)-mul(p->y-t->y,game.x-t->x);
  bool front=side==0?cross<=0:cross>0;if(phase_delta<0)front=!front;
  uint16_t distance=isqrt(mul(game.x-p->x,game.x-p->x)+mul(game.y-p->y,game.y-p->y));
  if(distance>157){
   if(front){int16_t fnx=normal(side==0?-uy:uy,flipper_length),fny=normal(side==0?ux:-ux,flipper_length);
    if(phase_delta<0){fnx=-fnx;fny=-fny;}int16_t alignment=dot(fnx,fny,nx,ny);
    if(alignment>0){uint32_t power=umul(ax(phase_delta*flipper_omega[side]),distance)/603;
     power=power*230/256;power=power*alignment/256;boost=power/256;}
   }else elastic=distance>=603?0:(603-distance)*192/603;
  }
 }
 /* The original powered flipper applies its impulse even when the ball is
    stationary or already travelling along the contact normal. A wall-style
    inward<=0 early return incorrectly let the paddle push it without a hit.
    Keep passive contacts unchanged; only the moving, front-face boost enters
    this branch. See TFlipperEdge::EdgeCollision and maths::basic_collision. */
 int16_t inward=-dot(game.vx,game.vy,nx,ny);bool hit;
 if(boost&&inward<=0){
  uint16_t speed=isqrt(mul(game.vx,game.vx)+mul(game.vy,game.vy));
  if(speed&&inward<0){
   uint16_t loss=umul(ax(inward),256-elastic)>>8;
   uint16_t keep=loss<speed?speed-loss:0;
   uint16_t scale=fraction_wide(keep,speed);
   game.vx=mul(game.vx,scale)/256;game.vy=mul(game.vy,scale)/256;
  }
  game.vx+=mul(nx,boost);game.vy+=mul(ny,boost);limit();hit=true;
 }else hit=rebound(nx,ny,elastic,128,boost,inward)>0;
 if(hit)++game.flipper_hits;

}
#include "flipper_sweep.h"
static BANK_TRAMPOLINE void paddle(uint8_t side,uint8_t old){RULE_ENTER;paddle_core(side,old);RULE_LEAVE;}
static bool well_force(){
 for(uint8_t wi=0;wi<sizeof(wells)/sizeof(wells[0]);++wi){const Well*w=&wells[wi];
  if(!(game.mask&w->mask)||game.disabled[w->group]||(w->group==center_group&&!rules.gravity))continue;
  int16_t dx=w->x-game.x,dy=w->y-game.y;if(ax(dx)>w->r||ax(dy)>w->r)continue;
  uint32_t sq=mul(dx,dx)+mul(dy,dy);if(sq>=(uint32_t)w->r*w->r)continue;
  uint16_t d=isqrt(sq);
  if(d<=w->capture){Edge obj={0};Edge*e=&obj;e->kind=w->kind;e->group=w->group;e->param=w->param;game.x=w->x;game.y=w->y;event(e);return true;}
  game.fx=(int32_t)dx*w->force/d-game.vx;game.fy=(int32_t)dy*w->force/d-game.vy;return true;
 }
 return false;
}
/* 3D Pinball accepts plunger input regardless of ball location. Only a
 * ball already resting at the plunger receives the existing launch impulse. */
static bool plunger_input(bool pull){
 bool serving=game.state==Serving;
 if(pull){
  if(!(game.flags&1)){game.flags|=1;game.charge=1;game.charge_clock=0;game.last_group=GROUP_473;game.last_kind=Plunger;sound(4);}
  else{game.charge_clock+=2;if(game.charge_clock>=3){game.charge_clock-=3;if(game.charge<99)game.charge+=2;else game.charge=100;}}
 }else if(game.flags&1){
  game.flags&=~1;
  if(serving){game.state=InPlay;game.vy=-(int16_t)(game.charge>60?60:game.charge)*256;}
  game.last_group=GROUP_473;game.last_kind=Plunger;sound(3);
 }
 return serving;
}
__attribute__((noinline)) static void tick(bool left,bool right,bool pull,bool nudge){
 rules_tick();if(game.state==Ready){if(!game.wait)serve();return;}
 game.tick+=2;for(uint8_t k=0;k<active_count;){uint8_t i=active[k];if(game.flash[i])game.flash[i]=game.flash[i]>2?game.flash[i]-2:0;if(game.disabled[i])game.disabled[i]=game.disabled[i]>2?game.disabled[i]-2:0;if(!game.flash[i]&&!game.disabled[i]){active_flags[i]=0;active[k]=active[--active_count];}else ++k;}if(game.ignore)game.ignore=game.ignore>2?game.ignore-2:0;
 bool keys[2]={left,right};uint8_t old[2],pressed=(left?1:0)|(right?2:0);
 for(uint8_t i=0;i<2;++i){old[i]=game.phase[i];uint8_t key=1u<<i;
  if((pressed^game.flipper_keys)&key){if(pressed&key){rules_shift(i);sound(0);}else sound(1);}
  if(keys[i]){if(game.phase[i]<120)game.phase[i]=game.phase[i]>70?120:game.phase[i]+50;}
  else if(game.phase[i])game.phase[i]=game.phase[i]<25?0:game.phase[i]-25;
 }
 game.flipper_keys=pressed;
 if(plunger_input(pull))return;
 if(game.state==Between){if(game.wait){game.wait=game.wait>2?game.wait-2:0;}if(!game.wait){if(game.balls)serve();else game.state=GameOver;}return;}
 if(game.state==Captured){if(game.wait){game.wait=game.wait>2?game.wait-2:0;}if(!game.wait)rules_release();return;}

 if(game.state!=InPlay)return;
 if(nudge&&!game.ignore){game.vx+=(game.nudges&1)?768:-768;game.vy-=1536;game.ignore=60;++game.nudges;}
 bool well=well_force();if(game.state!=InPlay)return;
 int16_t fx=well?game.fx:game.ramp?metadata[game.param].fx:0,fy=well?game.fy:game.ramp?metadata[game.param].fy:3068;
 game.accx+=fx;game.accy+=fy;int16_t dvx=div60(game.accx),dvy=div60(game.accy);game.vx+=dvx-div300(game.vx);game.vy+=dvy-div300(game.vy);game.accx-=dvx*60;game.accy-=dvy*60;limit();
 game.remx+=game.vx;game.remy+=game.vy;int16_t dx=div60(game.remx),dy=div60(game.remy);game.remx-=dx*60;game.remy-=dy*60;
 if(game.y>1800&&game.mask==1){
  uint8_t final[2]={game.phase[0],game.phase[1]};for(uint8_t i=0;i<2;++i)game.phase[i]=(old[i]+final[i])/2;
  int16_t before_vx=game.vx,before_vy=game.vy;
  int16_t sx=game.x,sy=game.y;uint16_t contacts=game.contacts;
  move(dx/2,dy/2,2);
  if(game.contacts==contacts){if(!paddle_static_tip(0,old[0],sx,sy,2))paddle_static_tip(1,old[1],sx,sy,2);}
  paddle(0,old[0]);paddle(1,old[1]);
  old[0]=game.phase[0];old[1]=game.phase[1];game.phase[0]=final[0];game.phase[1]=final[1];
  if(game.state==InPlay){sx=game.x;sy=game.y;contacts=game.contacts;
   move(game.vx==before_vx?dx-dx/2:div120(game.vx),game.vy==before_vy?dy-dy/2:div120(game.vy),2);
   if(game.contacts==contacts){if(!paddle_static_tip(0,old[0],sx,sy,2))paddle_static_tip(1,old[1],sx,sy,2);}
   paddle(0,old[0]);paddle(1,old[1]);}
 }else move(dx,dy,1);
 if(game.ramp){const Meta*m=&metadata[game.param];game.z=dot(game.x,game.y,m->ax,m->ay)+m->az+77;}
 if(game.x< -3072||game.x>3072||game.y>3900||game.y< -4352){++game.escapes;drain();}
}
__attribute__((noinline)) void game_frame(bool l,bool r,bool p,bool n){
#ifdef __CX16__
 uint8_t saved=*(volatile uint8_t*)0;
#endif
 tick(l,r,p,n);
#ifdef __CX16__
 __asm__ volatile("":::"memory");*(volatile uint8_t*)0=saved;
#endif
}
void game_place(int16_t x,int16_t y,int16_t vx,int16_t vy,uint8_t mask){game.state=InPlay;game.x=x;game.y=y;game.vx=vx;game.vy=vy;game.mask=mask;game.ramp=false;game.ignore=0;game.remx=game.remy=0;}
