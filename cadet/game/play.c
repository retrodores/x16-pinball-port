/* Original-table integration. Physics, graphics and audio stay independently testable. */
#include "engine.h"
#include "sprites.h"
#include "audio.h"
#include "audio_events.h"
#include "ui.h"
#include "projection.h"
#ifdef MILESTONE_INPUT
#include "verify_milestone_input.h"
#endif
#include "dynamic.h"
#if !defined(GAME_TEST)||defined(ATTRACT_TEST)
#include "attract.h"
#endif
extern int32_t signedmul(int16_t,int16_t);
extern uint16_t fastsqrt(uint32_t),depth_mask(int16_t,int16_t,uint8_t);
extern uint8_t depth_quant(uint32_t);
extern void mask_pixels(uint16_t);
extern void depth_masks(uint16_t,uint16_t,uint8_t,uint16_t*,uint8_t,uint8_t);
extern uint32_t fastmul16(uint16_t,uint16_t);
static int16_t projected(int16_t value,uint16_t scale){uint32_t p=fastmul16(value<0?-value:value,scale);return value<0?-(int16_t)(p>>12):(int16_t)(p>>12);}
#include <cbm.h>
#include <stdint.h>
extern void music_prefetch(void);
extern void lab_install(void),lab_uninstall(void),pcm_start(uint16_t),pcm_flipper_start(uint16_t),pcm_plunger_start(uint16_t),pcm_stop(void),music_start(void),music_stop(void);
extern uint16_t lab_clock(void);
extern volatile uint8_t pcm_select_bank,music_enabled,music_error,music_loops;
extern volatile uint16_t pcm_select_ptr,pcm_remaining,pcm_underruns;
extern volatile uint32_t irq_max,irq_start;
__attribute__((used)) volatile uint8_t keys[128];
__attribute__((used)) volatile uint8_t new_game_request,quit_request;
__attribute__((naked,used)) void keyboard(void){__asm__ volatile(
 "phx\npha\nand #127\ntax\npla\nbmi 1f\n"
 "cpx #17\nbeq 4f\ncpx #110\nbne 5f\n"
 "4: lda #1\nsta quit_request\nbra 3f\n"
 "5: cpx #113\nbne 3f\nlda keys,x\nbne 3f\ninc new_game_request\n"
 "3: lda #1\nbra 2f\n1: lda #0\n2: sta keys,x\nplx\nlda #0\nrts");}
static volatile uint8_t *const v=(volatile uint8_t*)0x9f20;
static uint8_t priority,mechanical_sample,previous_state=255,phase_cache[2]={255,255},plunger_cache=255;
static uint8_t score_cache[9],ball_cache=255;
static bool wide_score;
static void addr(uint32_t a){v[5]=0;v[0]=a;v[1]=a>>8;v[2]=0x10|(a>>16);}
static void word(uint16_t a){v[3]=a;v[3]=a>>8;}
static void hide(uint8_t n){addr(0x1fc06UL+(uint16_t)n*8);v[3]=0;}
static void tile(uint8_t n,uint16_t a,int16_t x,int16_t y,uint8_t size){addr(0x1fc00UL+(uint16_t)n*8);word(a);word(x);word(y);v[3]=12;v[3]=size;}
#ifdef CHRISTMAS
#include "christmas_lamps.h"
#endif
static void frame(uint8_t n,uint8_t f,int16_t x,int16_t y,uint8_t reserved){
 const SpriteFrame*s=&sprites[f];
 for(uint8_t i=0;i<reserved;++i){
  if(i<s->count){const SpriteTile*t=s->tiles+i;tile(n+i,t->address,x+t->x,y+t->y,t->size|t->palette);}else hide(n+i);
 }
}
static uint8_t load(const char*n,uint8_t mode,uint16_t a){cbm_k_setnam(n);cbm_k_setlfs(1,8,2);return(uintptr_t)cbm_k_load(mode,(void*)a)>255;}
#ifdef COVER_AUDIO
#include "music_cover_data.h"
extern volatile uint16_t cover_triggers;
#endif
/* KERNAL MEMTOP returns the usable 8 KB bank count in A. Zero means 256. */
static uint8_t ram_banks(void){
 uint8_t banks;
 __asm__ volatile("sec\njsr $ff99":"=a"(banks)::"x","y","p","memory");
 return banks;
}
static void print(const char*s){while(*s)cbm_k_bsout(*s++);}
static void echo(const char*s){while(*s)*(volatile uint8_t*)0x9fbb=*s++;}
static void hex(uint32_t a){for(uint8_t i=0;i<8;++i){*(volatile uint8_t*)0x9fbb="0123456789abcdef"[a>>28];a<<=4;}}
static uint32_t cycles(void){uint8_t a=*(volatile uint8_t*)0x9fb8,b=*(volatile uint8_t*)0x9fb9,c=*(volatile uint8_t*)0x9fba,d=*(volatile uint8_t*)0x9fbb;return(uint32_t)a|((uint32_t)b<<8)|((uint32_t)c<<16)|((uint32_t)d<<24);}
#ifndef GAME_TEST
/* The opening sample borrows the first gameplay PCM banks. Restore
 * their assets before any ball feed or gameplay effect can run. */
