#include "flipper.h"
#include "flipper_params.h"
static NativeTable native_table{};
namespace pb {NativeTable* MainTable=&native_table;}
namespace flippers {
TFlipperEdge edges[2];
static TFlipper controllers[2];
unsigned short contacts=0;
void reset() {
 for(unsigned char i=0;i<2;++i)edges[i]=TFlipperEdge{};
 initialize_flippers(edges);contacts=0;
 for(unsigned char i=0;i<2;++i){edges[i].set_control_points(0);controllers[i].FlipperEdge=&edges[i];controllers[i].MessageField=0;}
}
void set(unsigned char index,bool pressed) {
 if(index>=2)return;
 controllers[index].MessageField=edges[index].SetMotion(pressed?MessageCode::TFlipperExtend:MessageCode::TFlipperRetract);
}
int steps(unsigned char index,float dt,float& delta){return controllers[index].GetFlipperStepAngle(dt,&delta);}
void advance(unsigned char index,float delta,TBall& ball) {
 native_table.BallList[0]=&ball;
 vector2 previous=ball.Position;
 controllers[index].FlipperCollision(delta);
 if(ball.Position!=previous)++contacts;
}
float nearest(const ray_type& ray,unsigned char& index) {
 float distance=1e9f;
 for(unsigned char i=0;i<2;++i){
  auto& e=edges[i];
  // These are the original expanded bounds used by TFlipper::FlipperCollision.
  // Include ray travel when querying from the ball subdivision loop.
  if(ray.Origin.X+ray.MaxDistance<e.XMin||ray.Origin.X-ray.MaxDistance>e.XMax||
     ray.Origin.Y+ray.MaxDistance<e.YMin||ray.Origin.Y-ray.MaxDistance>e.YMax)continue;
  float d=e.FindCollisionDistance(ray);
  if(d<distance){distance=d;index=i;}
 }
 return distance;
}
}
