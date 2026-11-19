/* Static grazing-tip regression from original rest-tip circles.
 * The pre-fix engine misses both outside-to-outside crossings. */
#include "engine.c"
#ifndef __CX16__
#include <stdio.h>
#endif
static uint16_t checks,failures;
static void check(bool ok){++checks;if(!ok)++failures;}
static void text(const char*s){
#ifdef __CX16__
 while(*s)*(volatile uint8_t*)0x9fbb=*s++;
#else
 fputs(s,stdout);
#endif
}
static void hex(uint16_t x){for(uint8_t i=0;i<4;++i){char s[2]={"0123456789abcdef"[x>>12],0};text(s);x<<=4;}}
int main(void){
 if(!game_load()){text("# LOAD FAILED\n# DONE\n");return 1;}
 for(uint8_t side=0;side<2;++side){
  int16_t sign=side?-1:1;
  game_start();game_place(sign*46,3284,sign*8232,11704,1);
  uint32_t before=mul(game.vx,game.vx)+mul(game.vy,game.vy);
  game_frame(false,false,false,false);
  check(game.flipper_hits==1);check(game.state==InPlay);
  check((uint32_t)(mul(game.vx,game.vx)+mul(game.vy,game.vy))<=before);
  /* This farther parallel path stays outside the actual tip circle. */
  game_start();game_place(sign*13,3307,sign*8232,11704,1);
  game_frame(false,false,false,false);check(game.flipper_hits==0);
  /* An elevated ball must not collide with a floor flipper. */
  game_start();game_place(sign*46,3284,sign*8232,11704,4);
  game_frame(false,false,false,false);check(game.flipper_hits==0);
 }
 text("# TIP ");hex(checks);text(" ");hex(failures);text(failures?" FAIL\n":" PASS\n");text("# DONE\n");
#ifdef __CX16__
 *(volatile uint8_t*)0x9fb4=0;__asm__ volatile("jmp $ffff");
#endif
 return failures!=0;
}
