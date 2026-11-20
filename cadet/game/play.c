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
__attribute__((naked,used)) void keyboard(void){__asm__ volatile(
 "phx\npha\nand #127\ntax\npla\nbmi 1f\nlda #1\nbra 2f\n1: lda #0\n2: sta keys,x\nplx\nlda #0\nrts");}
static volatile uint8_t *const v=(volatile uint8_t*)0x9f20;
static uint8_t priority,previous_state=255,phase_cache[2]={255,255},plunger_cache=255;
static uint8_t score_cache[9],ball_cache=255,status_cache[40];
static bool wide_score;
static uint8_t music_cache=255;
static void addr(uint32_t a){v[5]=0;v[0]=a;v[1]=a>>8;v[2]=0x10|(a>>16);}
static void word(uint16_t a){v[3]=a;v[3]=a>>8;}
static void hide(uint8_t n){addr(0x1fc06UL+(uint16_t)n*8);v[3]=0;}
static void tile(uint8_t n,uint16_t a,int16_t x,int16_t y,uint8_t size){addr(0x1fc00UL+(uint16_t)n*8);word(a);word(x);word(y);v[3]=12;v[3]=size;}
static void frame(uint8_t n,uint8_t f,int16_t x,int16_t y,uint8_t reserved){
 const SpriteFrame*s=&sprites[f];
 for(uint8_t i=0;i<reserved;++i){
  if(i<s->count){const SpriteTile*t=s->tiles+i;tile(n+i,t->address,x+t->x,y+t->y,t->size|t->palette);}else hide(n+i);
 }
}
static uint8_t load(const char*n,uint8_t mode,uint16_t a){cbm_k_setnam(n);cbm_k_setlfs(1,8,2);return(uintptr_t)cbm_k_load(mode,(void*)a)>255;}
static void print(const char*s){while(*s)cbm_k_bsout(*s++);}
static void echo(const char*s){while(*s)*(volatile uint8_t*)0x9fbb=*s++;}
static void hex(uint32_t a){for(uint8_t i=0;i<8;++i){*(volatile uint8_t*)0x9fbb="0123456789abcdef"[a>>28];a<<=4;}}
static uint32_t cycles(void){uint8_t a=*(volatile uint8_t*)0x9fb8,b=*(volatile uint8_t*)0x9fb9,c=*(volatile uint8_t*)0x9fba,d=*(volatile uint8_t*)0x9fbb;return(uint32_t)a|((uint32_t)b<<8)|((uint32_t)c<<16)|((uint32_t)d<<24);}
static void effect(uint8_t id,uint8_t rank,uint8_t voice){
 if(id==255)return;
 if(!voice){
  uint16_t remaining;__asm__ volatile("php\nsei":::"memory");remaining=pcm_remaining;__asm__ volatile("plp":::"memory");
  if(remaining&&rank<priority)return;
 }
 const Effect*e=effects+id;pcm_select_bank=e->bank;pcm_select_ptr=e->ptr;
 if(voice==1)pcm_flipper_start(e->length);
 else if(voice==2)pcm_plunger_start(e->length);
 else{priority=rank;pcm_start(e->length);}
}
void audio_stop(void){pcm_stop();priority=0;}
void audio_effect(uint8_t id){
 uint16_t e=audio_event_sample(id,game.last_group,game.last_kind,game.sound_value);
 uint8_t voice=id<=1?1:(id==3||id==4||id==16)?2:0;
 effect((uint8_t)e,(uint8_t)(e>>8),voice);
}

