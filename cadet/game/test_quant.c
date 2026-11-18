#include <stdint.h>
#include <cbm.h>
extern uint16_t fastsqrt(uint32_t);
extern uint8_t depth_quant(uint32_t);
static void text(const char*s){while(*s)*(volatile uint8_t*)0x9fbb=*s++;}
int main(void){
 *(volatile uint8_t*)0=11;cbm_k_setnam("UI.BIN");cbm_k_setlfs(1,8,2);
 if((uintptr_t)cbm_k_load(0,(void*)0xa000)<256)goto fail;
 for(uint16_t n=4000;n<9500;++n){
  uint32_t sq=(uint32_t)n*n+n/2;uint16_t root=fastsqrt(sq);
  uint32_t scaled=root<=4992?0:(uint32_t)(root-4992)*4304;
  uint16_t q=scaled<1438?0:(scaled-1438)>>16;if(q>255)q=255;
  if(depth_quant(sq)!=q)goto fail;
 }
 text("# QUANT PASS 5500 distances\n# DONE\n");goto done;
fail:text("# QUANT FAIL\n# DONE\n");
done:*(volatile uint8_t*)0x9fb4=0;__asm__ volatile("jmp $ffff");return 0;
}
