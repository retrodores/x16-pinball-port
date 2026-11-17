#include "flipper.h"
#include <string.h>
#ifdef __CX16__
#include <cbm.h>
#else
#include <stdio.h>
static unsigned char geometry[131072];
#endif
bool load_integer_geometry(){
#ifdef __CX16__
 uint8_t saved=*(volatile uint8_t*)0;*(volatile uint8_t*)0=8;
 cbm_k_setnam("FLIP.BIN");cbm_k_setlfs(1,8,2);
 unsigned end=(unsigned)(uintptr_t)cbm_k_load(0,(void*)0xa000);
 *(volatile uint8_t*)0=saved;return end>255;
#else
 FILE*f=fopen("direct/build/integer/FLIP.BIN","rb");if(!f)return false;
 bool ok=fread(geometry,1,sizeof geometry,f)==sizeof geometry;fclose(f);return ok;
#endif
}
// Exported original geometry, 512 orientations per flipper; no runtime trig or
// normalization for these control points. Max angular quantization ~.00119 rad.
void integer_control_points(TFlipperEdge*e,Fixed angle){
 uint32_t a=angle.raw<0?-angle.raw:angle.raw,m=e->AngleMax.raw<0?-e->AngleMax.raw:e->AngleMax.raw;
 if((angle.raw<0)!=(e->AngleMax.raw<0))a=0;
 if(a>m)a=m;
 uint16_t index=(a*511+m/2)/m;
 uint8_t side=e==&flippers::edges[1];
#ifdef __CX16__
 uint8_t saved=*(volatile uint8_t*)0;*(volatile uint8_t*)0=8+side*8+(index>>6);
 const unsigned char*p=(const unsigned char*)(0xa000+(index&63)*128);
#else
 const unsigned char*p=geometry+(side*512UL+index)*128;
#endif
 memcpy(&e->LineA,p,sizeof(line_type)*2);memcpy(&e->T1,p+sizeof(line_type)*2,sizeof(vector2));
 e->circlebase={e->RotOrigin,e->CirclebaseRadiusSq};e->circleT1={e->T1,e->CircleT1RadiusSq};
#ifdef __CX16__
 *(volatile uint8_t*)0=saved;
#endif
 e->ControlPointDirtyFlag=false;
}
