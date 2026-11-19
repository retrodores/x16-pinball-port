/* Native exact mixer and original-asset overlap/music evidence.
 * The byte oracle reads the original resident samples independently. */
#include <stdint.h>
#include <cbm.h>
#include "audio.h"
extern void pcm_start(uint16_t),pcm_flipper_start(uint16_t),pcm_plunger_start(uint16_t),pcm_stop(void),pcm_render(void);
extern void lab_install(void),lab_uninstall(void),music_start(void),music_stop(void),music_prefetch(void);
extern uint16_t lab_clock(void);
extern volatile uint16_t pcm_select_ptr,pcm_remaining,pcm_flipper_remaining,pcm_plunger_remaining,pcm_quota,pcm_underruns;
extern volatile uint8_t pcm_select_bank,pcm_buffer[256],music_enabled,music_error,music_loops;
extern volatile uint32_t irq_max,fm_writes,psg_writes;
static unsigned failures;
static uint16_t previous_underruns;
static uint8_t expected[256];
static const uint8_t ids[]={SOUND43,SOUND104,SOUND22};
static void text(const char*s){while(*s)*(volatile uint8_t*)0x9fbb=*s++;}
static void hex(uint32_t x){for(uint8_t i=0;i<8;++i){*(volatile uint8_t*)0x9fbb="0123456789abcdef"[x>>28];x<<=4;}}
static uint32_t cycles(void){uint8_t a=*(volatile uint8_t*)0x9fb8,b=*(volatile uint8_t*)0x9fb9,c=*(volatile uint8_t*)0x9fba,d=*(volatile uint8_t*)0x9fbb;return(uint32_t)a|((uint32_t)b<<8)|((uint32_t)c<<16)|((uint32_t)d<<24);}
static void frame(void){uint16_t t=lab_clock();while(lab_clock()==t){
#ifdef AUDIO_MUSIC_SOAK
 __asm__ volatile("wai");
#endif
 }if(pcm_underruns!=previous_underruns){previous_underruns=pcm_underruns;text("# UNDERRUN AT ");hex(lab_clock());text(" ");hex(pcm_underruns);text("\n");}}
static void check(uint8_t ok,uint16_t line){if(!ok){++failures;text("# FAIL ");hex(line);text("\n");}}
#define CHECK(x) check((x),__LINE__)
static uint8_t load(const char*n,uint8_t b){*(volatile uint8_t*)0=b;cbm_k_setnam(n);cbm_k_setlfs(1,8,2);return(uintptr_t)cbm_k_load(0,(void*)0xa000)>255;}
static void start(uint8_t id,uint8_t voice){const Effect*e=effects+id;pcm_select_bank=e->bank;pcm_select_ptr=e->ptr;if(voice==0)pcm_start(e->length);else if(voice==1)pcm_flipper_start(e->length);else pcm_plunger_start(e->length);}
static int16_t source(uint8_t id,uint16_t offset){
 const Effect*e=effects+id;uint16_t pos=(e->ptr-0xa000)+offset;uint8_t b=e->bank;
 while(pos>=8192){pos-=8192;++b;if(b==31)b=51;}
 uint8_t save=*(volatile uint8_t*)0;*(volatile uint8_t*)0=b;int8_t sample=*(volatile int8_t*)(0xa000+pos);*(volatile uint8_t*)0=save;return sample;
}
static int16_t attenuation(int16_t v,uint8_t shift){if(!shift)return v;return v<0?-(((-v)+(1u<<shift)-1)>>shift):v>>shift;}
static void exact(void){
 uint32_t maximum[3]={0};uint32_t bytes=0;
 for(uint8_t mask=1;mask<8;++mask){
  uint16_t position[3]={0,0,0},left[3]={0,0,0};pcm_stop();
  for(uint8_t k=0;k<3;++k)if(mask&(1u<<k)){left[k]=effects[ids[k]].length;start(ids[k],k);}
  for(uint8_t block=0;block<16;++block){
   uint16_t quota=block==0?256:block%4==0?1:block%4==1?185:block%4==2?186:256;
   uint8_t count=!!left[0]+!!left[1]+!!left[2],shift=count==3?2:count==2?1:0;
   for(uint16_t i=0;i<quota;++i){int16_t value=0;for(uint8_t k=0;k<3;++k)if(i<left[k])value+=attenuation(source(ids[k],position[k]+i),shift);expected[i]=(uint8_t)value;}
   *(volatile uint8_t*)0=61;pcm_quota=quota;uint32_t before=cycles();pcm_render();uint32_t elapsed=cycles()-before;
   CHECK(*(volatile uint8_t*)0==61);
   if(count&&elapsed>maximum[count-1])maximum[count-1]=elapsed;
   for(uint16_t i=0;i<quota;++i){CHECK(pcm_buffer[i]==expected[i]);++bytes;}
   for(uint8_t k=0;k<3;++k){uint16_t n=left[k]<quota?left[k]:quota;left[k]-=n;position[k]+=n;}
   CHECK(pcm_remaining==left[0]&&pcm_flipper_remaining==left[1]&&pcm_plunger_remaining==left[2]);
  }
 }
 pcm_stop();text("# MIX EXACT ");hex(bytes);text(" ");
 for(uint8_t k=0;k<3;++k){hex(maximum[k]);text(" ");CHECK(maximum[k]<45000UL);}text("\n");
}
/* Left-only PSG marker makes request-to-mono-PCM latency observable in WAV.
   Music is off during markers; the right channel remains pure game PCM. */
