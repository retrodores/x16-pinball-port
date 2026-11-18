#include <stdint.h>
#include <cx16.h>
extern "C" {void audio_install();void audio_uninstall();void audio_effect(uint8_t);void audio_stop();void audio_toggle();void audio_music_toggle();void audio_pause(uint8_t);uint16_t audio_clock();uint32_t fastmul16(uint16_t,uint16_t);extern volatile uint16_t audio_remaining;}
static void text(const char*s){while(*s)*(volatile char*)0x9fbb=*s++;}
static void hex(uint32_t n){for(int i=7;i>=0;--i)*(volatile char*)0x9fbb="0123456789abcdef"[(n>>(i*4))&15];}
static void event(const char*s,uint8_t id=0){text("# EVENT ");text(s);text(" ");hex(id);text(" ");hex(*(volatile uint32_t*)0x9fb8);text("\n");}
static bool arithmetic=true,banking=true;
static void ticks(uint16_t n){uint16_t end=audio_clock()+n;while((int16_t)(end-audio_clock())>0){if(fastmul16(49153,16387)!=805470211UL)arithmetic=false;if(*(volatile uint8_t*)0!=7)banking=false;}}
int main(){text("# TAP BEGIN\n");uint16_t old=*(volatile uint16_t*)0x0314;audio_install();*(volatile uint8_t*)0=7;*(volatile uint8_t*)0x9fb8=0;*(volatile uint8_t*)0x9fb6=1;
 *(volatile uint8_t*)0x9f25=0;*(volatile uint8_t*)0x9f20=0x56;*(volatile uint8_t*)0x9f21=0x34;*(volatile uint8_t*)0x9f22=0x11;*(volatile uint8_t*)0x9f25=1;*(volatile uint8_t*)0x9f20=0x78;*(volatile uint8_t*)0x9f21=0x56;*(volatile uint8_t*)0x9f22=0x11;*(volatile uint8_t*)0x9f25=0;
 event("MUSIC");ticks(1100);
 asm volatile("sei":::"memory");bool vera_ok=*(volatile uint8_t*)0x9f25==0&&*(volatile uint8_t*)0x9f20==0x56&&*(volatile uint8_t*)0x9f21==0x34&&*(volatile uint8_t*)0x9f22==0x11;*(volatile uint8_t*)0x9f25=1;vera_ok=vera_ok&&*(volatile uint8_t*)0x9f20==0x78&&*(volatile uint8_t*)0x9f21==0x56&&*(volatile uint8_t*)0x9f22==0x11;*(volatile uint8_t*)0x9f25=0;asm volatile("cli":::"memory");
 text(vera_ok?"ok - PSG IRQ preserves both VERA addresses and control\n":"not ok - VERA address corrupted\n");audio_music_toggle();event("MUSIC_OFF");ticks(30);
 for(uint8_t i=0;i<7;++i){event("EFFECT",i);audio_effect(i);uint16_t end=audio_clock()+120;while(audio_remaining&&(int16_t)(end-audio_clock())>0)ticks(1);text(audio_remaining?"not ok - effect timeout\n":"ok - effect completes bounded envelope\n");ticks(15);}
 audio_music_toggle();event("MUSIC_RESUME");ticks(180);audio_pause(1);event("PAUSE");ticks(30);audio_pause(0);event("UNPAUSE");ticks(60);
 audio_toggle();audio_effect(2);event("MUTE");ticks(30);bool muted=audio_remaining==0;audio_toggle();audio_effect(2);audio_stop();bool stopped=audio_remaining==0;audio_uninstall();event("EXIT");ticks(0);
 text(arithmetic&&banking?"ok - IRQ preserves arithmetic and RAM bank\n":"not ok - IRQ caller state corrupted\n");text(muted&&stopped?"ok - mute and stop clear effects\n":"not ok - mute or stop failed\n");text(*(volatile uint16_t*)0x0314==old?"ok - IRQ restored\n":"not ok - IRQ restore failed\n");text("1..11\n# AUDIO DONE\n");*(volatile uint8_t*)0=0;return 0;}
