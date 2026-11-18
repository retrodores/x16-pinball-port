#include "engine.h"
#include <stdint.h>
#ifndef __CX16__
#include <stdio.h>
#endif
#ifdef __CX16__
static void text(const char*s){while(*s)*(volatile uint8_t*)0x9fbb=*s++;}
static void hex(uint32_t x){for(uint8_t i=0;i<8;++i){*(volatile uint8_t*)0x9fbb="0123456789abcdef"[x>>28];x<<=4;}}
static uint32_t clock_read(void){uint8_t a=*(volatile uint8_t*)0x9fb8,b=*(volatile uint8_t*)0x9fb9,c=*(volatile uint8_t*)0x9fba,d=*(volatile uint8_t*)0x9fbb;return(uint32_t)a|((uint32_t)b<<8)|((uint32_t)c<<16)|((uint32_t)d<<24);}
#else
static void text(const char*s){fputs(s,stdout);}
static void hex(uint32_t x){printf("%08x",x);}
static uint32_t clock_read(void){return 0;}
#endif
int main(void){
 uint32_t worst=0,total=0;uint16_t t,over=0;uint8_t run=0;uint16_t drains=0,escapes=0,flips=0,bumps=0,ramps=0;
 if(!game_load()){text("# LOAD FAILED\n");return 1;}game_start();text("# START\n");
 for(t=0;t<6000;++t){bool left=t%43<12,right=t%67<14,pull=game.state==Serving&&game.charge<80;
#ifdef __CX16__
  *(volatile uint8_t*)0x9fb8=0;
#endif
  game_frame(left,right,pull,false);uint32_t n=clock_read();total+=n;
  if(n>worst){worst=n;text("# WORST ");hex(t);text(" ");hex(n);text(" ");hex(game.x);text(" ");hex(game.y);text("\n");}
  if(n>105000)++over;
  if(!(t%120)){text("# STATE ");hex(t);text(" ");hex(game.x);text(" ");hex(game.y);text(" ");hex(game.vx);text(" ");hex(game.vy);text(" ");hex(game.state);text("\n");}
  if(game.state==GameOver){drains+=game.drains;escapes+=game.escapes;flips+=game.flipper_hits;bumps+=game.bumper_hits;ramps+=game.ramp_entries;if(++run==3)break;game_start();}
 }
 text("# RESULT ");hex(worst);text(" ");hex(total/(t+1));text(" ");hex(over);text(" ");hex(drains+game.drains);text(" ");hex(escapes+game.escapes);text(" ");hex(flips+game.flipper_hits);text(" ");hex(bumps+game.bumper_hits);text(" ");hex(ramps+game.ramp_entries);text("\n# DONE\n");
 #ifdef __CX16__
 *(volatile uint8_t*)0x9fb4=0;__asm__ volatile("jmp $ffff");
 #endif
 return 0;
}
