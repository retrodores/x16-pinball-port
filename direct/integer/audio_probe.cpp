#include "audio.h"
#include "fixed.h"
#include <cbm.h>
#include <cx16.h>
extern "C" volatile uint16_t audio_remaining;
static void out(char c){*(volatile char*)0x9fbb=c;}
static void text(const char*s){while(*s)out(*s++);}
static void hex(uint32_t n){for(int i=7;i>=0;--i)out("0123456789abcdef"[(n>>(i*4))&15]);}
static bool load(const char*n,uint8_t bank){*(volatile uint8_t*)0=bank;cbm_k_setnam(n);cbm_k_setlfs(1,8,2);return (uintptr_t)cbm_k_load(0,(void*)0xa000)>255;}
int main(){
 text("# TAP BEGIN\n");
 bool ok=load("SFXA.BIN",24)&&load("SFXB.BIN",2);
 uint16_t old=*(volatile uint16_t*)0x0314;
 audio_install();*(volatile uint8_t*)0=7;bool registers=true;
 *(volatile uint8_t*)0x9fb8=0;*(volatile uint8_t*)0x9fb6=1;
 for(uint8_t i=0;i<7;++i){
  text("# EFFECT ");hex(i);out(' ');hex(*(volatile uint32_t*)0x9fb8);out('\n');audio_effect(i);
  uint16_t frames=0;
  do {
   waitvsync();
   for(uint16_t k=0;k<400;++k)if(mul16(49153,16387)!=805470211UL)registers=false;
   if(*(volatile uint8_t*)0!=7)registers=false;
   if(++frames>400){ok=false;break;}
  }while(audio_remaining||!(*(volatile uint8_t*)0x9f3b&64));
  text(ok?"ok - PCM effect drained through IRQ refill\n":"not ok - PCM playback timeout\n");
 }
 audio_toggle();audio_effect(Bumper);bool muted=audio_remaining==0&&*(volatile uint8_t*)0x9f3c==0;
 audio_toggle();audio_effect(Bumper);audio_stop();bool stopped=audio_remaining==0&&*(volatile uint8_t*)0x9f3c==0;
 audio_uninstall();
 text(registers?"ok - IRQ preserves banking and arithmetic\n":"not ok - IRQ clobbered caller state\n");
 text(muted&&stopped?"ok - mute and stop clear playback\n":"not ok - mute or stop failed\n");
 text(*(volatile uint16_t*)0x0314==old?"ok - original IRQ restored\n":"not ok - IRQ restore failed\n");
 // Keep recording active: r49 only finalizes the WAV header in this state.
 text("1..10\n# AUDIO DONE\n");
 *(volatile uint8_t*)0=0;return 0;
}
