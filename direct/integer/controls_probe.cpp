#include <stdint.h>
#include "controls-generated.h"
static void out(char c){*(volatile char*)0x9fbb=c;}
static void text(const char*s){while(*s)out(*s++);}
static void inject(uint8_t code){asm volatile("lda %0\njsr %1"::"r"(code),"i"(key_handler):"a","x","memory");}
int main(){
 text("# TAP BEGIN\n");
 const uint8_t codes[8]={0x2c,0x2e,0x37,0x39,0x33,0x20,0x1a,0x6e};
 const uint8_t bits[8]={16,16,32,32,1,8,2,4};
 for(uint8_t i=0;i<8;++i){
  command_keys=0;inject(codes[i]);inject(codes[i]|128);
  text(command_keys==bits[i]&&!raw_keys[codes[i]]?"ok - press/release between frames remains latched\n":"not ok - short command lost\n");
 }
 text("1..8\n");*(volatile char*)0x9fb4=0;asm volatile("jmp $ffff");
}
