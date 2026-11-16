#pragma once
#include <math.h>
#include "maths.h"
// Platform shell: only the original fields used by basic_collision.
// No SDL, sprite ownership, virtual component graph or dynamic allocation.
class TBall {
public:
    vector3 Position{}, Direction{};
    float Speed=0;
};
#ifdef __CX16__
#include <stdint.h>
// LLVM-MOS has software float arithmetic but no sqrt in its math library.
// Positive finite values used by the engine; four Newton iterations.
inline float sqrt(float x) {
 if(x==0)return 0;
 union {float f; uint32_t u;} g;g.f=x;g.u=(g.u>>1)+0x1fc00000UL;
 for(unsigned char i=0;i<4;i++)g.f=.5f*(g.f+x/g.f);
 return g.f;
}
namespace std {
template<class T> T min(T a,T b) { return a<b?a:b; }
template<class T> T max(T a,T b) { return a>b?a:b; }
inline float abs(float x) { return x<0?-x:x; }
}

#else
#include <algorithm>
#endif
