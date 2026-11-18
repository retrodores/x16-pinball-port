/* Original-table integration. Physics, graphics and audio stay independently testable. */
#include "engine.h"
#include "sprites.h"
#include "audio.h"
#include "ui.h"
#include "projection.h"
extern int32_t signedmul(int16_t,int16_t);
extern uint32_t fastmul16(uint16_t,uint16_t);
static int16_t projected(int16_t value,uint16_t scale){uint32_t p=fastmul16(value<0?-value:value,scale);return value<0?-(int16_t)(p>>12):(int16_t)(p>>12);}
#include <cbm.h>
#include <stdint.h>
extern void lab_install(void),lab_uninstall(void),pcm_start(uint16_t),pcm_stop(void),music_start(void),music_stop(void);
extern uint16_t lab_clock(void);
extern volatile uint8_t pcm_select_bank,music_enabled,music_error,music_loops;
extern volatile uint16_t pcm_select_ptr,pcm_remaining;
extern volatile uint32_t irq_max,irq_start;
__attribute__((used)) volatile uint8_t keys[128];
__attribute__((naked,used)) void keyboard(void){__asm__ volatile(
 "phx\npha\nand #127\ntax\npla\nbmi 1f\nlda #1\nbra 2f\n1: lda #0\n2: sta keys,x\nplx\nlda #0\nrts");}