static __attribute__((noinline)) bool startup_pcm(bool opening){
 uint8_t saved=*(volatile uint8_t*)0;
 pcm_stop();
#ifdef COVER_AUDIO
 /* Keep the mixer FIFO from draining during the bank load. */
 uint8_t rate=v[28];v[28]=0;
#endif
 *(volatile uint8_t*)0=19;
 bool ok=load(opening?"STARTFX.BIN":"PCM0.BIN",0,0xa000);
 *(volatile uint8_t*)0=saved;
#ifdef COVER_AUDIO
 v[28]=rate;
#endif
 return ok;
}
#endif
static void effect(uint8_t id,uint8_t rank,uint8_t voice){
 if(id==255)return;
 if(!voice){
  uint16_t remaining;__asm__ volatile("php\nsei":::"memory");remaining=pcm_remaining;__asm__ volatile("plp":::"memory");
  /* Let the spinner click reach its transient on the single mechanical
   * voice. Closely spaced steps otherwise keep replaying its quiet lead-in. */
  if(remaining&&(rank<priority||(id==SOUND131&&mechanical_sample==SOUND131)))return;
 }
 const Effect*e=effects+id;pcm_select_bank=e->bank;pcm_select_ptr=e->ptr;
 if(voice==1)pcm_flipper_start(e->length);
 else if(voice==2)pcm_plunger_start(e->length);
 else{priority=rank;mechanical_sample=id;pcm_start(e->length);}
}
void audio_stop(void){pcm_stop();priority=0;}
void audio_effect(uint8_t id){
 if(id==SoundStartup){
  mechanical_sample=255;
  pcm_select_bank=19;pcm_select_ptr=0xa000;
  pcm_start(55539);return;
 }
 uint8_t saved=*(volatile uint8_t*)0;
 *(volatile uint8_t*)0=11;__asm__ volatile("":::"memory");
 uint16_t e=audio_event_sample(id,game.last_group,game.last_kind,game.sound_value);
 __asm__ volatile("":::"memory");*(volatile uint8_t*)0=saved;
 uint8_t voice=id<=1?1:(id==3||id==4||id==16)?2:0;
 effect((uint8_t)e,(uint8_t)(e>>8),voice);
}

