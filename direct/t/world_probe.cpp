#include "world.h"
#ifdef __CX16__
static void out(char c) { *(volatile char*)0x9fbb=c; }
static uint32_t cycles() {return *(volatile uint32_t*)0x9fb8;}
static void reset_cycles() { *(volatile char*)0x9fb8=0; }
#else
#include <stdio.h>
static void out(char c) {putchar(c);}
static uint32_t cycles() {return 0;}
static void reset_cycles() {}
#endif
static void text(const char*s){while(*s)out(*s++);}
static void hex(uint32_t n){for(int i=7;i>=0;--i)out("0123456789abcdef"[(n>>(i*4))&15]);}
static void number(float n){union{float f;uint32_t u;}v;v.f=n;hex(v.u);out(' ');}
int main(){
 text("# TAP BEGIN\n");
 if(!world::load()){text("not ok - world asset loads\n1..1\n");}
 else{
  text("ok - world asset loads\n");
  world::launch();uint32_t maximum=0;uint16_t max_frame=0;
  for(uint16_t i=0;i<240;++i){
   reset_cycles();world::frame(1.0f/60.0f);uint32_t elapsed=cycles();
   if(elapsed>maximum){maximum=elapsed;max_frame=i;}
   if(true){
    text("# WORLD ");hex(i);out(' ');number(world::ball.Position.X);number(world::ball.Position.Y);
    number(world::ball.Direction.X);number(world::ball.Direction.Y);number(world::ball.Speed);
    hex(world::contacts);out('\n');
   }
   if(world::drained)break;
  }
  text("# MAX_FRAME_CYCLES ");hex(maximum);out(' ');hex(max_frame);out('\n');
  text("ok - original-world launch trace completed\n1..2\n");
 }
#ifdef __CX16__
 *(volatile char*)0x9fb4=0;asm volatile("jmp $ffff");
#endif
 return 0;
}
