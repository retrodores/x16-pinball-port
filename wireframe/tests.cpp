#include "engine.cpp"
#ifndef __CX16__
#include <stdio.h>
#endif
static void out(char c){
#ifdef __CX16__
 *(volatile uint8_t*)0x9fbb=c;
#else
 putchar(c);
#endif
}
static void text(const char*s){while(*s)out(*s++);}
static void hex(uint32_t n){for(int i=7;i>=0;--i)out("0123456789abcdef"[(n>>(i*4))&15]);}
static unsigned total=0,failed=0;
static void check(bool ok,const char*message){++total;if(!ok)++failed;text(ok?"ok - ":"not ok - ");text(message);out('\n');}
int main(){using namespace pin;text("# TAP BEGIN\n");check(load(),"model loaded");
 uint32_t seed=1;bool arithmetic=true;for(uint16_t i=0;i<256;++i){seed=seed*1664525UL+1013904223UL;uint16_t r=isqrt(seed);arithmetic=arithmetic&&umul(r,r)<=seed&&(r==65535||umul(r+1,r+1)>seed);int16_t sv=seed;arithmetic=arithmetic&&div60(sv)==sv/60&&div120(sv)==sv/120&&div300(sv)==sv/300;uint16_t d=(seed&32767)+1,n=(seed>>16)%d;arithmetic=arithmetic&&fraction(n,d)==(uint32_t)n*256/d;}check(arithmetic,"integer square roots and unit fractions match independent arithmetic bounds");
 for(uint16_t id=0;id<edge_count;++id){Edge e=edge(id);if(e.kind!=Bumper)continue;unsigned good=0;for(uint8_t side=0;side<4;++side){start();int16_t nx=side==0?1:side==2?-1:0,ny=side==1?1:side==3?-1:0;place(e.x+nx*(e.r+5),e.y+ny*(e.r+5),-nx*2048,-ny*2048,e.mask);move(-nx*6,-ny*6,6);if(game.bumper_hits&&game.vx*nx+game.vy*ny>0)++good;}
 text("# BUMPER ");hex(e.group);out(' ');hex(good);out('\n');check(good==4,"bumper rebounds from all four directions");}
 for(uint8_t side=0;side<2;++side){unsigned resting=0,swept=0;for(uint8_t k=0;k<6;++k){start();int16_t f=64+k*25,ux=tips[side][0].x-pivots[side].x,uy=tips[side][0].y-pivots[side].y;uint16_t len=isqrt(mul(ux,ux)+mul(uy,uy));int16_t nx=(int32_t)uy*256/len,ny=-(int32_t)ux*256/len;if(ny>0){nx=-nx;ny=-ny;}int16_t radius=156-((30*f)>>8),x=pivots[side].x+mul(ux,f)/256+mul(nx,radius+5)/256,y=pivots[side].y+mul(uy,f)/256+mul(ny,radius+5)/256;
 place(x,y,0,2048);tick(false,false,false,false);if(game.flipper_hits&&game.vy<0)++resting;
 start();place(x,y,0,0);tick(side==0,side==1,false,false);if(game.flipper_hits&&game.vy<0)++swept;}
 text("# PADDLE ");hex(side);out(' ');hex(resting);out(' ');hex(swept);out('\n');check(resting==6,"resting paddle rebounds falling ball");check(swept==6,"moving paddle strikes stationary ball");}
 for(const auto&w:wells){start();game.flags|=2;place(w.x,w.y,0,0,w.mask);tick(false,false,false,false);bool captured=game.state==Captured;for(uint16_t f=0;f<200&&game.state==Captured;++f)frame(false,false,false);check(captured&&game.state==InPlay&&game.returns==1,"well captures and returns ball on a bounded timer");}
 for(uint16_t id=0;id<edge_count;++id){Edge e=edge(id);if(e.kind!=Sink&&e.kind!=Kickback)continue;start();int16_t x=(e.x+e.ex)/2+e.nx/64,y=(e.y+e.ey)/2+e.ny/64;place(x,y,-e.nx*8,-e.ny*8,e.mask);tick(false,false,false,false);if(e.kind==Sink){bool captured=game.state==Captured;for(uint16_t f=0;f<200&&game.state==Captured;++f)frame(false,false,false);check(captured&&game.returns==1,"sink collision captures and ejects ball");}else check(game.vy< -8000,"side-lane kickback ejects ball upward");}
 start();place(-1100,-1100,0,0,2);game.ramp=true;game.param=0;for(uint16_t f=0;f<180;++f)frame(false,false,false);check(!game.ramp&&game.mask==1,"raised ramp rolls back through its exit without a trapped layer");
 start();for(uint8_t i=0;i<3;++i){Edge e{};e.kind=Drop;e.group=drop_groups[i];event(e);}bool open=true;for(auto gate:gate_groups)open=open&&game.disabled[gate]>0;check(open&&(game.flags&2),"target bank opens gates and enables central well");
 start();for(uint8_t i=0;i<4;++i)game.score[i]=255;const char*digits="5927694924";for(uint8_t i=0;i<10;++i)game.digits[i]=digits[i]-'0';add_score(1);bool carry=game.score[4]==1;for(uint8_t i=0;i<4;++i)carry=carry&&!game.score[i];check(carry&&game.digits[0]==6,"score carries beyond 32 bits without truncation");
 start();for(auto&b:game.score)b=255;add_score(1);bool preserved=game.overflow;for(auto b:game.score)preserved=preserved&&b==255;check(preserved,"128-bit overflow is explicit and does not wrap");
 Edge de{};for(uint16_t id=0;id<edge_count;++id){if(edge(id).kind==Drain){de=edge(id);break;}}
 start();for(uint8_t ball=0;ball<3;++ball){place((de.x+de.ex)/2+de.nx/64,(de.y+de.ey)/2+de.ny/64,-de.nx*8,-de.ny*8,de.mask);for(uint16_t f=0;f<100&&game.state!=Serving&&game.state!=GameOver;++f)frame(false,false,false);}check(game.state==GameOver&&game.drains==3&&!game.balls,"three drains finish game without a lost-ball deadlock");
 text("# COUNTS ");hex(total);out(' ');hex(failed);out('\n');text("1..");if(total>=10)out('0'+total/10);out('0'+total%10);out('\n');
#ifdef __CX16__
 *(volatile uint8_t*)0x9fb4=0;asm volatile("jmp $ffff");
#endif
 return failed?1:0;
}