static void marker(uint8_t on){
 volatile uint8_t*v=(volatile uint8_t*)0x9f20;v[5]=0;v[0]=0xc0;v[1]=0xf9;v[2]=0x11;
 v[3]=0x7c;v[3]=0x0a;v[3]=on?0x7f:0;v[3]=32;
}
static void cue(uint8_t id,uint8_t voice){text("# CUE ");hex(lab_clock());text(" ");hex(voice);text(" ");hex(id);text("\n");start(id,voice);}
int main(void){
 for(uint8_t i=0;i<PCM_PARTS;++i){char n[]="PCM0.BIN";n[3]+=i;if(!load(n,pcm_load_banks[i]))goto fail;}
 for(uint8_t i=0;i<2;++i){char n[]="MUSIC0.BIN";n[5]+=i;if(!load(n,32+i*8))goto fail;}
#ifndef AUDIO_MUSIC_SOAK
 exact();lab_install();
 /* Original wormhole continues through independent flipper and launch cues. */
 for(uint16_t f=0;f<420;++f){frame();
  if(f==0)cue(SOUND43,0);if(f==24){marker(1);cue(SOUND104,1);}if(f==25)marker(0);if(f==36)cue(SOUND22,2);if(f==48)cue(SOUND105,1);
  if(f==160)cue(SOUND4,2);if(f==170)cue(SOUND104,1);if(f==180)cue(SOUND105,1);
  if(f==250||f==310)cue(SOUND22,2);
 }
 CHECK(!pcm_underruns);text("# MIX UNDERRUN ");hex(pcm_underruns);text(" IRQ ");hex(irq_max);text("\n");
 /* Real output evidence: music-only, M off silence, pending-start cancel, on. */
 music_start();text("# MUSIC START ");hex(lab_clock());text("\n");
 for(uint16_t f=0;f<240;++f){frame();music_prefetch();}
 CHECK(music_enabled==1&&!music_error&&fm_writes);
 music_stop();text("# MUSIC STOP ");hex(lab_clock());text("\n");
 for(uint8_t f=0;f<90;++f)frame();
 music_start();for(uint8_t f=0;f<10;++f){frame();music_prefetch();}CHECK(music_enabled==2);music_stop();
 for(uint8_t f=0;f<60;++f)frame();CHECK(!music_enabled);
 music_start();text("# MUSIC RESTART ");hex(lab_clock());text("\n");
 for(uint16_t f=0;f<240;++f){frame();music_prefetch();if(f==100)cue(SOUND43,0);if(f==112)cue(SOUND104,1);if(f==124)cue(SOUND22,2);}
 CHECK(!music_error&&!pcm_underruns&&music_enabled==1);
 music_stop();for(uint8_t i=0;i<90;++i)frame();
 /* Each one-byte source finishes in a single batch. End/start every VBL
    must not cause repeated256 priming or an increasing FIFO backlog. */
 *(volatile uint8_t*)0=1;*(volatile uint8_t*)0xa000=127;
 text("# PULSES ");hex(lab_clock()+1);text(" 00000080\n");
 for(uint8_t i=0;i<128;++i){frame();if(i==0)marker(1);if(i==1)marker(0);
  pcm_select_bank=1;pcm_select_ptr=0xa000;pcm_plunger_start(1);
 }
 for(uint8_t i=0;i<30;++i)frame();CHECK(!pcm_underruns);
#else
 lab_install();music_start();
 /* One complete actual theme loop with three simultaneous PCM voices.
    A stalled main frame is simulated without masking the audio IRQ. */
 for(uint16_t f=0;f<32050;++f){frame();music_prefetch();
  if(f%240==0)start(SOUND43,0);if(f%30==4)start(f&32?SOUND104:SOUND105,1);if(f%240==12)start(SOUND22,2);
  if(f==100){music_stop();for(uint8_t i=0;i<3;++i)frame();music_start();}
  if(f==140){music_stop();music_start();for(uint8_t i=0;i<8;++i){frame();music_prefetch();}CHECK(music_enabled==2);music_stop();music_start();}
  if(f==500){for(uint8_t i=0;i<4;++i)frame();}
  if(!(f%4000)){text("# MUSIC SOAK ");hex(f);text(" ");hex(music_error);text(" ");hex(pcm_underruns);text("\n");}
 }
 CHECK(music_loops>=1&&!music_error&&!pcm_underruns&&fm_writes&&psg_writes);
 text("# MUSIC MIXED LOOP ");hex(music_loops);text(" ");hex(fm_writes);text(" ");hex(psg_writes);text(" ");hex(pcm_underruns);text(" IRQ ");hex(irq_max);text("\n");
#endif
 lab_uninstall();if(failures)goto fail;
 text("# AUDIO MIX PASS\n# DONE\n");goto done;
fail:text("# AUDIO MIX FAIL\n# DONE\n");
done:*(volatile uint8_t*)0x9fb4=0;__asm__ volatile("jmp $ffff");return failures!=0;
}
