#include "engine.h"
#include "model.h"
#include <string.h>
#ifdef __CX16__
#include <cbm.h>
extern "C" uint32_t fastmul8(uint16_t,uint8_t);
extern "C" uint16_t fastsqrt(uint32_t);
extern "C" uint32_t fastmul16(uint16_t,uint16_t);
extern "C" void audio_effect(uint8_t);
extern "C" void audio_stop();
#else
#include <stdio.h>
static uint8_t model[440000];
#endif
namespace pin {
Game game;static uint16_t ramp_ignored[8];static uint8_t ramp_ignore_count;
static uint8_t active[160],active_flags[160],active_count;
static void touch(uint8_t c){if(!active_flags[c]){active_flags[c]=1;active[active_count++]=c;}}
static uint16_t cell[128],cell_id=65535;
#ifndef __CX16__
static uint16_t cache_id[16];static Edge cache[16];
#endif
static int16_t ax(int16_t x){return x<0?-x:x;}
__attribute__((noinline)) static int32_t mul(int16_t a,int16_t b){
#ifdef __CX16__
 uint16_t aa=ax(a),bb=ax(b);uint32_t p;if(!aa||!bb)return 0;if(bb<256)p=fastmul8(aa,bb);else if(bb==256)p=(uint32_t)aa<<8;else if(aa<256)p=fastmul8(bb,aa);else p=fastmul16(aa,bb);return (a<0)!=(b<0)?-(int32_t)p:(int32_t)p;
#else
 return (int32_t)a*b;
#endif
}
static uint32_t umul(uint16_t a,uint16_t b){
#ifdef __CX16__
 return fastmul16(a,b);
#else
 return (uint32_t)a*b;
#endif
}
static uint32_t wide_mul(uint32_t a,uint16_t b){return umul(a,b)+((uint32_t)((uint16_t)(a>>16)*b)<<16);}

// Exact signed division over the 16-bit input range, using reciprocal products.
static int16_t div60(int16_t v){uint16_t q=umul(v<0?-(int32_t)v:v,34953)>>21;return v<0?-q:q;}
static int16_t div120(int16_t v){uint16_t q=umul(v<0?-(int32_t)v:v,34953)>>22;return v<0?-q:q;}
static int16_t div300(int16_t v){uint16_t q=umul(v<0?-(int32_t)v:v,55925)>>24;return v<0?-q:q;}
static int16_t dot(int16_t x,int16_t y,int16_t nx,int16_t ny){if(!ny){if(nx==256)return x;if(nx== -256)return -x;}if(!nx){if(ny==256)return y;if(ny== -256)return -y;}return (mul(x,nx)+mul(y,ny))/256;}
// Exact floor(256*n/d), bounded to a unit fraction; no 32-bit division.
__attribute__((noinline)) static uint16_t fraction(uint16_t n,uint16_t d){if(!n)return 0;if(n>=d)return 256;uint16_t q=0;for(uint8_t i=0;i<8;++i){n<<=1;q<<=1;if(n>=d){n-=d;++q;}}return q;}
static uint16_t fraction_wide(uint32_t n,uint32_t d){if(n<32768&&d<32768)return fraction(n,d);if(n>=d)return 256;uint16_t q=0;for(uint8_t i=0;i<8;++i){n<<=1;q<<=1;if(n>=d){n-=d;++q;}}return q;}
static int16_t normal(int16_t n,uint16_t d){int16_t q=fraction(ax(n),d);return n<0?-q:q;}
static uint16_t isqrt(uint32_t n){
#ifdef __CX16__
 return fastsqrt(n);
#else
 uint32_t r=0,b=1UL<<30;while(b>n)b>>=2;while(b){if(n>=r+b){n-=r+b;r=(r>>1)+b;}else r>>=1;b>>=2;}return r;
#endif
}
static void read(uint8_t bank,uint16_t offset,void*d,uint16_t n){
#ifdef __CX16__
 uint8_t saved=*(volatile uint8_t*)0;*(volatile uint8_t*)0=bank;memcpy(d,(void*)(0xa000+offset),n);*(volatile uint8_t*)0=saved;
#else
 memcpy(d,model+(uint32_t)(bank-3)*8192+offset,n);
#endif
}
bool load(){cell_id=65535;
#ifndef __CX16__
 for(auto&i:cache_id)i=65535;
#endif
#ifdef __CX16__
 *(volatile uint8_t*)0=3;cbm_k_setnam("MODEL.BIN");cbm_k_setlfs(1,8,2);bool ok=(uintptr_t)cbm_k_load(0,(void*)0xa000)>255;*(volatile uint8_t*)0=5;ok=ok&&*(volatile uint16_t*)0xbffe==0x4657;*(volatile uint8_t*)0=0;return ok;
#else
 FILE*f=fopen("wireframe/build/MODEL.BIN","rb");if(!f)return false;bool ok=fread(model,1,sizeof model,f)>0;fclose(f);return ok;
#endif
}
void sound(uint8_t id){game.last_sound=id;
#if defined(__CX16__) && defined(PIN_AUDIO)
 if(id==255)audio_stop();else audio_effect(id);
#endif
}
void add_score(uint16_t n){if(game.overflow)return;uint16_t carry=n;for(uint8_t i=0;i<16&&carry;++i){uint16_t sum=game.score[i]+(carry&255);carry=(carry>>8)+(sum>>8);}if(carry){game.overflow=true;return;}carry=n;for(uint8_t i=0;i<16&&carry;++i){uint16_t sum=game.score[i]+(carry&255);game.score[i]=sum;carry=(carry>>8)+(sum>>8);}if(carry){game.overflow=true;return;}carry=n;for(uint8_t i=0;i<40&&carry;++i){uint8_t add=carry%10;carry/=10;uint8_t d=game.digits[i]+add;if(d>=10){d-=10;++carry;}game.digits[i]=d;}}
static void serve(){sound(255);game.state=Serving;game.x=serve_x;game.y=plunger_y-2;game.z=77;game.vx=game.vy=game.remx=game.remy=game.accx=game.accy=0;game.mask=1;game.ramp=false;game.charge=0;game.flags=0;game.nudges=0;}
void start(){active_count=0;memset(active_flags,0,sizeof active_flags);memset(&game,0,sizeof game);game.balls=3;game.multiplier=1;serve();}
static void drain(){if(game.state!=InPlay)return;game.state=Between;game.wait=120;game.vx=game.vy=0;game.mask=0;game.ramp=false;++game.drains;if(game.balls)--game.balls;sound(5);}
static void limit(){const int16_t cap=15360;int16_t m=ax(game.vx)>ax(game.vy)?ax(game.vx):ax(game.vy);if(m>cap){game.vx=(int32_t)game.vx*cap/m;game.vy=(int32_t)game.vy*cap/m;}}
static int16_t rebound(int16_t nx,int16_t ny,uint8_t e,uint8_t boost,int16_t ux=0,int16_t uy=0){
 int16_t inward=dot(game.vx-ux,game.vy-uy,nx,ny);if(inward>=0)return 0;
 int32_t impulse=umul(-(int32_t)inward,256+e)/256+(int16_t)boost*256;
 if(impulse>30000)impulse=30000;
 int32_t vx=game.vx+mul((int16_t)impulse,nx)/256,vy=game.vy+mul((int16_t)impulse,ny)/256;game.vx=vx>15360?15360:vx< -15360?-15360:vx;game.vy=vy>15360?15360:vy< -15360?-15360:vy;return -inward;
}
struct Hit {uint16_t id;int16_t t,nx,ny,x,y;bool circle;};
static Edge& edge(uint16_t id){
#ifdef __CX16__
 *(volatile uint8_t*)0=14+(id>>8);asm volatile("":::"memory");return *(Edge*)(0xa000+(id&255)*32);
#else
 uint8_t slot=id&15;if(cache_id[slot]!=id){read(14+(id>>8),(id&255)*32,&cache[slot],32);cache_id[slot]=id;}return cache[slot];
#endif
}

static bool occupied(int16_t dx,int16_t dy){
 int16_t lo=(game.x+(dx<0?dx:0)+3072-4)/16,hi=(game.x+(dx>0?dx:0)+3072+4)/16;
 int16_t top=(game.y+(dy<0?dy:0)+4096-4)/16,bottom=(game.y+(dy>0?dy:0)+4096+4)/16;
 if(lo<0||hi>=384||top<0||bottom>=512)return true;
 uint8_t left=lo&7,right=hi&7;uint16_t first=lo>>3,last=hi>>3;
 uint8_t base=occupancy_bank+(game.mask==2?3:game.mask==4?6:0);
#ifdef __CX16__
 uint8_t saved=*(volatile uint8_t*)0;
#endif
 bool found=false;
 for(int16_t y=top;y<=bottom&&!found;++y){uint16_t offset=y*48+first;
  for(uint16_t b=first;b<=last;++b,++offset){uint8_t mask=255;if(b==first)mask&=255<<left;if(b==last)mask&=255>>(7-right);uint8_t bits;
#ifdef __CX16__
   *(volatile uint8_t*)0=base+(offset>>13);asm volatile("":::"memory");bits=*(const uint8_t*)(0xa000+(offset&8191));
#else
   read(base+(offset>>13),offset&8191,&bits,1);
#endif
   if(bits&mask){found=true;break;}
  }
 }
#ifdef __CX16__
 *(volatile uint8_t*)0=saved;
#endif
 return found;
}
static uint32_t ray_a,ray_r2,ray_ar;static uint16_t circle_ids[24];static int16_t circle_distance[24];
__attribute__((noinline)) static bool circle_hit(uint16_t id,int16_t dx,int16_t dy,Hit&hit){Edge&e=edge(id);int16_t t,nx,ny,px,py;
   int16_t sx=game.x-e.x,sy=game.y-e.y;
   uint32_t r2=(uint16_t)e.ex|((uint32_t)(uint16_t)e.ey<<16);
   uint32_t oldsq=mul(sx,sx)+mul(sy,sy);
   if(oldsq<r2)return false;
   int32_t projection=-(mul(sx,dx)+mul(sy,dy));if(projection<=0)return false;
   if(oldsq<=r2)t=0;
   else{
    // Discriminant identity: a*r*r - cross(s,v)^2. All circles are <=181 Q8
    // units and each movement component <=256: the products fit unsigned 32 bits.
    uint32_t a=ray_a;
    int32_t cross=mul(sx,dy)-mul(sy,dx);
    if(cross>65535||cross< -65535)return false;
    uint16_t cross_abs=cross<0?-cross:cross;if(ray_r2!=r2){ray_r2=r2;ray_ar=wide_mul(a,(uint16_t)r2);}uint32_t ar=ray_ar,cross2=umul(cross_abs,cross_abs);
    if(cross2>=ar)return false;
    uint32_t discriminant=ar-cross2;
    uint16_t bound=hit.t<255?hit.t+1:256;
    int32_t minimum=projection-(wide_mul(a,bound)>>8);
#ifndef PIN_REFERENCE
    if(minimum>65535||(minimum>0&&umul(minimum,minimum)>discriminant))return false;
#endif
    int32_t numerator=projection-isqrt(discriminant);
    if(numerator>a)return false;
    t=numerator<=0?0:fraction_wide(numerator,a);
   }
   if(t>hit.t||(t==hit.t&&id>=hit.id))return false;
   px=game.x+mul(dx,t)/256;py=game.y+mul(dy,t)/256;
   nx=normal(px-e.x,e.r);ny=normal(py-e.y,e.r);

 hit={id,t,nx,ny,px,py,true};return true;
}
__attribute__((noinline)) static bool nearest(int16_t dx,int16_t dy,Hit&hit){
#ifndef PIN_REFERENCE
 if(!occupied(dx,dy))return false;
#endif
 int16_t gx=(game.x+dx/2+3072)/128,gy=(game.y+dy/2+4096)/128;if(gx<0||gx>=48||gy<0||gy>=64)return false;
 uint16_t ci=gx+gy*48;if(game.mask==2)ci+=3072;else if(game.mask==4)ci+=6144;
 if(ci!=cell_id){uint16_t offset;read(3+(ci>>12),(ci&4095)*2,&offset,2);uint8_t bank=6+(offset>>13);offset&=8191;uint16_t count;read(bank,offset,&count,2);read(bank,offset,cell,(count+1)*2);cell_id=ci;}
 const int16_t xl=game.x+(dx<0?dx:0)-4,xh=game.x+(dx>0?dx:0)+4,yl=game.y+(dy<0?dy:0)-4,yh=game.y+(dy>0?dy:0)+4;const uint8_t layer=game.mask;
 bool found=false;hit.t=257;uint8_t circle_count=0;ray_a=mul(dx,dx)+mul(dy,dy);ray_r2=0;
#ifdef __CX16__
 uint8_t saved=*(volatile uint8_t*)0;
#endif
 for(uint8_t i=0;i<cell[0];++i){uint16_t id=cell[i+1];
#ifdef __CX16__
 *(volatile uint8_t*)0=bounds_bank+(id>>9);asm volatile("":::"memory");const int16_t*b=(const int16_t*)(0xa000+(id&511)*16);
#else
 int16_t buf[8];read(bounds_bank+(id>>9),(id&511)*16,buf,16);const int16_t*b=buf;
#endif
  if(xh<b[0]||yh<b[1]||xl>b[2]||yl>b[3])continue;
  uint8_t mask=b[4]&255,kind=(uint16_t)b[4]>>8,group=b[5]&255;
  if(!(mask&layer)||game.disabled[group])continue;
  if(kind==Ramp){bool ignored=false;for(uint8_t k=0;k<ramp_ignore_count;++k)if(ramp_ignored[k]==id)ignored=true;if(ignored)continue;}
  if(group==center_group&&!(game.flags&2))continue;
  if(game.ignore&&(kind==Sink||kind==Kickout||kind==Hole))continue;
  Edge&e=edge(id);int16_t t,nx,ny,px,py;
  if(!(e.flags&1)){
   int16_t delta=dot(dx,dy,e.nx,e.ny);if(delta>=0)continue;
   int16_t d0=dot(game.x-e.x,game.y-e.y,e.nx,e.ny);if(d0< -3||d0+delta>0)continue;
   t=d0<=0?0:fraction(d0,-delta);if(t>256||t>hit.t||(t==hit.t&&id>=hit.id))continue;
   px=game.x+mul(dx,t)/256;py=game.y+mul(dy,t)/256;
   if(ax(e.ex-e.x)>=ax(e.ey-e.y)){if(px<e.xlo||px>e.xhi)continue;}else if(py<e.ylo||py>e.yhi)continue;
   nx=e.nx;ny=e.ny;
  }else{
   int16_t axx=ax(game.x-e.x),ayy=ax(game.y-e.y),distance=(axx>ayy?axx+ayy/2:ayy+axx/2)-e.r;
#ifdef PIN_REFERENCE
   if(circle_hit(id,dx,dy,hit))found=true;
#else
   if(circle_count<24){uint8_t at=circle_count++;while(at&&circle_distance[at-1]>distance){circle_ids[at]=circle_ids[at-1];circle_distance[at]=circle_distance[at-1];--at;}circle_ids[at]=id;circle_distance[at]=distance;}
   else if(circle_hit(id,dx,dy,hit))found=true;
#endif
   continue;

  }
  hit={id,t,nx,ny,px,py,(bool)(e.flags&1)};found=true;
 }
 // An earlier wall/target hit shortens the sweep for all remaining circles.
 // One extra time quantum and four position units conservatively cover rounding.
 uint16_t clip_t=65535;int16_t cxl=0,cxh=0,cyl=0,cyh=0;
 for(uint8_t i=0;i<circle_count;++i){
#ifndef PIN_REFERENCE
  if(clip_t!=hit.t){clip_t=hit.t;uint16_t t=hit.t<255?hit.t+1:256;int16_t ex=mul(dx,t)/256,ey=mul(dy,t)/256;
   cxl=game.x+(ex<0?ex:0)-4;cxh=game.x+(ex>0?ex:0)+4;cyl=game.y+(ey<0?ey:0)-4;cyh=game.y+(ey>0?ey:0)+4;}
  uint16_t id=circle_ids[i];
#ifdef __CX16__
  *(volatile uint8_t*)0=bounds_bank+(id>>9);asm volatile("":::"memory");const int16_t*b=(const int16_t*)(0xa000+(id&511)*16);
#else
  int16_t buf[8];read(bounds_bank+(id>>9),(id&511)*16,buf,16);const int16_t*b=buf;
#endif
  if(cxh<b[0]||cyh<b[1]||cxl>b[2]||cyl>b[3])continue;
#endif
  if(circle_hit(circle_ids[i],dx,dy,hit))found=true;
 }
#ifdef __CX16__
 *(volatile uint8_t*)0=saved;
#endif
 return found;
}
static bool event(const Edge&e){
 uint8_t c=e.group;touch(c);bool fresh=!game.flash[c];game.flash[c]=12;
 if(e.kind==Ramp){const Meta&m=metadata[e.param];if(m.action==1){game.ramp=true;game.param=e.param;game.mask=m.mask;}else if(m.action>=2){game.ramp=false;game.mask=m.mask;if(m.zflag)game.z=m.az+77;}if(fresh)add_score(25);return false;}
 if(e.kind==Pass||e.kind==Sensor||e.kind==Spinner){if(fresh){if(e.kind==Sensor)game.lamps[c]^=1;add_score(e.kind==Spinner?100:50);sound(6);}return false;}
 if(e.kind==Drain){drain();return false;}
 if(e.kind==Sink||e.kind==Kickout||e.kind==Hole){game.captured=e.kind;game.param=e.param;game.state=Captured;game.wait=metadata[e.param].delay;game.vx=game.vy=0;add_score(500);sound(2);return false;}
 if(e.kind==Drop){game.disabled[c]=1200;if(fresh){++game.target_hits;add_score(250);sound(2);game.lamps[c]=1;for(uint8_t bank=0;bank<3;++bank){uint8_t k=bank*3;if((c==drop_groups[k]||c==drop_groups[k+1]||c==drop_groups[k+2])&&game.disabled[drop_groups[k]]&&game.disabled[drop_groups[k+1]]&&game.disabled[drop_groups[k+2]]){add_score(1000);game.flags|=2;for(auto gate:gate_groups){touch(gate);game.disabled[gate]=1200;}}}}}
 else if(e.kind==Target&&fresh){++game.target_hits;add_score(100);sound(2);}
 else if(e.kind==Bumper&&fresh){++game.bumper_hits;add_score(100);sound(2);}
 else if(e.kind==Kickback){game.vx=0;game.vy=-14080;game.disabled[c]=30;add_score(100);sound(3);return true;}
 else if(e.kind==Plunger){game.vx=0;game.vy=-10000;sound(3);return true;}
 else if(fresh)sound(6);
 return true;
}
static int16_t scaled_step(int16_t v,int16_t remain,uint8_t steps){int16_t q=div60(v);uint32_t n=umul(ax(q),remain);int16_t result=(n>>8)/steps;return q<0?-result:result;}
static void move(int16_t dx,int16_t dy,uint8_t steps){int16_t remaining=256;ramp_ignore_count=0;
 for(uint8_t guard=0;guard<5&&(dx||dy);++guard){Hit h;if(!nearest(dx,dy,h)){game.x+=dx;game.y+=dy;return;}Edge e=edge(h.id);game.x=h.x;game.y=h.y;++game.contacts;
  bool ready=!game.flash[e.group];bool solid=event(e);if(game.state!=InPlay)return;
  remaining=remaining==256?256-h.t:((uint16_t)remaining*(uint16_t)(256-h.t))/256;
  if(!solid){if(e.kind==Ramp){if(ramp_ignore_count<8)ramp_ignored[ramp_ignore_count++]=h.id;}else game.disabled[e.group]=2;game.x+=dx>0?1:dx<0?-1:0;game.y+=dy>0?1:dy<0?-1:0;}
  else{
   ramp_ignore_count=0;bool boosted=e.kind==Kickback||e.kind==Plunger;
   if(!boosted){uint8_t boost=e.kind==Bumper&&!ready?0:e.boost;int16_t inward=-dot(game.vx,game.vy,h.nx,h.ny);if(inward<e.threshold)boost=0;rebound(h.nx,h.ny,e.elastic,boost);}
   game.x+=h.nx/64;game.y+=h.ny/64;
  }
  dx=scaled_step(game.vx,remaining,steps);dy=scaled_step(game.vy,remaining,steps);

  if(guard==4)++game.guard_hits;
 }
}
static void paddle(uint8_t side,uint8_t old){
 if(game.mask!=1||game.state!=InPlay)return;const Vec&p=pivots[side];const Vec&t=tips[side][game.phase[side]];
 int16_t bx=game.x-p.x,by=game.y-p.y;if(ax(bx)>800||ax(by)>800)return;
 int16_t ux=t.x-p.x,uy=t.y-p.y;
 int32_t projection=mul(bx,ux)+mul(by,uy);int16_t f=projection<=0?0:projection>=flipper_length2?256:(projection*256)/flipper_length2;
 int16_t cx=p.x+mul(ux,f)/256,cy=p.y+mul(uy,f)/256,dx=game.x-cx,dy=game.y-cy;
 int16_t radius=156-((30*f)>>8);uint32_t sq=mul(dx,dx)+mul(dy,dy);if(sq>=(uint32_t)radius*radius)return;
 uint16_t len=isqrt(sq);int16_t nx=len?normal(dx,len):0,ny=len?normal(dy,len):-256;
 game.x=cx+mul(radius+2,nx)/256;game.y=cy+mul(radius+2,ny)/256;
 int16_t angular=(int16_t)(game.phase[side]-old)*flipper_omega[side];
 int16_t sx=-mul(angular,game.y-p.y)/256,sy=mul(angular,game.x-p.x)/256;
 if(rebound(nx,ny,192,0,sx,sy)>0){++game.flipper_hits;if(game.phase[side]>old)sound(0);}
}
static bool well_force(){
 if(game.ignore)return false;
 for(const auto&w:wells){
  if(!(game.mask&w.mask)||(w.group==center_group&&!(game.flags&2)))continue;
  int16_t dx=w.x-game.x,dy=w.y-game.y;if(ax(dx)>w.r||ax(dy)>w.r)continue;
  uint32_t sq=mul(dx,dx)+mul(dy,dy);if(sq>=(uint32_t)w.r*w.r)continue;
  uint16_t d=isqrt(sq);
  if(d<34){Edge e{};e.kind=w.kind;e.group=w.group;e.param=w.param;game.x=w.x;game.y=w.y;event(e);return true;}
  game.fx=(int32_t)dx*2560/d-game.vx;game.fy=(int32_t)dy*2560/d-game.vy;return true;
 }
 return false;
}
static void release_capture(){const Meta&m=metadata[game.param];game.state=InPlay;game.ramp=false;game.ignore=90;game.remx=game.remy=0;
 if(game.captured==Hole){game.mask=m.mask;game.z=m.az;game.vx=0;game.vy=256;}
 else{game.x=m.x;game.y=m.y;game.vx=m.vx;game.vy=m.vy;game.mask=1;game.z=77;}
 ++game.returns;sound(3);
}
__attribute__((noinline)) static void tick(bool left,bool right,bool pull,bool nudge){
 game.tick+=2;for(uint8_t k=0;k<active_count;){uint8_t i=active[k];if(game.flash[i])game.flash[i]=game.flash[i]>2?game.flash[i]-2:0;if(game.disabled[i])game.disabled[i]=game.disabled[i]>2?game.disabled[i]-2:0;if(!game.flash[i]&&!game.disabled[i]){active_flags[i]=0;active[k]=active[--active_count];}else ++k;}if(game.ignore)game.ignore=game.ignore>2?game.ignore-2:0;
 bool keys[2]={left,right};uint8_t old[2];for(uint8_t i=0;i<2;++i){old[i]=game.phase[i];if(keys[i]){if(game.phase[i]<12)game.phase[i]=game.phase[i]>6?12:game.phase[i]+6;}else if(game.phase[i])game.phase[i]=game.phase[i]<4?0:game.phase[i]-4;if(old[i]==0&&game.phase[i])sound(0);if(old[i]==12&&game.phase[i]<12)sound(1);}
 if(game.state==Between){if(game.wait){game.wait=game.wait>2?game.wait-2:0;}if(!game.wait){if(game.balls)serve();else game.state=GameOver;}return;}
 if(game.state==Captured){if(game.wait){game.wait=game.wait>2?game.wait-2:0;}if(!game.wait)release_capture();return;}
 if(game.state==Serving){if(pull){if(!(game.flags&1))sound(4);game.flags|=1;if(game.charge<100&&!(game.tick&1))++game.charge;}else if(game.flags&1){game.state=InPlay;game.vy=-(int16_t)(25+game.charge*30/100)*256;game.flags&=~1;sound(3);}return;}
 if(game.state!=InPlay)return;
 if(nudge&&!game.ignore){game.vx+=(game.nudges&1)?768:-768;game.vy-=1536;game.ignore=60;++game.nudges;}
 bool well=well_force();if(game.state!=InPlay)return;
 int16_t fx=well?game.fx:game.ramp?metadata[game.param].fx:0,fy=well?game.fy:game.ramp?metadata[game.param].fy:3068;
 game.accx+=fx;game.accy+=fy;int16_t dvx=div60(game.accx),dvy=div60(game.accy);game.vx+=dvx-div300(game.vx);game.vy+=dvy-div300(game.vy);game.accx-=dvx*60;game.accy-=dvy*60;limit();
 game.remx+=game.vx;game.remy+=game.vy;int16_t dx=div60(game.remx),dy=div60(game.remy);game.remx-=dx*60;game.remy-=dy*60;
 if(game.y>1800&&game.mask==1){
  uint8_t final[2]={game.phase[0],game.phase[1]};for(uint8_t i=0;i<2;++i)game.phase[i]=(old[i]+final[i])/2;
  int16_t before_vx=game.vx,before_vy=game.vy;move(dx/2,dy/2,2);paddle(0,old[0]);paddle(1,old[1]);
  old[0]=game.phase[0];old[1]=game.phase[1];game.phase[0]=final[0];game.phase[1]=final[1];
  if(game.state==InPlay){move(game.vx==before_vx?dx-dx/2:div120(game.vx),game.vy==before_vy?dy-dy/2:div120(game.vy),2);paddle(0,old[0]);paddle(1,old[1]);}
 }else move(dx,dy,1);
 if(game.ramp){const Meta&m=metadata[game.param];game.z=dot(game.x,game.y,m.ax,m.ay)+m.az+77;}
 if(game.x< -3072||game.x>3072||game.y>3900||game.y< -4352)drain();
}
__attribute__((noinline)) void frame(bool l,bool r,bool p,bool n){
#ifdef __CX16__
 uint8_t saved=*(volatile uint8_t*)0;
#endif
 tick(l,r,p,n);
#ifdef __CX16__
 asm volatile("":::"memory");*(volatile uint8_t*)0=saved;
#endif
}
#ifdef PIN_TEST
void place(int16_t x,int16_t y,int16_t vx,int16_t vy,uint8_t mask){game.state=InPlay;game.x=x;game.y=y;game.vx=vx;game.vy=vy;game.mask=mask;game.ramp=false;game.ignore=0;game.remx=game.remy=0;}
#endif
}