static volatile uint8_t *const v=(volatile uint8_t*)0x9f20;
static uint8_t priority,previous_state=255,phase_cache[2]={255,255},plunger_cache=255;
static uint8_t score_cache[9],ball_cache=255,status_cache[40];
static void addr(uint32_t a){v[5]=0;v[0]=a;v[1]=a>>8;v[2]=0x10|(a>>16);}
static void word(uint16_t a){v[3]=a;v[3]=a>>8;}
static void hide(uint8_t n){addr(0x1fc06UL+(uint16_t)n*8);v[3]=0;}
static void tile(uint8_t n,uint16_t a,int16_t x,int16_t y,uint8_t size){addr(0x1fc00UL+(uint16_t)n*8);word(a);word(x);word(y);v[3]=12;v[3]=size;}
static void frame(uint8_t n,uint8_t f,int16_t x,int16_t y,uint8_t reserved){
 const SpriteFrame*s=&sprites[f];
 for(uint8_t i=0;i<reserved;++i){
  if(i<s->count){const SpriteTile*t=s->tiles+i;tile(n+i,t->address,x+t->x,y+t->y,0x50|t->palette);}else hide(n+i);
 }
}
static uint8_t load(const char*n,uint8_t mode,uint16_t a){cbm_k_setnam(n);cbm_k_setlfs(1,8,2);return(uintptr_t)cbm_k_load(mode,(void*)a)>255;}
static void print(const char*s){while(*s)cbm_k_bsout(*s++);}
static void echo(const char*s){while(*s)*(volatile uint8_t*)0x9fbb=*s++;}
static void hex(uint32_t a){for(uint8_t i=0;i<8;++i){*(volatile uint8_t*)0x9fbb="0123456789abcdef"[a>>28];a<<=4;}}
static uint32_t cycles(void){uint8_t a=*(volatile uint8_t*)0x9fb8,b=*(volatile uint8_t*)0x9fb9,c=*(volatile uint8_t*)0x9fba,d=*(volatile uint8_t*)0x9fbb;return(uint32_t)a|((uint32_t)b<<8)|((uint32_t)c<<16)|((uint32_t)d<<24);}
static void effect(uint8_t id,uint8_t rank){
 if(id==255)return;
 if(pcm_remaining&&rank<priority)return;
 const Effect*e=effects+id;pcm_select_bank=e->bank;pcm_select_ptr=e->ptr;priority=rank;pcm_start(e->length);
}
void audio_stop(void){pcm_stop();priority=0;}
void audio_effect(uint8_t id){
 switch(id){
 case 0:effect(SOUND104,1);break;
 case 1:effect(SOUND105,1);break;
 case 2:case 6:effect(contact_sound[game.last_group],2);break;
 case 3:if(game.returns==0||game.last_kind==Plunger)effect(SOUND22,3);break;
 default:break;
 }
}
static void status(const char*s){
 for(uint8_t i=0;i<40;++i){uint8_t c=*s?*s++:32;if(status_cache[i]==c)continue;status_cache[i]=c;
  tile(50+i,FONT_BASE/32+c-32,405+(i%20)*8,248+(i/20)*8,FONT_BANK);
 }
}
static void display(void){
 /* Camera matrix from PINBALL.DAT, Q8. Products retain 16 fractional bits. */
 int16_t depth=6317-(signedmul(game.y,104)+signedmul(game.z,234))/256;
 int16_t camera_y=(signedmul(game.y,-234)+signedmul(game.z,104))/256+971;
 if(depth<2048)depth=2048;if(depth>10232)depth=10232;
 uint16_t scale=projection_scale[(depth-2048+4)>>3];
 int16_t x=191-projected(game.x,scale),y=243-projected(camera_y,scale);
 uint8_t f=0;while(f<6&&ball_depths[f]>depth)++f;
 const SpriteFrame*b=sprites+24+f;
 if(game.state==Serving||game.state==InPlay)frame(0,24+f,x-b->width/2,y-b->height/2,1);else hide(0);
 for(uint8_t i=0;i<2;++i){uint8_t pose=((uint16_t)game.phase[i]*7+60)/120;
  if(pose!=phase_cache[i]){f=i*8+pose;frame(1+i*12,f,sprites[f].x,sprites[f].y,12);phase_cache[i]=pose;}
 }
 uint8_t pose=game.state==Serving?(uint16_t)game.charge*7/100:0;
 if(pose!=plunger_cache){f=16+pose;frame(25,f,sprites[f].x,sprites[f].y,6);plunger_cache=pose;}
 if(game.score_dirty){uint8_t hi=39;while(hi&&!game.digits[hi])--hi;
  for(uint8_t i=0;i<9;++i){uint8_t digit=i<=hi?game.digits[i]:255;if(digit==score_cache[i])continue;score_cache[i]=digit;
   if(digit==255){hide(31+i*2);hide(32+i*2);}else frame(31+i*2,31+digit,553-i*15,197,2);
  }
  if(hi>=9){echo("# EXACT SCORE ");for(int8_t i=hi;i>=0;--i)*(volatile uint8_t*)0x9fbb=48+game.digits[i];echo("\n");}
  game.score_dirty=false;
 }
 uint8_t number=game.ball_number;if(number!=ball_cache){frame(90,31+number,553,152,2);ball_cache=number;}
 if(previous_state!=game.state){
  static const char*const labels[]={"F2: NEW GAME","HOLD SPACE TO LAUNCHRELEASE TO FIRE","BALL IN PLAY","CAPTURE / RETURN","NEXT BALL","GAME OVER           F2: NEW GAME"};
  status(labels[game.state]);previous_state=game.state;
  if(game.state==Serving)effect(SOUND4,3);
 }
 /* 128-bit score remains exact. Flag a panel overflow instead of silently truncating. */
 for(uint8_t i=9;i<40;++i)if(game.digits[i]){status("SCORE EXCEEDS PANEL  SEE EXACT SCORE LOG");break;}
}
int main(void){
 uint8_t oldbank=*(volatile uint8_t*)0;uint16_t oldkey=*(volatile uint16_t*)0x032e;
 print("\x93" "CMDRX CADET - ORIGINAL TABLE\rLOADING...\r");v[5]=0;v[9]=1;
 if(!game_load()||!load("MAP.BIN",2,0)||!load("TILES.BIN",2,0x1000)||!load("PAL.BIN",3,0xfa00)||
 !load("SPRITES.BIN",3,SPRITE_BASE&65535)||!load("FONT.BIN",3,FONT_BASE&65535))goto fail;
 for(uint8_t i=0;i<4;++i){char n[]="MUSIC0.BIN";n[5]+=i;*(volatile uint8_t*)0=32+i*8;if(!load(n,0,0xa000))goto fail;}
 for(uint8_t i=0;i<PCM_PARTS;++i){char n[]="PCM0.BIN";n[3]+=i;*(volatile uint8_t*)0=19+i*8;if(!load(n,0,0xa000))goto fail;}
 *(volatile uint8_t*)0=oldbank;
 for(uint8_t i=0;i<128;++i)hide(i);
 for(uint8_t i=0;i<9;++i)score_cache[i]=254;
 v[5]=0;v[9]=0x51;v[10]=v[11]=128;v[12]=0;
 v[13]=0x12;v[14]=0;v[15]=0x0b;v[16]=v[17]=v[18]=v[19]=0;
 __asm__ volatile("sei");*(volatile uint16_t*)0x032e=(uint16_t)(uintptr_t)keyboard;__asm__ volatile("cli");
 lab_install();game_start();frame(92,32,403,197,2);display();
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
  game_frame(count%43<12,count%67<14,game.state==Serving&&game.charge<80,false);
  if(game.state==GameOver)game_start();
#else
  if(keys[110])break;
  if(keys[113]&&!old_new){game_start();previous_state=255;}
  if(keys[52]&&!old_m){if(music_enabled)music_stop();else music_start();}
  old_new=keys[113];old_m=keys[52];
  game_frame(keys[44]||keys[46],keys[55]||keys[57],keys[61],keys[83]);
#endif
  display();++count;
  uint32_t elapsed=cycles()-before;total+=elapsed;
  if(elapsed>maximum){maximum=elapsed;echo("# WORST ");hex(count);echo(" ");hex(elapsed);echo("\n");}
  if(elapsed>133333)++over;
#ifdef GAME_TEST
  if(count>=6000)break;
#endif
 }
 echo("# RESULT ");hex(count);echo(" ");hex(maximum);echo(" ");hex(total/count);echo(" ");hex(over);echo(" ");hex(gaps);echo(" ");hex(irq_max);echo(" ");hex(music_error);echo("\n# DONE\n");
 lab_uninstall();__asm__ volatile("sei");*(volatile uint16_t*)0x032e=oldkey;__asm__ volatile("cli");
 *(volatile uint8_t*)0=oldbank;
#ifdef GAME_TEST
 *(volatile uint8_t*)0x9fb4=0;__asm__ volatile("jmp $ffff");
#endif
 __asm__ volatile("jsr $ff81");return 0;
fail:*(volatile uint8_t*)0=oldbank;__asm__ volatile("jsr $ff81");print("ASSET LOAD FAILED\r");echo("# LOAD FAILED\n");return 1;
}
