/* Regressions for moving-flipper contacts from the OBS review.
 * Original oracle: TFlipperEdge::EdgeCollision + maths::basic_collision. */
#include "engine.c"
#ifndef __CX16__
#include <assert.h>
#include <stdio.h>
#endif
static unsigned failures;
static void check(bool ok){if(!ok)++failures;}
int main(void){
 if(!game_load())return 1;
 for(uint8_t side=0;side<2;++side){
  for(uint8_t mode=0;mode<3;++mode){
   game_start();game.state=InPlay;game.mask=1;game.phase[side]=25;
   Vec p=pivots[side],t=tips[side][25];
   int16_t ux=t.x-p.x,uy=t.y-p.y;
   uint16_t len=isqrt(mul(ux,ux)+mul(uy,uy));
   int16_t nx=normal(side==0?-uy:uy,len),ny=normal(side==0?ux:-ux,len);
   game.x=t.x+mul(nx,80)/256;game.y=t.y+mul(ny,80)/256;
   game.vx=mode==1?nx:0;game.vy=mode==1?ny:0;
   int16_t before=dot(game.vx,game.vy,nx,ny);
   paddle(side,mode==2?25:0);
   int16_t after=dot(game.vx,game.vy,nx,ny);
   if(mode==2){check(after==0);check(game.flipper_hits==0);}
   else {check(after>before+256);check(game.flipper_hits==1);}
#ifndef __CX16__
   printf("side=%u mode=%u before=%d after=%d hits=%u\n",side,mode,before,after,game.flipper_hits);
#endif
  }
 }
#ifdef __CX16__
 const char*s=failures?"# FLIPPER FAIL\n# DONE\n":"# FLIPPER PASS\n# DONE\n";
 while(*s)*(volatile uint8_t*)0x9fbb=*s++;
 *(volatile uint8_t*)0x9fb4=0;__asm__ volatile("jmp $ffff");
#else
 printf("failures=%u\n",failures);
#endif
 return failures!=0;
}