static void status(const char*s){
 for(uint8_t i=0;i<40;++i){uint8_t c=*s?*s++:32;if(status_cache[i]==c)continue;status_cache[i]=c;
  tile(33+i,FONT_BASE/32+c-32,405+(i%20)*8,248+(i/20)*12,FONT_STATUS_BANK);
 }
}
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
 if(update_panel&&previous_state!=game.state){
  static const char*const labels[]={"F2: NEW GAME","HOLD SPACE          " "RELEASE TO LAUNCH","BALL IN PLAY","CAPTURE / RETURN","NEXT BALL","GAME OVER           F2: NEW GAME"};
  status(labels[game.state]);previous_state=game.state;
 }
 if(update_panel&&music_cache!=music_enabled){
  const char*label=music_enabled==0?"OFF":music_enabled==1?"ON ":"...";
  for(uint8_t i=0;i<3;++i)tile(73+i,FONT_BASE/32+label[i]-32,533+i*8,372,FONT_STATUS_BANK);
  music_cache=music_enabled;
 }
 dynamic_update(update_panel?128:0);
 /* 128-bit score remains exact. Flag a panel overflow instead of silently truncating. */
 if(update_panel&&wide_score)status("SCORE EXCEEDS PANEL  SEE EXACT SCORE LOG");
}
static void compact_footer(void){
 /* Row 25 contains the bottom of the backbox frame and the first line of
  * old footer text. Copy its 13 right-side tiles, blanking only y >= 406.
  * These replacement patterns occupy the gap after the fast dynamic tiles. */
 const uint16_t first=960;
 for(uint8_t col=0;col<13;++col){
  uint16_t cell=25u*128+(24+col)*2;
  addr(cell);uint8_t lo=v[3],hi=v[3];
  uint16_t tile_index=lo|((uint16_t)(hi&3)<<8);
  uint32_t source=4096UL+(uint32_t)tile_index*128;
  uint32_t dest=4096UL+(uint32_t)(first+col)*128;
  uint8_t data[128];
  addr(source);
  for(uint8_t i=0;i<128;++i){
   uint8_t pixel=v[3];
   bool keep=(hi&8)?i>=80:i<48;
   data[i]=keep?pixel:0;
  }
  addr(dest);for(uint8_t i=0;i<128;++i)v[3]=data[i];
  addr(cell);v[3]=(uint8_t)(first+col);v[3]=(hi&0xfc)|((first+col)>>8);
 }
 addr(29u*128+39*2);uint8_t lo=v[3],hi=v[3];
 for(uint8_t row=26;row<30;++row){
  addr((uint16_t)row*128+48);
  for(uint8_t col=0;col<13;++col){v[3]=lo;v[3]=hi;}
 }
}
static void controls_panel(void){
 static const char*const labels[]={
  "FLIPPERS  Z /",
  "PLUNGER   SPACE",
  "NEW GAME  F2",
  "EXIT      ESC",
  "MUSIC     M",
 };
 uint8_t sprite=76;
 for(uint8_t row=0;row<sizeof(labels)/sizeof(labels[0]);++row)
  for(uint8_t i=0;labels[row][i];++i){
   uint8_t c=labels[row][i];
   if(c!=' ')tile(sprite++,FONT_BASE/32+c-32,405+i*8,308+row*16,FONT_BANK);
  }
}
int main(void){
 uint8_t oldbank=*(volatile uint8_t*)0;uint16_t oldkey=*(volatile uint16_t*)0x032e;
 print("\x93" "CMDRX CADET - ORIGINAL TABLE\rLOADING...\r");v[5]=0;v[9]=1;
 if(!game_load()||!load("MAP.BIN",2,0)||!load("TILES.BIN",2,0x1000)||!load("PAL.BIN",3,0xfa00)||
 !load("SPRITES.BIN",3,SPRITE_BASE&65535)||!load("FONT.BIN",3,FONT_BASE&65535))goto fail;
 /* Clear the spill below the cabinet using the existing blank map tile. */
 addr(29u*128+39*2);uint8_t blank_lo=v[3],blank_hi=v[3];
 for(uint8_t row=27;row<30;++row){
  addr((uint16_t)row*128);
  for(uint8_t col=0;col<24;++col){v[3]=blank_lo;v[3]=blank_hi;}
 }
 for(uint8_t i=0;i<2;++i){char n[]="MUSIC0.BIN";n[5]+=i;*(volatile uint8_t*)0=32+i*8;if(!load(n,0,0xa000))goto fail;}
 for(uint8_t i=0;i<PCM_PARTS;++i){char n[]="PCM0.BIN";n[3]+=i;*(volatile uint8_t*)0=pcm_load_banks[i];if(!load(n,0,0xa000))goto fail;}
 for(uint8_t i=0;i<9;++i){char n[]="DEPTH00.BIN";n[6]+=i;*(volatile uint8_t*)0=i==0?10:i<3?16+i:i+42;if(!load(n,0,0xa000))goto fail;}
 for(uint8_t i=0;i<DYNAMIC_BANK_COUNT;++i){char n[]="DYN0.BIN";n[3]+=i;*(volatile uint8_t*)0=dynamic_load_banks[i];if(!load(n,0,0xa000))goto fail;}
 *(volatile uint8_t*)0=11;if(!load("UI.BIN",0,0xa000))goto fail;
 for(uint8_t i=0;i<128;++i)hide(i);
 for(uint8_t i=0;i<9;++i)score_cache[i]=254;
 compact_footer();controls_panel();
 /* Fill the 640x480 signal with the playable viewport. Keep the backbox
  * entirely visible while reducing the empty strip below the cabinet. */
 v[5]=0;v[9]=0x51;v[10]=119;v[11]=117;v[12]=0;
 v[13]=0x12;v[14]=0;v[15]=0x0b;v[16]=v[17]=v[18]=v[19]=0;
 __asm__ volatile("sei");*(volatile uint16_t*)0x032e=(uint16_t)(uintptr_t)keyboard;__asm__ volatile("cli");
 lab_install();game_start();dynamic_init();frame(31,32,403,197,1);display(true);
#ifndef NO_MUSIC
 music_start();
#endif

 uint16_t last=lab_clock(),count=0,gaps=0,over=0;uint32_t maximum=0,total=0;
 uint8_t old_m=0,old_new=0;echo("# PLAY READY\n");
#ifdef GAME_TEST
 *(volatile uint8_t*)0x9fb8=0;
#endif
 for(;;){
  uint16_t now=lab_clock();if(now==last)continue;if((uint16_t)(now-last)>1)++gaps;last=now;
  uint32_t before=irq_start;
#ifdef GAME_TEST
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
  if(keys[110])break;
  if(keys[113]&&!old_new){game_start();previous_state=255;}
  if(keys[52]&&!old_m){if(music_enabled)music_stop();else music_start();}
  old_new=keys[113];old_m=keys[52];
  game_frame(keys[44]||keys[46],keys[55]||keys[57],keys[61],keys[83]);
#endif

#ifdef PROFILE_DISPLAY
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
  if(elapsed>maximum){maximum=elapsed;echo("# WORST ");hex(count);echo(" ");hex(elapsed);echo("\n");}
  if(elapsed>133333)++over;
#ifdef GAME_TEST
#ifndef TEST_FRAMES
#define TEST_FRAMES 6000
#endif
  if(count>=TEST_FRAMES)break;
#endif
 }
 echo("# RESULT ");hex(count);echo(" ");hex(maximum);echo(" ");hex(total/count);echo(" ");hex(over);echo(" ");hex(gaps);echo(" ");hex(irq_max);echo(" ");hex(music_error);echo("\n# PCM UNDERRUNS ");hex(pcm_underruns);echo("\n# DONE\n");
 lab_uninstall();__asm__ volatile("sei");*(volatile uint16_t*)0x032e=oldkey;__asm__ volatile("cli");
 *(volatile uint8_t*)0=oldbank;
#ifdef GAME_TEST
 *(volatile uint8_t*)0x9fb4=0;__asm__ volatile("jmp $ffff");
#endif
 __asm__ volatile("jsr $ff81");return 0;
fail:*(volatile uint8_t*)0=oldbank;__asm__ volatile("jsr $ff81");print("ASSET LOAD FAILED\r");echo("# LOAD FAILED\n");return 1;
}
