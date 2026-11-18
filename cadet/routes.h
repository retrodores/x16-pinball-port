#ifndef CADET_ROUTES_H
#define CADET_ROUTES_H
#include <stdint.h>
/* World coordinates Q8, plane slopes Q12. No floating point on target.
 * Bounds required: positions [-16,16], displacement <=32 world units.
 * This module handles directed line crossings and route state only.
 * Circles, collision response, overlap recovery and flippers remain separate. */
typedef struct { int16_t ax,ay,bx,by; uint8_t mask,active,kind,action,target,zflag; int16_t px,py,pz,z,fx,fy; } cadet_edge;
typedef struct { int16_t x,y,z,radius,px,py,pz,fx,fy; uint8_t mask,on_ramp; } cadet_ball;
enum { CADET_IGNORE,CADET_BLOCK,CADET_PASS,CADET_RAMP,CADET_EVENT };
uint8_t cadet_crosses(const cadet_edge*,int16_t,int16_t,int16_t,int16_t);
uint8_t cadet_route(const cadet_edge*,cadet_ball*);
#endif
