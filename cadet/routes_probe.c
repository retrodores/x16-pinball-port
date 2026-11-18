#include "routes.h"
#include "route-fixtures.h"
#include <string.h>
#ifndef __CX16__
#include <stdio.h>
#define EMIT(c) putchar(c)
#else
#define EMIT(c) (*(volatile uint8_t*)0x9fbb=(c))
#endif
static void text(const char*s){while(*s){EMIT(*s);++s;}}
static void hex(uint16_t n){uint8_t j;for(j=0;j<4;++j){EMIT("0123456789abcdef"[n>>12]);n<<=4;}}
static uint16_t checks,failed;
static void check(uint8_t ok,uint16_t i){++checks;if(!ok){++failed;text("not ok edge ");hex(i);text("\n");}}
int main(void){
 uint16_t i;cadet_edge e;cadet_ball b,old;const fixture*f;int16_t dz;uint8_t result;
 for(i=0;i<FIXTURE_COUNT;++i){
  f=&fixtures[i];e=f->edge;
  check(cadet_crosses(&e,f->shot[0],f->shot[1],f->shot[2],f->shot[3]),i);
  check(!cadet_crosses(&e,f->shot[2],f->shot[3],f->shot[0],f->shot[1]),i);
  check(!cadet_crosses(&e,e.ax,e.ay,e.bx,e.by),i); /* parallel along the rail */
  memset(&b,0,sizeof(b));b.x=f->mx;b.y=f->my;b.z=1000;b.radius=77;b.mask=e.mask;b.on_ramp=1;old=b;
  result=cadet_route(&e,&b);dz=b.z-f->z;
  check(result==f->result&&b.mask==f->mask&&dz>=-3&&dz<=3,i);
  if(result==CADET_RAMP)check(b.on_ramp==(e.action==1),i);
  else check(!memcmp(&old,&b,sizeof(b)),i);
  b=old;b.mask=8;old=b;
  check(cadet_route(&e,&b)==CADET_IGNORE&&!memcmp(&old,&b,sizeof(b)),i);
  b=old;b.mask=e.mask;old=b;e.active=0;
  check(cadet_route(&e,&b)==CADET_IGNORE&&!memcmp(&old,&b,sizeof(b)),i);
 }
 text("# ROUTE CHECKS ");hex(checks);text(" FAILED ");hex(failed);text("\n");
#ifdef __CX16__
 *(volatile uint8_t*)0x9fb4=failed?1:0;__asm__ volatile("jmp $ffff");
#endif
 return failed?1:0;
}
