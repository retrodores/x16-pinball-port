#include "fixed.h"
#ifdef __CX16__
static void out(char c){*(volatile char*)0x9fbb=c;}
#else
#include <stdio.h>
static void out(char c){putchar(c);}
#endif
static void text(const char*s){while(*s)out(*s++);}
static void check(bool ok,const char*s){text(ok?"ok - ":"not ok - ");text(s);out('\n');}
int main(){
 text("# TAP BEGIN\n");bool ok=true;
 for(uint16_t a=0;a<256;++a){uint32_t expected=0;for(uint16_t b=0;b<256;++b){if(mul16(a,b)!=expected)ok=false;expected+=a;}}
 check(ok,"all 65536 byte products against repeated addition");
 ok=true;uint32_t state=0x91e5a381;
 for(unsigned n=0;n<4096;++n){
  state=state*1664525UL+1013904223UL;uint16_t a=state>>16;
  state=state*1664525UL+1013904223UL;uint16_t b=state>>16;
  uint32_t expected=0,v=a;uint16_t bits=b;
  for(uint8_t i=0;i<16;++i){if(bits&1)expected+=v;bits>>=1;v<<=1;}
  if(mul16(a,b)!=expected)ok=false;
 }
 check(ok,"4096 wide products against shift/add oracle");
 check(mul16(65535,65535)==0xfffe0001UL,"maximum product and carries");
 check((Fixed::bits(-12345)*Fixed::bits(4321)).raw==-13023,"signed fixed multiplication");
 check((Fixed::bits(-12345)/Fixed::bits(4321)).raw==-11702,"signed fixed division");
 check(integer_sqrt(0)==0&&integer_sqrt(1)==1&&integer_sqrt(4294967295UL)==65535,"integer square root endpoints");
 text("1..6\n");
#ifdef __CX16__
 *(volatile char*)0x9fb4=0;asm volatile("jmp $ffff");
#endif
}
