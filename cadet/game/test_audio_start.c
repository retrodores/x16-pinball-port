#include <stdint.h>
#include <cbm.h>
extern void lab_install(void),lab_uninstall(void),music_start(void),music_stop(void),music_prefetch(void),pcm_start(uint16_t);
extern uint16_t lab_clock(void);
extern volatile uint16_t music_buffered,pcm_remaining,pcm_select_ptr;
extern volatile uint8_t music_enabled,music_error,pcm_select_bank;
extern volatile uint32_t fm_writes,psg_writes;
#include "audio.h"
static void text(const char*s){while(*s)*(volatile uint8_t*)0x9fbb=*s++;}
static void hex(uint32_t x){for(uint8_t i=0;i<8;++i){*(volatile uint8_t*)0x9fbb="0123456789abcdef"[x>>28];x<<=4;}}
static uint32_t cycles(void){uint8_t a=*(volatile uint8_t*)0x9fb8,b=*(volatile uint8_t*)0x9fb9,c=*(volatile uint8_t*)0x9fba,d=*(volatile uint8_t*)0x9fbb;return(uint32_t)a|((uint32_t)b<<8)|((uint32_t)c<<16)|((uint32_t)d<<24);}
static void frame(void){uint16_t a=lab_clock();while(lab_clock()==a);}
static uint8_t load(const char*n,uint8_t bank){*(volatile uint8_t*)0=bank;cbm_k_setnam(n);cbm_k_setlfs(1,8,2);return(uintptr_t)cbm_k_load(0,(void*)0xa000)>255;}
int main(void){
 uint32_t start_max=0,prefetch_max=0;
 for(uint8_t i=0;i<2;++i){char n[]="MUSIC0.BIN";n[5]+=i;if(!load(n,32+i*8))goto fail;}
 for(uint8_t i=0;i<PCM_PARTS;++i){char n[]="PCM0.BIN";n[3]+=i;if(!load(n,pcm_load_banks[i]))goto fail;}
 lab_install();
 for(uint8_t attempt=0;attempt<4;++attempt){
  uint32_t before=cycles();music_start();uint32_t used=cycles()-before;if(used>start_max)start_max=used;
  if(music_enabled!=2||music_buffered!=0)goto fail_installed;
  uint32_t old_fm=fm_writes,old_psg=psg_writes;
  for(uint8_t i=0;i<31;++i){frame();if(music_enabled!=2||fm_writes!=old_fm||psg_writes!=old_psg)goto fail_installed;
   before=cycles();music_prefetch();used=cycles()-before;if(used>prefetch_max)prefetch_max=used;
  }
  if(music_buffered!=1984||music_enabled!=2)goto fail_installed;
  if(attempt==1){music_stop();music_prefetch();frame();if(music_enabled||music_buffered!=1984)goto fail_installed;continue;}
  music_prefetch();if(music_enabled!=1)goto fail_installed;
  for(uint8_t i=0;i<16;++i){frame();music_prefetch();}
  if(music_error||fm_writes==old_fm)goto fail_installed;
 }
 music_stop();
 text("# AUDIO START ");hex(start_max);text(" ");hex(prefetch_max);text("\n");
 if(start_max>20000UL||prefetch_max>60000UL)goto fail_installed;
 /* Full real IRQ playback, including SOUND43 crossing bank30 -> bank51. */
 const uint8_t ids[]={SOUND43,SOUND17,SOUND49D,SOUND14,SOUND35,SOUND131};
 for(uint8_t n=0;n<sizeof(ids);++n){
  for(uint8_t i=0;i<30;++i)frame();
  const Effect*e=effects+ids[n];pcm_select_bank=e->bank;pcm_select_ptr=e->ptr;
  text("# PCM ");hex(ids[n]);text(" ");hex(e->length);text("\n");
  pcm_start(e->length);uint16_t deadline=lab_clock()+300;
  while(pcm_remaining){frame();if((int16_t)(lab_clock()-deadline)>=0)goto fail_installed;}
 }
 for(uint8_t i=0;i<30;++i)frame();
 lab_uninstall();text("# AUDIO START PASS\n# DONE\n");goto done;
fail_installed:lab_uninstall();
fail:text("# AUDIO START FAIL\n# DONE\n");
done:*(volatile uint8_t*)0x9fb4=0;__asm__ volatile("jmp $ffff");return 0;
}
