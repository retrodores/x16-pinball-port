#include "world.h"
#include <string.h>
#include "edge_bounds.h"
#include "flipper.h"
#include "plunger.h"
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
static bool mechanisms=false,previous_input[3]={false,false,false};
static uint8_t best_flipper=255;
static uint16_t cell[64],last_cell=65535;

static Edge edge,best_edge;
// A tiny unbanked cache avoids repeated KERNAL-window copies for nearby contacts.
static Edge cache;
static uint16_t cache_id=65535;
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
 cache_id=65535;
 last_cell=65535;
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
 mechanisms=false;ball.ActiveFlag=true;ball.CollisionMask=1;
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
 // Each world ray travels at most half a ball radius. Integer bounds only
 // reject impossible contacts; the accepted primitive uses original floats.
 // 41/256 covers .15 travel, .002 backwards tolerance and rounding.
 int16_t qx=(int16_t)(ray.Origin.X*256),qy=(int16_t)(ray.Origin.Y*256);
 float distance=1e9f;
 for(uint8_t i=0;i<cell[0];++i) {
  uint16_t id=cell[i+1];int16_t b[4];read_record(edge_bounds_bank,id*8,b,8);
  if(qx+41<b[0]||qy+41<b[1]||qx-41>b[2]||qy-41>b[3])continue;
  if(cache_id!=id){read_record(44+(id>>6),(id&63)*128,&cache,sizeof edge);cache_id=id;}
  Edge& candidate=cache;
  float d=candidate.type?maths::ray_intersect_circle(ray,candidate.shape.circle):maths::ray_intersect_line(ray,candidate.shape.line);
  if(d<distance){distance=d;best_edge=candidate;}
 }
 best_flipper=255;
 if(mechanisms){uint8_t which=255;float d=flippers::nearest(ray,which);if(d<distance){best_flipper=which;distance=d;}}
 return distance;
}
void start(){
 mechanisms=true;drained=false;contacts=0;last_cell=65535;
 for(uint8_t i=0;i<3;++i)previous_input[i]=false;
 flippers::reset();plunger::reset(ball);plunger::feed();
}
void input(bool left,bool right,bool pullback){
 bool next[3]={left,right,pullback};
 for(uint8_t i=0;i<3;++i)if(next[i]!=previous_input[i]){
  if(i<2)flippers::set(i,next[i]);else plunger::input(next[i]);
  previous_input[i]=next[i];
 }
}
// Match upstream options::DefUps=120: two simulation updates per display frame.
void preview_tick(){for(uint8_t i=0;i<2;++i){frame(1.f/120.f);if(mechanisms)plunger::advance_half_frame();}}
void tick(){frame(1.0f/60.0f);if(mechanisms)plunger::advance_frame();}
void frame(float dt) {
 if(drained&&!mechanisms)return;
 float frame_dt=dt;
 float travel=0;int steps=0;
 const float half=ball_radius*.5f;
 if(ball.ActiveFlag){
  // TTableLayer::FieldEffect, with deterministic midpoint noise.
  if(dt>.01f && ball.Speed<.8f)dt=.01f;
  vector2 force{gravity_x-ball.Direction.X*ball.Speed*drag,gravity_y-ball.Direction.Y*ball.Speed*drag};
  ball.Direction.X=ball.Direction.X*ball.Speed+force.X*dt;
  ball.Direction.Y=ball.Direction.Y*ball.Speed+force.Y*dt;
  ball.Speed=maths::normalize_2d(ball.Direction);
  if(ball.Speed>ball_radius*200)ball.Speed=ball_radius*200;
  travel=ball.Speed*dt;
  steps=(int)(travel/half);if(steps*half<travel)++steps;
 }
 float delta[2]={0,0};int flip_steps[2]={0,0};int maximum=steps;
 if(mechanisms)for(uint8_t i=0;i<2;++i){flip_steps[i]=flippers::steps(i,frame_dt,delta[i]);if(flip_steps[i]>maximum)maximum=flip_steps[i];}
 ray_type ray{};ray.MinDistance=.002f;ray.CollisionMask=1;
 // Match pb::timed_frame: each ball substep, then each moving flipper substep.
 for(int step=0;step<maximum;++step) {
  if(ball.ActiveFlag&&step<steps){
   float sum=0;
   for(uint8_t guard=0;guard<16 && sum<half;++guard) {
    ray.Origin=ball.Position;ray.Direction=ball.Direction;
    ray.MaxDistance=step==steps-1?travel-step*half:half;
    float distance=nearest(ray);
    if(distance>=1e9f) {
     ball.Position.X+=ray.MaxDistance*ray.Direction.X;
     ball.Position.Y+=ray.MaxDistance*ray.Direction.Y;break;
    }
    if(best_flipper!=255){flippers::edges[best_flipper].EdgeCollision(&ball,distance);++flippers::contacts;}
    else{
     vector2 p,n;
     if(best_edge.type) {
      p={distance*ball.Direction.X+ball.Position.X,distance*ball.Direction.Y+ball.Position.Y};
      n=maths::vector_sub(p,best_edge.shape.circle.Center);maths::normalize_2d(n);
     } else {p=best_edge.shape.line.RayIntersect;n=best_edge.shape.line.PerpendicularC;}
     if(best_edge.kind==2){drained=true;ball.ActiveFlag=false;ball.CollisionMask=0;break;}
     if(mechanisms&&best_edge.kind==1)plunger::instance.Collision(&ball,&p,&n,distance,nullptr);
     else maths::basic_collision(&ball,&p,&n,best_edge.elasticity,best_edge.smoothness,best_edge.threshold,best_edge.boost);
    }
    ++contacts;
    if(distance<=0)break;
    sum+=distance;
   }
  }
  if(mechanisms)for(uint8_t i=0;i<2;++i)if(step<flip_steps[i])flippers::advance(i,delta[i],ball);
 }
}
}
