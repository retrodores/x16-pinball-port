#include "engine.h"
#include <cbm.h>
#include <string.h>
int16_t bound_query[4];
extern const Edge* bounded_edge(uint16_t);
static void text(const char*s){while(*s)*(volatile uint8_t*)0x9fbb=*s++;}
static void hex(uint16_t n){for(uint8_t i=0;i<4;++i){*(volatile uint8_t*)0x9fbb="0123456789abcdef"[n>>12];n<<=4;}}
int main(void){
 for(uint8_t i=0;i<2;++i){char n[]="GEOM0.BIN";n[4]+=i;*(volatile uint8_t*)0=1+i*8;cbm_k_setnam(n);cbm_k_setlfs(1,8,2);if((uintptr_t)cbm_k_load(0,(void*)0xa000)<256)goto fail;}
 for(uint16_t id=0;id<1217;++id){
  *(volatile uint8_t*)0=12+(id>>8);Edge e;memcpy(&e,(const void*)(0xa000+(id&255)*32),32);
  for(uint8_t j=0;j<12;++j){
   bound_query[0]=e.xlo-5;bound_query[1]=e.xhi+5;bound_query[2]=e.ylo-5;bound_query[3]=e.yhi+5;
   switch(j){
    case 1:bound_query[1]=e.xlo-1;break;
    case 2:bound_query[0]=e.xhi+1;break;
    case 3:bound_query[3]=e.ylo-1;break;
    case 4:bound_query[2]=e.yhi+1;break;
    case 5:bound_query[1]=e.xlo;break;
    case 6:bound_query[0]=e.xhi;break;
    case 7:bound_query[3]=e.ylo;break;
    case 8:bound_query[2]=e.yhi;break;
    case 9:bound_query[0]=bound_query[2]=-32768;break;
    case 10:bound_query[1]=bound_query[3]=32767;break;
    case 11:bound_query[0]=bound_query[1]=bound_query[2]=bound_query[3]=0;break;
   }
   bool expected=!(bound_query[1]<e.xlo||bound_query[3]<e.ylo||bound_query[0]>e.xhi||bound_query[2]>e.yhi);
   const Edge*p=bounded_edge(id);
   if((p!=0)!=expected||(p&&(uintptr_t)p!=0xa000+(id&255)*32)||*(volatile uint8_t*)0!=12+(id>>8)){
    text("# BOUNDS FAIL ");hex(id);text(" ");hex(j);text(" ");hex((uintptr_t)p);text(" ");hex(expected);text("\n");goto fail;
   }
  }
 }
 text("# BOUNDS PASS 14604 signed comparisons\n# DONE\n");goto done;
fail:text("# FAIL\n# DONE\n");
done:*(volatile uint8_t*)0x9fb4=0;__asm__ volatile("jmp $ffff");return 0;
}
