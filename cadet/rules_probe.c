#ifdef __CC65__
#pragma charmap (0x41, 0x41)
#pragma charmap (0x42, 0x42)
#pragma charmap (0x43, 0x43)
#pragma charmap (0x44, 0x44)
#pragma charmap (0x45, 0x45)
#pragma charmap (0x46, 0x46)
#pragma charmap (0x47, 0x47)
#pragma charmap (0x48, 0x48)
#pragma charmap (0x49, 0x49)
#pragma charmap (0x4a, 0x4a)
#pragma charmap (0x4b, 0x4b)
#pragma charmap (0x4c, 0x4c)
#pragma charmap (0x4d, 0x4d)
#pragma charmap (0x4e, 0x4e)
#pragma charmap (0x4f, 0x4f)
#pragma charmap (0x50, 0x50)
#pragma charmap (0x51, 0x51)
#pragma charmap (0x52, 0x52)
#pragma charmap (0x53, 0x53)
#pragma charmap (0x54, 0x54)
#pragma charmap (0x55, 0x55)
#pragma charmap (0x56, 0x56)
#pragma charmap (0x57, 0x57)
#pragma charmap (0x58, 0x58)
#pragma charmap (0x59, 0x59)
#pragma charmap (0x5a, 0x5a)
#pragma charmap (0x61, 0x61)
#pragma charmap (0x62, 0x62)
#pragma charmap (0x63, 0x63)
#pragma charmap (0x64, 0x64)
#pragma charmap (0x65, 0x65)
#pragma charmap (0x66, 0x66)
#pragma charmap (0x67, 0x67)
#pragma charmap (0x68, 0x68)
#pragma charmap (0x69, 0x69)
#pragma charmap (0x6a, 0x6a)
#pragma charmap (0x6b, 0x6b)
#pragma charmap (0x6c, 0x6c)
#pragma charmap (0x6d, 0x6d)
#pragma charmap (0x6e, 0x6e)
#pragma charmap (0x6f, 0x6f)
#pragma charmap (0x70, 0x70)
#pragma charmap (0x71, 0x71)
#pragma charmap (0x72, 0x72)
#pragma charmap (0x73, 0x73)
#pragma charmap (0x74, 0x74)
#pragma charmap (0x75, 0x75)
#pragma charmap (0x76, 0x76)
#pragma charmap (0x77, 0x77)
#pragma charmap (0x78, 0x78)
#pragma charmap (0x79, 0x79)
#pragma charmap (0x7a, 0x7a)
#endif
#include "rules.h"
#include <string.h>
#ifndef __CX16__
#include <stdio.h>
#define EMIT(c) putchar(c)
#else
#define EMIT(c) (*(volatile uint8_t*)0x9fbb=(c))
#endif
static void text(const char*s) { while(*s) { EMIT(*s); ++s; } }
static void hex(uint32_t n) {
    uint8_t i;
    for(i=0;i<8;++i) { EMIT("0123456789abcdef"[(uint8_t)(n>>28)]); n<<=4; }
}
static uint8_t failed=0,tests=0;
static void check(uint8_t ok,const char*s) {
    ++tests; if(!ok) ++failed;
    text(ok?"ok - ":"not ok - "); text(s); text("\n");
}
static cadet_score score;
int main(void) {
    uint16_t i;
    uint32_t cycles=0;

#ifdef __CX16__
    uint8_t timer[4];
#endif
    uint8_t good;
    text("# TAP BEGIN\n");
    check(cadet_bumper_award(0,0)==500&&cadet_bumper_award(0,3)==2000,"attack bumper levels from original control.cpp");
    check(cadet_bumper_award(1,0)==1500&&cadet_bumper_award(1,3)==4500,"launch bumper levels from original control.cpp");
    check(cadet_rebounder_award()==500,"original rebounder award");
    memset(&score,0,sizeof(score));
    cadet_add_score(&score,0xffffffffUL);cadet_add_score(&score,1);
    check(score.bytes[4]==1&&score.bytes[0]==0&&score.bytes[3]==0,"carry beyond 32 bits");
    memset(&score,0xff,sizeof(score));score.overflow=0;cadet_add_score(&score,1);
    good=score.overflow;for(i=0;i<16;++i) if(score.bytes[i]!=255)good=0;
    check(good,"128-bit overflow saturates explicitly");
    memset(&score,0,sizeof(score));
#ifdef __CX16__
    *(volatile uint8_t*)0x9fb8=0;
#endif
    for(i=0;i<1000;++i) {
        cadet_add_score(&score,cadet_bumper_award(i&1,(i>>1)&3));
        cadet_add_score(&score,cadet_rebounder_award());
    }
#ifdef __CX16__
    timer[0]=*(volatile uint8_t*)0x9fb8;
    timer[1]=*(volatile uint8_t*)0x9fb9;
    timer[2]=*(volatile uint8_t*)0x9fba;
    timer[3]=*(volatile uint8_t*)0x9fbb;
    cycles=(uint32_t)timer[0]|((uint32_t)timer[1]<<8)|((uint32_t)timer[2]<<16)|((uint32_t)timer[3]<<24);
#endif
    text("# SCORE ");for(i=0;i<16;++i)hex(score.bytes[i]);text("\n# CYCLES ");hex(cycles);text("\n");
    check(score.bytes[0]==0xe8&&score.bytes[1]==0x0d&&score.bytes[2]==0x28,"1000 original bumper/rebounder pairs total 2625000");
    text("1..6\n");
#ifdef __CX16__
    *(volatile uint8_t*)0x9fb4=failed;
#ifdef __CC65__
    __asm__("jmp $ffff");
#else
    __asm__ volatile("jmp $ffff");
#endif
#endif
    return failed;
}
