#include <stdint.h>
extern uint16_t fraction8(uint16_t,uint16_t);
extern int32_t signedmul(int16_t,int16_t);
static void text(const char*s){while(*s)*(volatile uint8_t*)0x9fbb=*s++;}
static uint16_t rng=0x51a7;
static uint16_t next(void){rng^=rng<<7;rng^=rng>>9;rng^=rng<<8;return rng;}
static uint8_t check(int16_t a,int16_t b){return signedmul(a,b)==(int32_t)a*b;}
int main(void){
 static const int16_t values[]={-32768,-32767,-256,-255,-1,0,1,255,256,32767};
 for(uint8_t i=0;i<10;++i)for(uint8_t j=0;j<10;++j)if(!check(values[i],values[j]))goto bad;
 for(uint16_t i=0;i<8192;++i)if(!check(next(),next()))goto bad;
 for(uint16_t d=1;d<32768;d+=17){uint16_t n=next()%d;if(fraction8(n,d)!=(uint32_t)n*256/d)goto bad;if(fraction8(d,d)!=256)goto bad;}
 text("# MATH PASS 8292 products + 3856 fractions\n");goto done;
bad:text("# MATH FAILED\n");
done:*(volatile uint8_t*)0x9fb4=0;__asm__ volatile("jmp $ffff");return 0;
}
