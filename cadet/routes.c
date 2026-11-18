/* C/fixed-point adaptation of maths::ray_intersect_line, TOneway::Collision,
 * TRamp::Collision in the recovered SpaceCadetPinball source (MIT).
 * No normalization/division is needed to reject a finite swept crossing.
 * The original exported edges already include the ball-radius offsets. */
#include "routes.h"
static int32_t cross(int16_t ax,int16_t ay,int16_t bx,int16_t by){
 return (int32_t)ax*by-(int32_t)ay*bx;
}
uint8_t cadet_crosses(const cadet_edge*e,int16_t sx,int16_t sy,int16_t tx,int16_t ty){
 int16_t dx=tx-sx,dy=ty-sy,ex=e->bx-e->ax,ey=e->by-e->ay;
 int32_t d,n,u;
 d=cross(dx,dy,ex,ey);
 if(d>=0)return 0; /* Same directed-face test as the recovered ray function. */
 n=cross(ex,ey,sx-e->ax,sy-e->ay);
 if(n>0||n<d)return 0;
 u=cross(e->ax-sx,e->ay-sy,dx,dy);
 return u<=0&&u>=d;
}
uint8_t cadet_route(const cadet_edge*e,cadet_ball*b){
 if(!e->active||!(e->mask&b->mask))return CADET_IGNORE;
 if(e->kind!=CADET_RAMP)return e->kind;
 if(!e->action)return CADET_EVENT; /* Line1 emits an event; no layer transfer. */
 if(e->action==1){
  b->on_ramp=1;b->mask=e->target;
  b->px=e->px;b->py=e->py;b->pz=e->pz;b->fx=e->fx;b->fy=e->fy;
  b->z=(int16_t)(((int32_t)b->x*e->px+(int32_t)b->y*e->py)/4096)+b->radius+e->pz;
 }else{
  b->on_ramp=0;b->mask=e->target;
  if(e->zflag)b->z=b->radius+e->z;
 }
 return CADET_RAMP;
}
