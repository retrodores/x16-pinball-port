/* Independent host oracle: exercise every uint16 award and 128-bit carries. */
#include "engine.h"
#include <stdio.h>
#include <string.h>
#include <assert.h>
typedef unsigned __int128 Wide;
static void setup(Wide n){
 memset(&game,0,sizeof game);Wide v=n;
 for(unsigned i=0;i<16;++i){game.score[i]=v;v>>=8;}
 v=n;for(unsigned i=0;i<40;++i){game.digits[i]=v%10;v/=10;}
}
static void verify(Wide n){
 Wide v=n;for(unsigned i=0;i<16;++i){assert(game.score[i]==(uint8_t)v);v>>=8;}
 v=n;for(unsigned i=0;i<40;++i){assert(game.digits[i]==v%10);v/=10;}
}
int main(void){
 Wide sum=0;setup(0);
 for(unsigned n=0;n<=65535;++n){add_score(n);sum+=n;verify(sum);assert(!game.overflow);}
 for(unsigned bit=0;bit<128;++bit){
  Wide start=((Wide)1<<bit)-1;setup(start);add_score(1);verify(start+1);assert(!game.overflow);
 }
 Wide max=~(Wide)0;
 for(unsigned n=1;n<=65535;n+=257){
  setup(max-n);add_score(n);verify(max);assert(!game.overflow);
  add_score(1);verify(max);assert(game.overflow);
 }
 puts("SCORE PASS: all 65536 uint16 awards; 128 carry boundaries; 255 full-width overflow checks");
}