#include "message_display.h"
#ifdef PROFILE_DISPLAY
static uint32_t mask_cycles,copy_cycles,prefetch_cycles;
#endif
static void ball(uint8_t f,int16_t x,int16_t y,uint32_t distance_squared){
 const SpriteTile*t=sprites[24+f].tiles;
 uint16_t masks[16]={0},all=65535,any=0;
 uint8_t width=sprites[24+f].width,height=sprites[24+f].height;
 uint8_t depth=depth_quant(distance_squared);
#ifdef PROFILE_DISPLAY
 uint32_t mask_start=cycles();mask_cycles=copy_cycles=0;
#endif
 if(x>=8&&x<=357&&y>=5&&y<=459)depth_masks(x-8,y-5,depth,masks,sprites[24+f].width,sprites[24+f].height);
 else for(uint8_t row=0;row<height;++row)masks[row]=depth_mask(x-8,y-5+row,depth);
 for(uint8_t row=0;row<height;++row){all&=masks[row];any|=masks[row];}
#ifdef PROFILE_DISPLAY
 mask_cycles=cycles()-mask_start;
#endif
 if((all&((1u<<width)-1))==((1u<<width)-1)){frame(0,24+f,x,y,1);return;}
 if(!any){hide(0);return;}
#ifdef PROFILE_DISPLAY
 uint32_t copy_start=cycles();
#endif
 uint32_t src=(uint32_t)t->address<<5;
 v[5]=1;v[0]=src;v[1]=src>>8;v[2]=0x10|(src>>16);v[5]=0;
 addr(FONT_BASE+2048);
 mask_pixels((uint16_t)(uintptr_t)masks);
 tile(0,(FONT_BASE+2048)/32,x,y,0x50|t->palette);
#ifdef PROFILE_DISPLAY
 copy_cycles=cycles()-copy_start;
#endif
}
static __attribute__((section(".rules"),noinline)) void update_status_banked(void){
 uint8_t panel_state=game.state;
 uint8_t upper=game.tilted?4:1+game.upper_notice;
#if !defined(GAME_TEST)||defined(ATTRACT_TEST)
 if(attract_caption)panel_state=5+attract_caption;
#endif
 if(game.state==Ready&&game.wait>StartupReadyFrames){panel_state=126;upper=0;}
 if((game.state==InPlay||game.state==Captured)&&game.mission)panel_state=128+9*game.mission+game.mission_left;
 if(wide_score)panel_state=254;
 if(previous_state!=panel_state||upper_status!=upper){
  static const char*const labels[]={
   "",
   "Ready to\nlaunch",
   "In play",
   "Ball held\nReturn soon",
   "Next ball",
   "Game over\nF2 for\nnew game",
  };
  if(wide_score)status("Long score\nView exact\nscore log",0,upper);
  else if(panel_state>=128){
   switch(game.mission){
    case SelectPractice:status("Launch ramp\nTo accept\nTarget practice",0,upper);break;
    case SelectLaunch:status("Launch ramp\nTo accept\nLaunch training",0,upper);break;
    case Practice:status("Attack\nbumpers\nLeft: #",'0'+game.mission_left,upper);break;
    case LaunchTraining:status("Launch ramp\nLeft: #",'0'+game.mission_left,upper);break;
   }
  }
#if !defined(GAME_TEST)||defined(ATTRACT_TEST)
  else if(attract_caption){
   status(attract_caption==DemoFinalScore?
    "Demo\nFinal score\nF2 to play":"Demo\nHit mission\ntargets",0,upper);
  }
#endif
  else status(labels[game.state],0,upper);
  previous_state=panel_state;
 }
}
static void update_status(void){
 uint8_t saved=*(volatile uint8_t*)0;
 font_bank(61);
 update_status_banked();
 font_bank(saved);
}
static void display(bool update_panel){
 /* Camera matrix from PINBALL.DAT, Q8. Products retain 16 fractional bits. */
 int16_t depth=6317-(signedmul(game.y,104)+signedmul(game.z,234))/256;
 int16_t camera_y=(signedmul(game.y,-234)+signedmul(game.z,104))/256+971;
 if(depth<2048)depth=2048;if(depth>10232)depth=10232;
 uint16_t scale=projection_scale[(depth-2048+4)>>3];
 int16_t x=191-projected(game.x,scale),y=243-projected(camera_y,scale);
 uint32_t distance_squared=signedmul(game.x,game.x)+signedmul(camera_y,camera_y)+signedmul(depth,depth);
 uint8_t f=0;while(f<6&&ball_depth_squared[f]>distance_squared)++f;
 const SpriteFrame*b=sprites+24+f;
 if(game.state==Serving||game.state==InPlay||(game.state==Captured&&game.captured==Kickout))ball(f,x-b->width/2,y-b->height/2,distance_squared);else hide(0);
 for(uint8_t i=0;i<2;++i){uint8_t pose=phase_pose[game.phase[i]];
  if(pose!=phase_cache[i]){f=i*8+pose;frame(1+i*9,f,sprites[f].x,sprites[f].y,9);phase_cache[i]=pose;}
 }
 uint8_t pose=(game.flags&1)?charge_pose[game.charge]:0;
 if(pose!=plunger_cache){f=16+pose;frame(19,f,sprites[f].x,sprites[f].y,3);plunger_cache=pose;}
 if(game.score_dirty&&update_panel){uint8_t hi=39;while(hi&&!game.digits[hi])--hi;
  for(uint8_t i=0;i<9;++i){uint8_t digit=i<=hi?game.digits[i]:255;if(digit==score_cache[i])continue;score_cache[i]=digit;
   if(digit==255){hide(22+i);}else frame(22+i,31+digit,553-i*15,197,1);
  }
  wide_score=hi>=9;
  if(hi>=9){echo("# EXACT SCORE ");for(int8_t i=hi;i>=0;--i)*(volatile uint8_t*)0x9fbb=48+game.digits[i];echo("\n");}
  game.score_dirty=false;
 }
 uint8_t number=game.ball_number;if(update_panel&&number!=ball_cache){frame(32,31+number,553,152,1);ball_cache=number;}
 if(update_panel)update_status();
 dynamic_update(update_panel?(game.state==Ready?240:128):0);
 if(update_panel)message_step();
#ifdef CHRISTMAS
 if(update_panel){
  uint8_t saved=*(volatile uint8_t*)0;
  *(volatile uint8_t*)0=64;
  christmas_lamps();
  *(volatile uint8_t*)0=saved;
 }
#endif
}
static __attribute__((section(".mechanics"),noinline)) void compact_footer(void){
 /* The supported maps use private tiles in this part of row 25. The
  * shared blank tiles already have zero in the rows we erase. */
 for(uint8_t col=24;col<37;++col){
  addr(25u*128+col*2);
  uint8_t lo=v[3],hi=v[3];
  uint16_t tile_index=lo|((uint16_t)(hi&3)<<8);
  uint32_t pattern=4096UL+(uint32_t)tile_index*128;
  addr(pattern+((hi&8)?0:48));
  for(uint8_t i=0;i<80;++i)v[3]=0;
 }
 addr(29u*128+39*2);uint8_t lo=v[3],hi=v[3];
 for(uint8_t row=26;row<30;++row){
  addr((uint16_t)row*128+48);
  for(uint8_t col=0;col<13;++col){v[3]=lo;v[3]=hi;}
 }
}
static void restore_keyboard(uint16_t vector){
 __asm__ volatile("php\nsei":::"memory");
 *(volatile uint16_t*)0x032e=vector;
 __asm__ volatile("plp":::"memory");
}

