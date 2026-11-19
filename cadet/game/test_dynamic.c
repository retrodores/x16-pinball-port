/* Native VERA readback verifies every packed mechanism pose and untouched nibble. */
#include <cbm.h>
#include <stdint.h>
#include "dynamic.h"
#include "engine.h"
Game game;
static uint8_t poses[DYNAMIC_COUNT],before[512];
static volatile uint8_t *const v=(volatile uint8_t*)0x9f20;
static uint16_t checks,errors;
uint8_t game_pose(uint16_t group){for(uint8_t i=0;i<DYNAMIC_COUNT;++i)if(dynamic_desc[i].group==group)return poses[i];return 0;}
uint8_t game_lamp(uint16_t group){return game_pose(group);}
static void text(const char*s){while(*s)*(volatile uint8_t*)0x9fbb=*s++;}
static void hex(uint16_t n){for(uint8_t i=0;i<4;++i){*(volatile uint8_t*)0x9fbb="0123456789abcdef"[n>>12];n<<=4;}}
static uint16_t word(const uint8_t*p){return(uint16_t)p[0]|((uint16_t)p[1]<<8);}
static uint8_t load(const char*n,uint8_t mode,uint16_t a){cbm_k_setnam(n);cbm_k_setlfs(1,8,2);return(uintptr_t)cbm_k_load(mode,(void*)a)>255;}
static void addr(uint16_t a,uint8_t high){v[5]=0;v[0]=a;v[1]=a>>8;v[2]=0x10|high;}
int main(void){
 if(!load("TILES.BIN",2,4096)){text("# LOAD FAILED\n# DONE\n");return 1;}
 for(uint8_t i=0;i<3;++i){char n[]="DYN0.BIN";n[3]+=i;*(volatile uint8_t*)0=58+i;if(!load(n,0,0xa000)){text("# LOAD FAILED\n# DONE\n");return 1;}}
 *(volatile uint8_t*)0=11;dynamic_init();
 for(uint8_t i=0;i<DYNAMIC_COUNT;++i){
  const DynamicDesc*d=dynamic_desc+i;*(volatile uint8_t*)0=d->bank;
  const uint8_t*p=(const uint8_t*)(uintptr_t)d->ptr;uint8_t runs=p[0],count=p[1];uint16_t bytes=word(p+2);
  const uint8_t *rp=p+4,*masks=rp+(uint16_t)runs*4,*values=masks+bytes;
  if(bytes>512){++errors;continue;}
  for(uint8_t pose=0;pose<count;++pose){
   uint16_t at=0;
   for(uint8_t r=0;r<runs;++r){const uint8_t*q=rp+(uint16_t)r*4;addr(word(q),q[2]);for(uint8_t k=0;k<q[3];++k)before[at++]=v[3];}
   poses[i]=pose;++game.visual_epoch;*(volatile uint8_t*)0=11;
   uint16_t calls=0;while(dynamic_update(17)){if(*(volatile uint8_t*)0!=11)++errors;if(++calls>128){++errors;break;}}
   *(volatile uint8_t*)0=d->bank;at=0;const uint8_t*expected=values+(uint16_t)pose*bytes;
   for(uint8_t r=0;r<runs;++r){const uint8_t*q=rp+(uint16_t)r*4;addr(word(q),q[2]);
    for(uint8_t k=0;k<q[3];++k){uint8_t actual=v[3],mask=masks[at];if((actual&mask)!=(expected[at]&mask)||(actual&~mask)!=(before[at]&~mask))++errors;++at;++checks;}
   }
  }
 }
 text(errors?"# DYNAMIC FAIL ":"# DYNAMIC PASS ");hex(checks);text(" ");hex(errors);text("\n# DONE\n");
 *(volatile uint8_t*)0x9fb4=0;__asm__ volatile("jmp $ffff");return 0;
}
