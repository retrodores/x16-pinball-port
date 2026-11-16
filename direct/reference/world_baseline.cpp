#include "world.h"
#include <string.h>
#ifdef __CX16__
#include <cbm.h>
#else
#include <stdio.h>
static unsigned char model[200000];
#endif
namespace world {
TBall ball;
bool drained=false;
uint16_t contacts=0;
static uint16_t cell[64],last_cell=65535;
static Edge edge,best_edge;
static void read_record(uint8_t bank,uint16_t offset,void* destination,uint8_t size) {
#ifdef __CX16__
 uint8_t saved=*(volatile uint8_t*)0;
 *(volatile uint8_t*)0=bank;
 memcpy(destination,(const void*)(0xa000+offset),size);
 *(volatile uint8_t*)0=saved;
#else
 memcpy(destination,model+((uint32_t)(bank-32)*8192)+offset,size);
#endif
}
bool load() {
#ifdef __CX16__
 uint8_t saved=*(volatile uint8_t*)0;
 *(volatile uint8_t*)0=32;
 cbm_k_setnam("WORLD.BIN");cbm_k_setlfs(1,8,2);
 cbm_k_load(0,(void*)0xa000);
 *(volatile uint8_t*)0=32;
 bool ok=*(volatile uint16_t*)0xa07e==0x5843;
 *(volatile uint8_t*)0=saved;return ok;
#else
 FILE* f=fopen("direct/build/WORLD.BIN","rb");if(!f)return false;
 bool ok=fread(model,1,sizeof model,f)>0;fclose(f);return ok;
#endif
}
void launch() {
 // Settled at the original plunger collision line, full boost with the
 // original random multiplier held at its midpoint for reproducible traces.
 ball.Position={serve_x,plunger_y-.0005f};
 ball.Direction={0,-1};ball.Speed=105;
 drained=false;contacts=0;last_cell=65535;
}
static float nearest(ray_type& ray) {
 int gx=(int)(ray.Origin.X+12),gy=(int)(ray.Origin.Y+16);
 if(gx<0||gx>=24||gy<0||gy>=32)return 1e9f;
 uint16_t ci=gx+gy*24;
 if(ci!=last_cell){read_record(32+(ci>>6),(ci&63)*128,cell,128);last_cell=ci;}
 float distance=1e9f;
 for(uint8_t i=0;i<cell[0];++i) {
  uint16_t id=cell[i+1];read_record(44+(id>>6),(id&63)*128,&edge,sizeof edge);
  float d=edge.type?maths::ray_intersect_circle(ray,edge.shape.circle):maths::ray_intersect_line(ray,edge.shape.line);
  if(d<distance){distance=d;best_edge=edge;}
 }
 return distance;
}
void frame(float dt) {
 if(drained)return;
 // TTableLayer::FieldEffect with RandFloat fixed to .5 in this diagnostic.
 if(dt>.01f && ball.Speed<.8f)dt=.01f;
 vector2 force{gravity_x-ball.Direction.X*ball.Speed*drag,gravity_y-ball.Direction.Y*ball.Speed*drag};
 ball.Direction.X=ball.Direction.X*ball.Speed+force.X*dt;
 ball.Direction.Y=ball.Direction.Y*ball.Speed+force.Y*dt;
 ball.Speed=maths::normalize_2d(ball.Direction);
 if(ball.Speed>ball_radius*200)ball.Speed=ball_radius*200;
 const float half=ball_radius*.5f;
 const float travel=ball.Speed*dt;
 // Same half-radius subdivision and ray/rebound sequence as pb::timed_frame.
 int steps=(int)(travel/half);
 if(steps*half<travel)++steps;
 ray_type ray{};ray.MinDistance=.002f;ray.CollisionMask=1;
 for(int step=0;step<steps;++step) {
  float sum=0;
  for(uint8_t guard=0;guard<16 && sum<half;++guard) {
   ray.Origin=ball.Position;ray.Direction=ball.Direction;
   ray.MaxDistance=step==steps-1?travel-step*half:half;
   float distance=nearest(ray);
   if(distance>=1e9f) {
    ball.Position.X+=ray.MaxDistance*ray.Direction.X;
    ball.Position.Y+=ray.MaxDistance*ray.Direction.Y;break;
   }
   vector2 p,n;
   if(best_edge.type) {
    p={distance*ball.Direction.X+ball.Position.X,distance*ball.Direction.Y+ball.Position.Y};
    n=maths::vector_sub(p,best_edge.shape.circle.Center);maths::normalize_2d(n);
   } else {p=best_edge.shape.line.RayIntersect;n=best_edge.shape.line.PerpendicularC;}
   if(best_edge.kind==2){drained=true;return;}
   maths::basic_collision(&ball,&p,&n,best_edge.elasticity,best_edge.smoothness,best_edge.threshold,best_edge.boost);
   ++contacts;
   if(distance<=0)break;
   sum+=distance;
  }
 }
}
}