static void restore_console(uint8_t bank){
 *(volatile uint8_t*)0=bank;
 cbm_k_clrch();
 /* Reload the BASIC palette, charset and screen mode and clear game input. */
 __asm__ volatile("jsr $ff81":::"a","x","y","p","memory");
 *(volatile uint8_t*)0=bank;
}

int main(void){
 uint8_t oldbank=*(volatile uint8_t*)0;uint16_t oldkey=*(volatile uint16_t*)0x032e;
 uint8_t banks=ram_banks();
#ifdef COVER_AUDIO
 if(banks){
  print("\rPINBALL NEEDS 2 MB OF BANKED RAM.\rTRY THE 512 KB EDITION INSTEAD.\r");
#else
 if(banks&&banks<64){
  print("\rPINBALL NEEDS 512 KB OF BANKED RAM.\r");
#endif
  return 1;
 }
#ifdef CHRISTMAS
 print("\x93" "SPACE CMDRX16 CHRISTMAS EDITION\rLOADING...\r");
#else
 print("\x93" "CMDRX CADET - ORIGINAL TABLE\rLOADING...\r");
#endif
 v[5]=0;v[9]=1;
 if(!game_load()||!load("MAP.BIN",2,0)||!load("TILES.BIN",2,0x1000)||!load("PAL.BIN",3,0xfa00)||
 !load("SPRITES.BIN",3,SPRITE_BASE&65535)||!load("FONT.BIN",3,FONT_BASE&65535))goto fail;
 /* Clear the spill below the cabinet using the existing blank map tile. */
 addr(29u*128+39*2);uint8_t blank_lo=v[3],blank_hi=v[3];
 for(uint8_t row=27;row<30;++row){
  addr((uint16_t)row*128);
  for(uint8_t col=0;col<24;++col){v[3]=blank_lo;v[3]=blank_hi;}
 }
#ifdef COVER_AUDIO
 *(volatile uint8_t*)0=32;if(!load("COVER.CMD",0,0xa000))goto fail;
#ifdef CHRISTMAS
 *(volatile uint8_t*)0=64;if(!load("COVER.XMS",0,0xa000))goto fail;
#else
 *(volatile uint8_t*)0=64;if(!load("COVER.PCM",0,0xa000))goto fail;
 *(volatile uint8_t*)0=COVER_CMD_HIGH;if(!load("COVER.HI",0,0xa000))goto fail;
#endif
#else
 for(uint8_t i=0;i<2;++i){char n[]="MUSIC0.BIN";n[5]+=i;*(volatile uint8_t*)0=32+i*8;if(!load(n,0,0xa000))goto fail;}
#endif
 for(uint8_t i=0;i<PCM_PARTS;++i){char n[]="PCM0.BIN";n[3]+=i;*(volatile uint8_t*)0=pcm_load_banks[i];if(!load(n,0,0xa000))goto fail;}
 for(uint8_t i=0;i<9;++i){char n[]="DEPTH00.BIN";n[6]+=i;*(volatile uint8_t*)0=i==0?10:i<3?16+i:i+42;if(!load(n,0,0xa000))goto fail;}
 *(volatile uint8_t*)0=57;if(!load("MSGFONT.BIN",0,0xa400))goto fail;
 *(volatile uint8_t*)0=31;if(!load("RINGS.BIN",0,0xb000))goto fail;
 *(volatile uint8_t*)0=11;if(!load("RINGS2.BIN",0,DYNAMIC_OVERFLOW_ADDRESS))goto fail;
 for(uint8_t i=0;i<DYNAMIC_BANK_COUNT;++i){char n[]="DYN0.BIN";n[3]+=i;*(volatile uint8_t*)0=dynamic_load_banks[i];if(!load(n,0,0xa000))goto fail;}
 *(volatile uint8_t*)0=11;if(!load("UI.BIN",0,0xa000))goto fail;
 for(uint8_t i=0;i<128;++i)hide(i);
 for(uint8_t i=0;i<9;++i)score_cache[i]=254;
 *(volatile uint8_t*)0=10;
 __asm__ volatile("":::"memory");
 compact_footer();
 __asm__ volatile("":::"memory");
 *(volatile uint8_t*)0=11;
 /* Fill the 640x480 signal with the playable viewport. Keep the backbox
  * entirely visible while reducing the empty strip below the cabinet. */
 v[5]=0;v[10]=119;v[11]=117;v[12]=0;
 v[13]=0x12;v[14]=0;v[15]=0x0b;v[16]=v[17]=v[18]=v[19]=0;
#ifndef GAME_TEST
 if(!startup_pcm(true))goto fail;
#endif
 restore_keyboard((uint16_t)(uintptr_t)keyboard);
 lab_install();
#ifdef GAME_TEST
 game_start();
#else
 game_begin(true);
#endif
 dynamic_init();
#ifdef CHRISTMAS
 *(volatile uint8_t*)0=64;christmas_init();*(volatile uint8_t*)0=11;
#endif
 frame(31,32,403,197,1);display(true);v[9]=0x51;
#ifndef NO_MUSIC
 music_start();
#endif

 uint16_t last=lab_clock(),count=0,gaps=0,over=0;uint32_t maximum=0,total=0;
#ifndef GAME_TEST
 uint8_t old_m=0;
 bool opening_pending=false;
#endif
 echo("# PLAY READY\n");
#ifdef GAME_TEST
 *(volatile uint8_t*)0x9fb8=0;
#endif
 for(;;){
  uint16_t now=lab_clock();if(now==last)continue;if((uint16_t)(now-last)>1)++gaps;last=now;
  uint32_t before=irq_start;
#if defined(ATTRACT_TEST)
  uint8_t buttons=attract_input(count?0:DemoToggle,now);
  if(buttons&DemoReset){game_start();previous_state=255;}
  game_frame(buttons&DemoLeft,buttons&DemoRight,buttons&DemoLaunch,false);
#elif defined(GAME_TEST)
#ifdef MILESTONE_INPUT
  if(count>=MILESTONE_FIRST_TICK){
   volatile uint8_t *const ram_bank=(volatile uint8_t*)0;
   uint8_t saved=*ram_bank;
   *ram_bank=62;__asm__ volatile("":::"memory");
   milestone_setup(count);
   __asm__ volatile("":::"memory");*ram_bank=saved;
  }
  /* Measured restart and cancellation while the music buffer is priming. */
  if(count==6100||count==6500||count==6502)music_stop();
  if(count==6101||count==6501||count==6503)music_start();
#endif
  game_frame(count%43<12,count%67<14,game.state==Serving&&game.charge<80,false);
  if(game.state==GameOver)game_start();
#else
  if(quit_request)break;
  if(keys[52]&&!old_m){if(music_enabled)music_stop();else music_start();}
  old_m=keys[52];
  __asm__ volatile("php\nsei":::"memory");
  uint8_t new_game=new_game_request;new_game_request=0;
  __asm__ volatile("plp":::"memory");
  uint8_t buttons=(keys[44]||keys[46]?DemoLeft:0)|(keys[55]||keys[57]?DemoRight:0)|
    (keys[61]?DemoLaunch:0)|(keys[83]?DemoNudge:0)|(keys[114]?DemoToggle:0)|
    (new_game?DemoNew:0);
  buttons=attract_input(buttons,now);
  if(buttons&DemoReset){
#ifdef CHRISTMAS
   if(new_game&&music_enabled)music_start();
#endif
   bool show=game.state!=Ready&&!attract_caption&&!(buttons&15);
   previous_state=255;
   if(show){
    game_begin(true);
    /* Acknowledge the reset with the first lamp phase and clear the
     * previous ball and messages before the blocking PCM bank load. */
    hide(0);update_status();dynamic_update(96);
    /* Let VERA finish a frame before the KERNAL can block on storage. */
    opening_pending=true;
    continue;
   }else{
    if(game.state==Ready&&!opening_pending&&!startup_pcm(false))goto audio_load_failed;
    opening_pending=false;
    game_start();
   }
  }
  if(opening_pending){
   if(!startup_pcm(true))goto audio_load_failed;
   opening_pending=false;
  }
  if(game.state==Ready&&game.wait==1&&!startup_pcm(false))goto audio_load_failed;
  game_frame(buttons&DemoLeft,buttons&DemoRight,buttons&DemoLaunch,buttons&DemoNudge);
#endif

#if defined(PROFILE_DISPLAY) || defined(PROFILE_ATTRACT)
  uint32_t physics_end=cycles();
#endif
  display(cycles()-before<80000UL);++count;
#ifdef PROFILE_DISPLAY
  uint32_t prefetch_start=cycles();
#endif
  if(cycles()-before<100000UL)music_prefetch();
#ifdef PROFILE_DISPLAY
  prefetch_cycles=cycles()-prefetch_start;
#endif
  uint32_t elapsed=cycles()-before;total+=elapsed;

#ifdef PROFILE_DISPLAY
  if(elapsed>120000){echo("# COST ");hex(count);echo(" ");hex(physics_end-before);echo(" ");hex(cycles()-physics_end);echo(" ");hex(game.x);echo(" ");hex(game.y);echo(" ");hex(mask_cycles);echo(" ");hex(copy_cycles);echo(" ");hex(prefetch_cycles);echo("\n");}
#endif
  if(elapsed>maximum){maximum=elapsed;echo("# WORST ");hex(count);echo(" ");hex(elapsed);
#ifdef PROFILE_ATTRACT
   echo(" ");hex(physics_end-before);
#endif
   echo("\n");}
  if(elapsed>133333)++over;
#ifdef GAME_TEST
#ifndef TEST_FRAMES
#define TEST_FRAMES 6000
#endif
  if(count>=TEST_FRAMES)break;
#ifdef ATTRACT_TEST
  if(game.state==GameOver)break;
#endif
#endif
 }
#ifdef ATTRACT_TEST
 echo("# DEMO ");hex(game.state);echo(" ");hex(game.drains);echo(" ");hex(game.flipper_hits);echo(" ");hex(game.escapes);echo("\n");
#endif
#ifdef COVER_AUDIO
 echo("# COVER LOOPS ");hex(music_loops);echo(" TRIGGERS ");hex(cover_triggers);echo("\n");
#endif
 echo("# RESULT ");hex(count);echo(" ");hex(maximum);echo(" ");hex(count?total/count:0);echo(" ");hex(over);echo(" ");hex(gaps);echo(" ");hex(irq_max);echo(" ");hex(music_error);echo("\n# PCM UNDERRUNS ");hex(pcm_underruns);echo("\n# DONE\n");
 lab_uninstall();restore_keyboard(oldkey);
 *(volatile uint8_t*)0=oldbank;
#ifdef GAME_TEST
 *(volatile uint8_t*)0x9fb4=0;__asm__ volatile("jmp $ffff");
#endif
 restore_console(oldbank);return 0;
#ifndef GAME_TEST
audio_load_failed:
 lab_uninstall();restore_keyboard(oldkey);
#endif
fail:restore_console(oldbank);print("ASSET LOAD FAILED\r");echo("# LOAD FAILED\n");return 1;
}
