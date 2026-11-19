/* Actual original-wall impulses must expose the complete rubber/glow composite
 * in the same render call and restore it after the source's six-frame timer. */
#include <cbm.h>
#include <stdint.h>
#include "engine.h"
#include "dynamic.h"
static volatile uint8_t *const v=(volatile uint8_t*)0x9f20;
static uint16_t checks,errors;
static uint32_t maximum;
static void text(const char*s){while(*s)*(volatile uint8_t*)0x9fbb=*s++;}
static void hex(uint32_t n){for(uint8_t i=0;i<8;++i){*(volatile uint8_t*)0x9fbb="0123456789abcdef"[n>>28];n<<=4;}}
static uint16_t word(const uint8_t*p){return(uint16_t)p[0]|((uint16_t)p[1]<<8);}
static uint8_t load(const char*n,uint8_t mode,uint16_t a){cbm_k_setnam(n);cbm_k_setlfs(1,8,2);return(uintptr_t)cbm_k_load(mode,(void*)a)>255;}
static uint32_t cycles(void){uint8_t a=*(volatile uint8_t*)0x9fb8,b=*(volatile uint8_t*)0x9fb9,c=*(volatile uint8_t*)0x9fba,d=*(volatile uint8_t*)0x9fbb;return(uint32_t)a|((uint32_t)b<<8)|((uint32_t)c<<16)|((uint32_t)d<<24);}
static void check(uint8_t condition){++checks;if(!condition)++errors;}
static void visible(uint8_t side,uint8_t pose){
 const DynamicDesc*d=dynamic_desc+side;*(volatile uint8_t*)0=d->bank;
 const uint8_t*p=(const uint8_t*)(uintptr_t)d->ptr;uint8_t count=*p;p+=4;
 while(count--){uint16_t a=word(p),expected=word(p+2+pose*2);p+=6;
  v[5]=0;v[0]=a;v[1]=a>>8;v[2]=0x10;uint16_t actual=v[3];actual|=(uint16_t)v[3]<<8;check(actual==expected);
 }
 *(volatile uint8_t*)0=11;
}
static void render(void){uint32_t start=cycles();dynamic_update(0);uint32_t elapsed=cycles()-start;if(elapsed>maximum)maximum=elapsed;check(*(volatile uint8_t*)0==11);}
int main(void){
 if(!game_load()||!load("TILES.BIN",2,4096)){text("# LOAD FAILED\n# DONE\n");return 1;}
 for(uint8_t i=0;i<DYNAMIC_BANK_COUNT;++i){char n[]="DYN0.BIN";n[3]+=i;*(volatile uint8_t*)0=dynamic_load_banks[i];if(!load(n,0,0xa000)){text("# LOAD FAILED\n# DONE\n");return 1;}}
 *(volatile uint8_t*)0=11;game_start();dynamic_init();
 for(uint8_t side=0;side<2;++side){
  game_start();while(dynamic_update(128)){}
  game_place(side?-986:986,2249,side?944:-944,-396,1);
  game_frame(false,false,false,false);
  check(game_pose(469+side)==1);check(game_lamp(180+side)==1);check(game.contacts==1);
  render();visible(side,1);
  for(uint8_t tick=1;tick<=6;++tick){
   game_frame(false,false,false,false);render();uint8_t active=tick<6;
   check(game_pose(469+side)==active);check(game_lamp(180+side)==active);visible(side,active);
  }
 }
 check(maximum<20000);
 text(errors?"# SLINGSHOT RENDER FAIL ":"# SLINGSHOT RENDER PASS ");hex(checks);text(" ");hex(errors);text(" ");hex(maximum);text("\n# DONE\n");
 *(volatile uint8_t*)0x9fb4=0;__asm__ volatile("jmp $ffff");return 0;
}
