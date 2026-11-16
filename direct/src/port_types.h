#pragma once
#include <math.h>
#include <stdint.h>
#include "maths.h"
// Platform shell: only the original fields used by basic_collision.
// No SDL, sprite ownership, virtual component graph or dynamic allocation.
class TBall {
public:
    vector3 Position{}, Direction{};
    float Speed=0;
    uint16_t CollisionMask=1;
    bool ActiveFlag=true;
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
// Polynomial platform sin/cos for the flipper angle range, not a general libm.
// Horner evaluation through x^11/x^12; desktop differential tests bound error.
inline float sin(float x) {float z=x*x;return x*(1+z*(-1.0f/6+z*(1.0f/120+z*(-1.0f/5040+z*(1.0f/362880-z/39916800)))));}
inline float floor(float x) {int n=(int)x;return x<n?n-1:n;}
inline float cos(float x) {float z=x*x;return 1+z*(-1.0f/2+z*(1.0f/24+z*(-1.0f/720+z*(1.0f/40320+z*(-1.0f/3628800+z/479001600)))));}
namespace std {
template<class T> T min(T a,T b) { return a<b?a:b; }
template<class T> T max(T a,T b) { return a>b?a:b; }
inline float abs(float x) { return x<0?-x:x; }
inline float fabs(float x) { return abs(x); }
inline float sqrt(float x) { return ::sqrt(x); }
inline float ceil(float x) {int n=(int)x;return x>n?n+1:n;}
}

#else
#include <algorithm>
#endif
