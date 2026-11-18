/* Runnable asset audition, deliberately separate from the accepted game. */
#include <cbm.h>
#include <stdint.h>
#include "lab-assets.h"
#include "music-files.h"
extern void lab_install(void),lab_uninstall(void),pcm_start(uint16_t),pcm_stop(void),music_start(void),music_stop(void);
extern uint16_t lab_clock(void);
extern volatile uint8_t music_enabled,music_loops,music_error;
extern volatile uint16_t pcm_remaining;
extern volatile uint32_t irq_max,fm_writes,psg_writes;
static volatile uint8_t*const v=(volatile uint8_t*)0x9f20;
static void print(const char*s){while(*s)cbm_k_bsout(*s++);}
static uint8_t load(const char*n,uint8_t mode,uint16_t addr){
 cbm_k_setnam(n);cbm_k_setlfs(1,8,2);
 return (uintptr_t)cbm_k_load(mode,(void*)addr)>255;
}
static void addr(uint32_t a){v[5]=0;v[0]=a;v[1]=a>>8;v[2]=0x10|(a>>16);}
static void text(uint8_t x,uint8_t y,const char*s){
 uint8_t count=0;addr(0x1a000UL+(uint16_t)y*256+(uint16_t)x*2);
 while(*s&&count++<31){uint8_t c=*s++;v[3]=(c>=32&&c<128)?c-32:0;v[3]=FONT_PALETTE<<4;}
 while(count++<31){v[3]=0;v[3]=FONT_PALETTE<<4;}
}
static void video(void){
 uint16_t i;addr(0x1a000UL);for(i=0;i<16384;++i)v[3]=0;
 v[5]=0;v[9]=0x31;v[10]=128;v[11]=128;v[12]=0;
 v[13]=0x12;v[14]=0;v[15]=0x0b;v[16]=v[17]=v[18]=v[19]=0;
 v[20]=0x62;v[21]=0xd0;v[22]=0xf0;v[23]=v[24]=v[25]=v[26]=0;
}
static void echo(const char*s){while(*s)*(volatile uint8_t*)0x9fbb=*s++;}
static void hex(uint32_t n){uint8_t i;for(i=0;i<8;++i){*(volatile uint8_t*)0x9fbb="0123456789abcdef"[n>>28];n<<=4;}}
static uint32_t cycle_clock(void){
 uint8_t a=*(volatile uint8_t*)0x9fb8,b=*(volatile uint8_t*)0x9fb9,c=*(volatile uint8_t*)0x9fba,d=*(volatile uint8_t*)0x9fbb;
 return (uint32_t)a|((uint32_t)b<<8)|((uint32_t)c<<16)|((uint32_t)d<<24);
}
static void event(const char*s,uint16_t id){echo("# EVENT ");echo(s);echo(" ");hex(id);echo(" ");hex(cycle_clock());echo("\n");}
static uint8_t play(uint8_t effect){
 uint8_t bank=*(volatile uint8_t*)0;pcm_stop();
 *(volatile uint8_t*)0=1;
 if(!load(effect_files[effect],0,0xa000)){*(volatile uint8_t*)0=bank;return 0;}
 *(volatile uint8_t*)0=bank;event("EFFECT",effect);pcm_start(effect_lengths[effect]);return 1;
}
int main(void){
 uint8_t i,selected=0,k,oldbank=*(volatile uint8_t*)0;
 uint16_t now,last=0;char file[]="MUSIC0.BIN";
 print("\x93" "CMDRX CADET FIDELITY LAB\rLOADING...\r");
 v[5]=0;v[9]=1;
 if(!load("MAP.BIN",2,0)||!load("TILES.BIN",2,0x1000)||!load("PAL.BIN",3,0xfa00)||!load("FONT.BIN",3,0xe000))goto fail;
 for(i=0;i<MUSIC_PARTS;++i){file[5]='0'+i;*(volatile uint8_t*)0=16+i*8;if(!load(file,0,0xa000))goto fail;}
 *(volatile uint8_t*)0=oldbank;video();lab_install();
 text(48,46,effect_files[selected]);text(48,48,"MUSIC OFF");
#if defined(MUSIC_TEST) || defined(PCM_TEST)
 *(volatile uint8_t*)0x9fb8=0;*(volatile uint8_t*)0x9fb6=1;
#endif
#ifdef MUSIC_TEST
 music_start();event("MUSIC",0);
 while(!music_loops&&!music_error){}
 event("LOOP",music_loops);
#else
#ifdef PCM_TEST
 event("BEGIN",0);
 for(selected=0;selected<EFFECT_COUNT;++selected){
  if(!play(selected)){echo("# LOAD FAILED\n");break;}
  while(pcm_remaining||!(v[27]&0x40)){}
  now=lab_clock();while((uint16_t)(lab_clock()-now)<12){}
 }
 event("END",selected);
#else
 for(;;){
  now=lab_clock();if(now==last)continue;last=now;
  k=cbm_k_getin();if(!k)continue;
  if(k==27)break;
  if(k==157){if(selected)--selected;else selected=EFFECT_COUNT-1;}
  if(k==29){if(++selected==EFFECT_COUNT)selected=0;}
  if(k==32&&!play(selected)){text(48,48,"SAMPLE LOAD FAILED");continue;}
  if(k=='M'||k=='m'){if(music_enabled)music_stop();else music_start();event("MUSIC",music_enabled);}
  if(k=='S'||k=='s'){pcm_stop();music_stop();}
  text(48,46,effect_files[selected]);text(48,48,music_enabled?"MUSIC ON":"MUSIC OFF");
 }
#endif
#endif
 echo("# STATS ");hex(irq_max);echo(" ");hex(fm_writes);echo(" ");hex(psg_writes);echo(" ");hex(music_loops);echo(" ");hex(music_error);echo("\n");
 lab_uninstall();*(volatile uint8_t*)0=oldbank;
 __asm__ volatile("jsr $ff81");print("FIDELITY LAB ENDED\r");echo("# DONE\n");return 0;
fail:
 *(volatile uint8_t*)0=oldbank;__asm__ volatile("jsr $ff81");print("FIDELITY ASSET LOAD FAILED\r");return 1;
}
