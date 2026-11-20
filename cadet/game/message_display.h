#ifndef CADET_MESSAGE_DISPLAY_H
#define CADET_MESSAGE_DISPLAY_H

#include "msgfont.h"

/* Bank 57: PCM ends before A400, font data ends before BD00.
 * The glyph renderer runs in bank 62. */
#define FONT_RECORDS ((const uint8_t *)0xa400)
#define FONT_CODE __attribute__((section(".physics"),noinline))
static uint8_t font_cache[96] __attribute__((section(".physics.fontcache")));
#define FONT_BANK_RAM 57
#define FONT_HEAD_CELLS 16u
#define FONT_TAIL_CELLS ((0x1f9c0UL-FAST_TILE_END)/128u)
#define PLAYER_FIRST_SPRITE 33u
#define MESSAGE_FIRST_SPRITE 41u
#define MESSAGE_LAST_SPRITE 96u
#define MESSAGE_LEFT 405u
#define MESSAGE_RIGHT 570u
#define MESSAGE_TOP 306u

static const uint8_t font_colors[16] = MSG_COLOR_TABLE;
static uint8_t font_head,font_tail,player_head,player_tail,font_slot,font_digit;
static uint16_t font_x,font_y;
static const char *font_pending;

static void font_bank(uint8_t b){
 __asm__ volatile("":::"memory");
 *(volatile uint8_t*)0=b;
 __asm__ volatile("":::"memory");
}

/* A banked caller cannot keep executing while bank 57 is selected. Copy
 * the glyph into its unbanked stack before switching back to the renderer. */
static __attribute__((noinline)) uint8_t font_read(uint8_t code,uint8_t *pixels){
 uint8_t saved=*(volatile uint8_t*)0;
 font_bank(FONT_BANK_RAM);
 const uint8_t *record=FONT_RECORDS+3u*code;
 uint8_t width=record[0];
 if(pixels){
  const uint8_t *source=(const uint8_t*)(uintptr_t)(record[1]|((uint16_t)record[2]<<8));
  uint8_t count=(uint8_t)((width+3u)/4u*MSG_HEIGHT);
  for(uint8_t i=0;i<count;++i)pixels[i]=source[i];
 }
 font_bank(saved);
 return width;
}

static uint16_t glyph_pattern(uint8_t slot){
 if(slot<FONT_HEAD_CELLS)return FONT_BASE/32u+4u*slot;
 return FAST_TILE_END/32u+4u*(slot-FONT_HEAD_CELLS);
}

static FONT_CODE uint8_t font_upload(uint8_t code,uint8_t width,const uint8_t *pixels){
 uint8_t cells=width>16?4:width>8?2:1;
 uint8_t slot;
 if(font_head+cells<=FONT_HEAD_CELLS){
  slot=font_head;font_head+=cells;
 }else if(font_tail+cells<=FONT_HEAD_CELLS+FONT_TAIL_CELLS){
  slot=font_tail;font_tail+=cells;
 }else return 255;
 font_cache[code]=slot;
 uint8_t stride=cells*4,bytes=(width+3)/4;
 addr((uint32_t)glyph_pattern(slot)*32u);
 for(uint8_t y=0;y<32;++y){
  uint8_t n=0;
  if(y<MSG_HEIGHT){
   for(uint8_t j=0;j<bytes;++j){
    uint8_t data=*pixels++;
    v[3]=font_colors[data>>4];v[3]=font_colors[data&15];n+=2;
   }
  }
  while(n++<stride)v[3]=0;
 }
 return slot;
}

/* Each frame uploads at most one new glyph. Already cached advances are cheap. */
static FONT_CODE void message_banked(void){
 uint8_t pixels[110];
 for(uint8_t i=0;i<4;++i){
  uint8_t c=*font_pending++;
  if(!c||font_slot>=MESSAGE_LAST_SPRITE||font_y>MESSAGE_TOP+2u*MSG_HEIGHT){
   font_pending=0;break;
  }
  if(c=='\n'){font_x=MESSAGE_LEFT;font_y+=MSG_HEIGHT;continue;}
  if(c=='#')c=font_digit;
  if(c<32||c>=128)c=' ';
  uint8_t code=c-32;
  uint8_t slot=font_cache[code];
  bool fresh=slot==255;
  uint8_t width=font_read(code,fresh?pixels:0);
  if(c!=' '&&font_x+width<=MESSAGE_RIGHT){
   if(fresh)slot=font_upload(code,width,pixels);
   uint8_t attr=0x82;
   if(width>8)attr+=width>16?32:16;
   if(slot!=255)tile(font_slot++,glyph_pattern(slot),font_x,font_y,attr);
   font_x+=width+MSG_GAP;
   if(fresh)break;
  }else font_x+=width+MSG_GAP;
 }
}

static void message_step(void){
 if(!font_pending)return;
 uint8_t saved=*(volatile uint8_t*)0;
 font_bank(62);
 message_banked();
 font_bank(saved);
}

static FONT_CODE void init_messages(void){
 for(uint8_t i=0;i<96;++i)font_cache[i]=255;
 font_slot=PLAYER_FIRST_SPRITE;
 font_head=0;font_tail=FONT_HEAD_CELLS;
 font_x=MESSAGE_LEFT;font_y=244;
 font_pending="Player 1";
 while(font_pending)message_banked();
 player_head=font_head;player_tail=font_tail;
 font_slot=MESSAGE_FIRST_SPRITE;
}

static FONT_CODE void status_banked(const char *s,uint8_t digit){
 uint8_t visible=game.state==Ready&&game.wait>StartupReadyFrames?0:12;
 for(uint8_t i=PLAYER_FIRST_SPRITE;i<PLAYER_FIRST_SPRITE+7;++i){
  addr(0x1fc06UL+(uint16_t)i*8);v[3]=visible;
 }
 while(font_slot>MESSAGE_FIRST_SPRITE)hide(--font_slot);
 for(uint8_t i=0;i<96;++i){
  uint8_t slot=font_cache[i];
  if((slot>=player_head&&slot<FONT_HEAD_CELLS)||slot>=player_tail)font_cache[i]=255;
 }
 font_head=player_head;font_tail=player_tail;
 font_x=MESSAGE_LEFT;font_y=MESSAGE_TOP;font_digit=digit;font_pending=s;
}

static void status(const char *s,uint8_t digit){
 uint8_t saved=*(volatile uint8_t*)0;
 font_bank(62);
 status_banked(s,digit);
 font_bank(saved);
}

#endif
