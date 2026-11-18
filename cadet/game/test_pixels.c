#include <stdint.h>
extern void mask_pixels(uint16_t);
static volatile uint8_t*v=(volatile uint8_t*)0x9f20;
static void addr(uint8_t port,uint32_t a){v[5]=port;v[0]=a;v[1]=a>>8;v[2]=0x10|(a>>16);}
static void text(const char*s){while(*s)*(volatile uint8_t*)0x9fbb=*s++;}
int main(void){
 uint16_t masks[16];uint16_t rng=0x6502;
 static const uint8_t keep[]={0,240,15,255};
 for(uint16_t pass=0;pass<256;++pass){
  for(uint8_t y=0;y<16;++y){rng^=rng<<7;rng^=rng>>9;rng^=rng<<8;masks[y]=y==0?0:y==1?65535:rng;}
  addr(0,0x1e000);
  for(uint8_t x=0;x<128;++x)v[3]=x+pass;
  addr(1,0x1e000);addr(0,0x1e080);mask_pixels((uint16_t)(uintptr_t)masks);
  addr(0,0x1e080);
  for(uint8_t x=0;x<128;++x){
   uint8_t expected=(uint8_t)(x+pass)&keep[(masks[x/8]>>(2*(x%8)))&3];
   if(v[3]!=expected){text("# PIXELS FAIL\n# DONE\n");goto done;}
  }
 }
 text("# PIXELS PASS 32768 VERA bytes\n# DONE\n");
done:*(volatile uint8_t*)0x9fb4=0;__asm__ volatile("jmp $ffff");return 0;
}
