#include "engine.h"
#include <cstdio>
int main(){if(!pin::load())return 1;pin::start();unsigned gi=0,gf=0,drains=0,returns=0;const unsigned charge[3]={80,73,78},lp[3]={53,50,96},rp[3]={67,56,102};for(unsigned f=0;f<18000;++f){auto&g=pin::game;pin::frame(gf%lp[gi]<12,gf%rp[gi]<12,g.state==pin::Serving&&g.charge<charge[gi]);if(f%120==0)printf("# PLAY %08x %08x %08x %08x %08x\n",f,(uint32_t)g.x,(uint32_t)g.y,g.state,g.drains);++gf;if(g.state==pin::GameOver){drains+=g.drains;returns+=g.returns;if(++gi==3){printf("# FINISHED %u %u %u\n",f+1,drains,returns);return 0;}pin::start();gf=0;}}return 1;}
