/* Host-only independent oracle for the production uint32_t award helper.
 * cc -O2 -fsanitize=address,undefined -Icadet/play-build
 *   cadet/game/test_award_large.c -o /tmp/cadet-test-award-large
 * Includes engine.c so the private banked-rules helper is tested directly. */
#include "engine.c"
#include <assert.h>
#include <stdio.h>

typedef unsigned __int128 Wide;
static void setup_score(Wide n){
 memset(&game,0,sizeof game);Wide v=n;
 for(unsigned i=0;i<16;++i){game.score[i]=v;v>>=8;}
 v=n;for(unsigned i=0;i<40;++i){game.digits[i]=v%10;v/=10;}
}
static void verify_score(Wide n){
 Wide v=n;for(unsigned i=0;i<16;++i){assert(game.score[i]==(uint8_t)v);v>>=8;}
 v=n;for(unsigned i=0;i<40;++i){assert(game.digits[i]==v%10);v/=10;}
}
int main(void){
 const uint32_t award[]={0,1,49999,50000,50001,65535,65536,99999,100000,100001,149999,150000,150001,5000000,UINT32_MAX};
 const uint32_t room[]={0,1,49999,50000,50001,99999,100000,100001,125000,149999,150000,150001,UINT32_MAX};
 const Wide max=~(Wide)0;unsigned carries=0,limits=0,latches=0;
 for(unsigned a=0;a<sizeof award/sizeof *award;++a){
  uint32_t n=award[a];
  for(unsigned bit=0;bit<128;++bit){
   Wide start=((Wide)1<<bit)-1;setup_score(start);rule_award_large(n);
   verify_score(start+n);assert(!game.overflow);++carries;
  }
  /* Check every chunk edge and the exact full-award limit. In particular,
   * max-125000 + 150000 previously committed 100000 before overflowing. */
  for(unsigned r=0;r<sizeof room/sizeof *room+3;++r){
   Wide capacity=r<sizeof room/sizeof *room?room[r]:
    r==sizeof room/sizeof *room?(n?(Wide)n-1:0):
    r==sizeof room/sizeof *room+1?(Wide)n:(Wide)n+1;
   Wide start=max-capacity;setup_score(start);rule_award_large(n);
   bool overflow=(Wide)n>capacity;
   verify_score(overflow?start:start+n);assert(game.overflow==overflow);
   assert(game.score_dirty==(n!=0));++limits;
  }
  setup_score(max-125000);game.overflow=true;rule_award_large(n);
  verify_score(max-125000);assert(game.overflow);assert(!game.score_dirty);++latches;
 }
 printf("LARGE AWARD PASS: %u carry cases, %u atomic-limit cases, %u overflow-latch cases; binary score and decimal digits verified\n",carries,limits,latches);
 return 0;
}
