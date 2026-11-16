#include "port_types.h"
#include <stdint.h>
#ifdef __CX16__
static void out(char c) { *(volatile char*)0x9fbb=c; }
static uint32_t cycles() {
    return *(volatile uint32_t*)0x9fb8;
}
static void reset_cycles() { *(volatile char*)0x9fb8=0; }
#else
#include <stdio.h>
static void out(char c) { putchar(c); }
static uint32_t cycles() {return 0;}
static void reset_cycles() {}
#endif
static void text(const char* s) { while(*s)out(*s++); }
static void hex(uint32_t n) {
 for(int i=7;i>=0;--i) out("0123456789abcdef"[(n>>(i*4))&15]);
}
static void number(float n) { union {float f;uint32_t i;} u;u.f=n;hex(u.i);out(' '); }
static void row(int i) {text("# RESULT ");hex(i);out(' ');}
static uint32_t random_state=1;
static float rnd() {random_state=random_state*1664525UL+1013904223UL;return (float)((random_state>>16)&255)/16.0f-8.0f;}
int main() {
 text("# TAP BEGIN\n");
 for(int i=0;i<64;i++) {
  vector2 n{rnd(),rnd()};
  float mag=maths::normalize_2d(n);
  row(i);number(mag);number(n.X);number(n.Y);out('\n');
 }
 // Oriented wall; front approach, reversed/back approach, parallel and endpoint cases.
 line_type l;
 maths::line_init(l,2,-4,2,4);
 for(int i=0;i<64;i++) {
  ray_type r{};
  r.Origin={rnd(),rnd()};r.Direction={rnd(),rnd()};
  maths::normalize_2d(r.Direction);r.MaxDistance=15;r.MinDistance=.002f;
  l.RayIntersect={0,0};
  row(64+i);number(maths::ray_intersect_line(r,l));number(l.RayIntersect.X);number(l.RayIntersect.Y);out('\n');
 }
 circle_type c{{2,3},9};
 for(int i=0;i<64;i++) {
  ray_type r{};
  r.Origin={rnd(),rnd()};r.Direction={rnd(),rnd()};
  maths::normalize_2d(r.Direction);r.MaxDistance=15;r.MinDistance=.002f;
  row(128+i);number(maths::ray_intersect_circle(r,c));out('\n');
 }
 for(int i=0;i<64;i++) {
  TBall b;b.Direction={rnd(),rnd()};b.Speed=40;
  maths::normalize_2d(b.Direction);
  vector2 p{3,4},n{rnd(),rnd()};maths::normalize_2d(n);
  float e=(float)(i%5)/4.0f, smooth=.8f;
  row(192+i);number(maths::basic_collision(&b,&p,&n,e,smooth,10,6));
  number(b.Position.X);number(b.Position.Y);number(b.Direction.X);number(b.Direction.Y);number(b.Speed);out('\n');
 }
 // Cost samples are not a claim that the complete frame fits.
 ray_type r{{4,0},{-1,0},15,.002f,1};
 reset_cycles();volatile float hit=maths::ray_intersect_line(r,l);uint32_t elapsed=cycles();
 text("# LINE_CYCLES ");hex(elapsed);out('\n');
 r.Origin={-4,3};r.Direction={1,0};
 reset_cycles();hit=maths::ray_intersect_circle(r,c);elapsed=cycles();
 text("# CIRCLE_CYCLES ");hex(elapsed);out('\n');
 TBall b;b.Direction={-1,0};b.Speed=40;vector2 p{2,3},n{1,0};
 reset_cycles();hit=maths::basic_collision(&b,&p,&n,.8f,.9f,1000000000.0f,0);elapsed=cycles();
 text("# REBOUND_CYCLES ");hex(elapsed);out('\n');
 text("ok - original collision routines executed\n1..1\n");
#ifdef __CX16__
 *(volatile char*)0x9fb4=0;
 asm volatile("jmp $ffff");
#endif
 return 0;
}
