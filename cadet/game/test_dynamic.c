/* Native VERA readback verifies every packed mechanism pose and untouched nibble. */
#include <cbm.h>
#include <stdint.h>
#include "dynamic.h"
#include "engine.h"
Game game;
static uint8_t cross;
static uint8_t poses[DYNAMIC_COUNT],before[512];
static volatile uint8_t *const v=(volatile uint8_t*)0x9f20;
static uint16_t checks,errors;static uint32_t fast_max;
uint8_t game_pose(uint16_t group){for(uint8_t i=0;i<DYNAMIC_COUNT;++i)if(dynamic_desc[i].lamp!=3&&dynamic_desc[i].group==group)return poses[i];return 0;}
uint8_t game_lamp(uint16_t group){return group==254?cross:game_pose(group);}
uint8_t game_ring_lamp(uint8_t index){
 for(uint8_t i=0;i<DYNAMIC_COUNT;++i)if(dynamic_desc[i].lamp==3&&dynamic_desc[i].group==index)return poses[i];
 return 0;
}
static void text(const char*s){while(*s)*(volatile uint8_t*)0x9fbb=*s++;}
static void hex(uint16_t n){for(uint8_t i=0;i<4;++i){*(volatile uint8_t*)0x9fbb="0123456789abcdef"[n>>12];n<<=4;}}
static uint16_t word(const uint8_t*p){return(uint16_t)p[0]|((uint16_t)p[1]<<8);}
static uint8_t load(const char*n,uint8_t mode,uint16_t a){cbm_k_setnam(n);cbm_k_setlfs(1,8,2);return(uintptr_t)cbm_k_load(mode,(void*)a)>255;}
static void addr(uint16_t a,uint8_t high){v[5]=0;v[0]=a;v[1]=a>>8;v[2]=0x10|high;}
static uint32_t cycles(void){uint8_t a=*(volatile uint8_t*)0x9fb8,b=*(volatile uint8_t*)0x9fb9,c=*(volatile uint8_t*)0x9fba,d=*(volatile uint8_t*)0x9fbb;return(uint32_t)a|((uint32_t)b<<8)|((uint32_t)c<<16)|((uint32_t)d<<24);}
static void fast_maps(uint8_t pose){
 for(uint8_t i=0;i<DYNAMIC_FAST_COUNT;++i){
  const DynamicDesc*d=dynamic_desc+i;*(volatile uint8_t*)0=d->bank;
  const uint8_t*p=(const uint8_t*)(uintptr_t)d->ptr;uint8_t count=*p;p+=4;
  while(count--){uint16_t expected=word(p+2+pose*2);addr(word(p),0);uint16_t actual=v[3];actual|=(uint16_t)v[3]<<8;if(actual!=expected)++errors;++checks;p+=6;}
 }
 *(volatile uint8_t*)0=11;
}
static void fast_tick(void){uint32_t start=cycles();dynamic_update(0);uint32_t elapsed=cycles()-start;if(elapsed>fast_max)fast_max=elapsed;if(*(volatile uint8_t*)0!=11)++errors;}
int main(void){
 if(!load("TILES.BIN",2,4096)){text("# LOAD FAILED\n# DONE\n");return 1;}
 *(volatile uint8_t*)0=31;if(!load("RINGS.BIN",0,0xb000)){text("# LOAD FAILED\n# DONE\n");return 1;}
 *(volatile uint8_t*)0=11;if(!load("RINGS2.BIN",0,DYNAMIC_OVERFLOW_ADDRESS)){text("# LOAD FAILED\n# DONE\n");return 1;}
 for(uint8_t i=0;i<DYNAMIC_BANK_COUNT;++i){char n[]="DYN0.BIN";n[3]+=i;*(volatile uint8_t*)0=dynamic_load_banks[i];if(!load(n,0,0xa000)){text("# LOAD FAILED\n# DONE\n");return 1;}}
 *(volatile uint8_t*)0=11;dynamic_init();
 /* The X uses its own VERA sprite and also updates at zero tile budget. */
 *(volatile uint8_t*)0=63;
 const uint8_t*cross_data=(const uint8_t*)(uintptr_t)CROSS_PATTERN_PTR;
 addr(CROSS_PATTERN_VRAM&65535u,CROSS_PATTERN_VRAM>>16);
 for(uint8_t i=0;i<128;++i){if(v[3]!=cross_data[i])++errors;++checks;}
 *(volatile uint8_t*)0=11;
 cross=1;fast_tick();addr(0xfffeu,1);if(v[3]!=12)++errors;++checks;
 game.state=Serving;cross=0;fast_tick();addr(0xfffeu,1);if(v[3]!=0)++errors;++checks;
 /* Alternate pixels and original-rest patterns must be preloaded exactly. */
 for(uint8_t i=0;i<DYNAMIC_FAST_COUNT;++i){
  const DynamicDesc*d=dynamic_desc+i;*(volatile uint8_t*)0=d->bank;
  const uint8_t*p=(const uint8_t*)(uintptr_t)d->ptr;uint8_t tiles=p[0];const uint8_t*meta=p+4,*pixels=meta+(uint16_t)tiles*6;
  for(uint8_t pose=0;pose<2;++pose){const uint8_t*q=meta;
   for(uint8_t t=0;t<tiles;++t){uint32_t a=4096UL+(uint32_t)(word(q+2+pose*2)&1023)*128;q+=6;addr(a,a>>16);
    for(uint8_t k=0;k<128;++k){if(v[3]!=*pixels++)++errors;++checks;}
   }
  }
 }
 *(volatile uint8_t*)0=11;
 /* Both 100 ms flashes must display immediately despite an unfinished bumper
  * patch, remain visible for six simulation frames, and restore immediately. */
 poses[DYNAMIC_FAST_COUNT]=1;++game.visual_epoch;dynamic_update(1);
 for(uint8_t i=0;i<DYNAMIC_FAST_COUNT;++i)poses[i]=1;
 ++game.visual_epoch;fast_tick();fast_maps(1);
 for(uint8_t frame=1;frame<6;++frame){fast_tick();fast_maps(1);}
 for(uint8_t i=0;i<DYNAMIC_FAST_COUNT;++i)poses[i]=0;
 ++game.visual_epoch;fast_tick();fast_maps(0);
 while(dynamic_update(17)){}
 if(fast_max>20000)++errors;
 for(uint8_t i=DYNAMIC_FAST_COUNT;i<DYNAMIC_COUNT;++i){
  const DynamicDesc*d=dynamic_desc+i;*(volatile uint8_t*)0=d->bank;
  const uint8_t*p=(const uint8_t*)(uintptr_t)d->ptr;uint8_t runs=p[0],count=p[1];uint16_t bytes=word(p+2);
  const uint8_t *rp=p+4,*masks=rp+(uint16_t)runs*4,*values=masks+bytes;
  if(bytes>512){++errors;continue;}
  for(uint8_t pose=0;pose<count;++pose){
   uint16_t at=0;
   for(uint8_t r=0;r<runs;++r){const uint8_t*q=rp+(uint16_t)r*4;addr(word(q),q[2]);for(uint8_t k=0;k<q[3];++k)before[at++]=v[3];}
   poses[i]=pose;
   if(i==FLAG_DESCRIPTOR||i==FLAG_DESCRIPTOR+1)++game.spinner_epoch;
   else ++game.visual_epoch;
   *(volatile uint8_t*)0=11;
   uint16_t calls=0;while(dynamic_update(17)){if(*(volatile uint8_t*)0!=11)++errors;if(++calls>128){++errors;break;}}
   *(volatile uint8_t*)0=d->bank;at=0;const uint8_t*expected=values+(uint16_t)pose*bytes;
   for(uint8_t r=0;r<runs;++r){const uint8_t*q=rp+(uint16_t)r*4;addr(word(q),q[2]);
    for(uint8_t k=0;k<q[3];++k){uint8_t actual=v[3],mask=masks[at];if((actual&mask)!=(expected[at]&mask)||(actual&~mask)!=(before[at]&~mask))++errors;++at;++checks;}
   }
  }
 }
 text("# FAST MAP MAX ");hex(fast_max>>16);hex(fast_max);text("\n");
 text(errors?"# DYNAMIC FAIL ":"# DYNAMIC PASS ");hex(checks);text(" ");hex(errors);text("\n# DONE\n");
 *(volatile uint8_t*)0x9fb4=0;__asm__ volatile("jmp $ffff");return 0;
}
