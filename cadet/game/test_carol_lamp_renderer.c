#include <stdint.h>
#include <stdbool.h>
#include "engine.h"
Game game;
volatile uint8_t music_enabled;
volatile uint16_t christmas_song_tick;
static uint8_t reserved;
static volatile uint8_t *const v=(volatile uint8_t *)0x9f20;
static void addr(uint32_t a){v[5]=0;v[0]=a;v[1]=a>>8;v[2]=0x10|(a>>16);}
static void word(uint16_t n){v[3]=n;v[3]=n>>8;}
static void hide(uint8_t s){addr(0x1fc06UL+(uint16_t)s*8);v[3]=0;}
uint8_t game_ring_lamp(uint8_t i){return reserved&&i==19;}
bool game_claims_accent(uint16_t g){return reserved&&g==168;}
#include "christmas_lamps.h"

static void text(const char*s){while(*s)*(volatile uint8_t*)0x9fbb=*s++;}
static void hex(uint32_t n){for(uint8_t j=0;j<8;j++){*(volatile uint8_t*)0x9fbb="0123456789abcdef"[n>>28];n<<=4;}}
static uint32_t cycles(void){
 volatile uint8_t *const r=(volatile uint8_t *)0x9fb8;
 uint8_t a=r[0],b=r[1],c=r[2],d=r[3];
 return (uint32_t)a|((uint32_t)b<<8)|((uint32_t)c<<16)|((uint32_t)d<<24);
}
static uint8_t errors;
static uint32_t maximum;
static uint8_t count(uint16_t tick){
 christmas_song_tick=tick;
 for(uint8_t j=0;j<4;++j){
  __asm__ volatile("php\nsei":::"memory");
  uint32_t start=cycles();christmas_lamps();uint32_t elapsed=cycles()-start;
  __asm__ volatile("plp":::"memory");
  if(elapsed>maximum)maximum=elapsed;
 }
 uint8_t n=0;
 for(uint8_t i=0;i<HOLIDAY_COUNT;i++){
  addr(0x1fc06UL+((uint16_t)CHRISTMAS_FIRST_SPRITE+i)*8);
  if(v[3]&12)n++;
 }
 return n;
}
static void check(uint16_t t,uint8_t expect){uint8_t n=count(t);if(n!=expect){++errors;text("# BAD ");hex(t);text(" ");hex(n);text(" ");hex(expect);text("\n");}}
int main(void){
 game.state=Serving;music_enabled=1;christmas_init();
 check(0,0);check(64,2);check(84,0);check(2392,31);
 music_enabled=0;check(2392,0);music_enabled=1;check(0,0);
 check(9060,31);reserved=1;check(9060,29);
 reserved=0;game.mission=Practice;check(9060,13);
 game.mission=NoMission;game.tilted=1;check(9060,0);
 game.tilted=0;game.ring_flash=1;check(9060,0);
 game.ring_flash=0;game.state=Ready;check(9060,0);
 game.state=InPlay;check(13280,31);check(13740,0);check(13960,0);check(0,0);
 text("# SCORE-LAMP ");hex(errors);text(" ");hex(maximum);text("\n# DONE\n");
 return 0;
}
