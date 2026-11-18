// Includes the production solver so the test exercises its actual swept contacts.
#define PIN_TEST
#include "engine.cpp"
#include <cstdio>
using namespace pin;
static bool inside(){for(uint8_t i=0;i<8;++i){Edge e=edge(i);if(dot(game.x-e.x,game.y-e.y,e.nx,e.ny)<-6)return false;}return true;}
int main(){if(!load())return 2;unsigned tested=0,failed=0;for(uint8_t i=0;i<8;++i){Edge e=edge(i);if(e.kind==Drain)continue;
 for(int f=1;f<256;f+=5)for(int shift=-128;shift<=128;shift+=32){
  start();int16_t x=e.x+mul(e.ex-e.x,f)/256+e.nx/16,y=e.y+mul(e.ey-e.y,f)/256+e.ny/16;
  int16_t vx=-e.nx*48+e.ny*shift/4,vy=-e.ny*48-e.nx*shift/4;
  place(x,y,vx,vy);if(!inside())continue;++tested;
  for(uint8_t t=0;t<12;++t){frame(false,false,false);if(game.escapes||(game.state==InPlay&&!inside())){if(failed<10)printf("ESCAPE edge=%u f=%d shift=%d t=%u xy=%d,%d v=%d,%d\n",i,f,shift,t,game.x,game.y,game.vx,game.vy);++failed;break;}if(game.state!=InPlay)break;}
 }}printf("Perimeter swept shots: %u tested, %u escaped\n",tested,failed);return failed?1:0;}
