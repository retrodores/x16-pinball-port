#include <stdint.h>
#include <cbm.h>
extern void music_reset(void);
extern uint8_t lz_byte(void),music_byte(void);
extern void music_prefetch(void);
extern volatile uint8_t music_enabled;
extern volatile uint8_t music_error;
static void text(const char*s){while(*s)*(volatile uint8_t*)0x9fbb=*s++;}
static uint8_t load(const char*n,uint8_t bank){*(volatile uint8_t*)0=bank;cbm_k_setnam(n);cbm_k_setlfs(1,8,2);return(uintptr_t)cbm_k_load(0,(void*)0xa000)>255;}
int main(void){
 for(uint8_t i=0;i<2;++i){char n[]="MUSIC0.BIN";n[5]+=i;if(!load(n,32+i*8))goto fail;}
 for(uint8_t i=0;i<4;++i){char n[]="RAW0.BIN";n[3]+=i;if(!load(n,1+i*8))goto fail;}
 for(uint8_t loop=0;loop<2;++loop){
  music_reset();uint8_t bank=1;uint16_t at=0xa000;
  for(uint32_t i=0;i<214239UL;++i){
   *(volatile uint8_t*)0=bank;uint8_t expected=*(const uint8_t*)at;
   if(lz_byte()!=expected||music_error)goto fail;
   if(++at==0xc000){at=0xa000;++bank;}
  }
 }
 music_reset();music_enabled=1;
 for(uint8_t i=0;i<32;++i)music_prefetch();
 for(uint8_t loop=0;loop<2;++loop){
  uint8_t bank=1;uint16_t at=0xa000;
  for(uint32_t i=0;i<214239UL;++i){
   *(volatile uint8_t*)0=bank;uint8_t expected=*(const uint8_t*)at;
   *(volatile uint8_t*)0=31;
   if(music_byte()!=expected||music_error)goto fail;
   if(!(i&63))music_prefetch();
   if(++at==0xc000){at=0xa000;++bank;}
  }
 }
 text("# MUSIC LZ PASS 856956 exact bytes: resets and buffered looping\n# DONE\n");goto done;
fail:text("# MUSIC LZ FAIL\n# DONE\n");
done:*(volatile uint8_t*)0x9fb4=0;__asm__ volatile("jmp $ffff");return 0;
}
