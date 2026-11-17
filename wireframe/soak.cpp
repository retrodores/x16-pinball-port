#include "engine.h"
#include <cstdio>
#include <cstdlib>
#include <algorithm>
int main(){if(!pin::load())return 2;unsigned stuck=0,drains=0,returns=0;
for(int run=0;run<120;++run){pin::start();int slow=0,maxslow=0,oldx=0,oldy=0;for(int f=0;f<18000;++f){auto&g=pin::game;bool launch=g.state==pin::Serving&&(g.charge<60+run%41);bool flip=run%3&&g.state==pin::InPlay;pin::frame(flip&&f%(37+run)<12,flip&&f%(43+run)<12,launch);if(f%60==0){int motion=std::abs(g.x-oldx)+std::abs(g.y-oldy);if(g.state==pin::InPlay&&motion<30)++slow;else slow=0;maxslow=std::max(slow,maxslow);oldx=g.x;oldy=g.y;}if(slow>8){++stuck;printf("STUCK run=%d f=%d x=%d y=%d v=%d,%d mask=%d ramp=%d param=%d hits=%u guard=%u\n",run,f,g.x,g.y,g.vx,g.vy,g.mask,g.ramp,g.param,g.contacts,g.guard_hits);break;}if(g.state==pin::GameOver){printf("DONE run=%d f=%d bump=%u paddle=%u targets=%u returns=%u guard=%u\n",run,f,g.bumper_hits,g.flipper_hits,g.target_hits,g.returns,g.guard_hits);break;}if(f==17999){++stuck;printf("TIME run=%d x=%d y=%d mask=%d slow=%d\n",run,g.x,g.y,g.mask,maxslow);}}drains+=pin::game.drains;returns+=pin::game.returns;}
printf("SUMMARY stuck=%u drains=%u returns=%u\n",stuck,drains,returns);return stuck?1:0;}
