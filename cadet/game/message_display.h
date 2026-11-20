#ifndef CADET_MESSAGE_DISPLAY_H
#define CADET_MESSAGE_DISPLAY_H

#include <stdint.h>

/* Original 5x7 dot designs, stored as seven rows of five bits. */
static const uint8_t message_glyphs[][7] __attribute__((section(".physics.rodata"))) = {
    {14,17,17,31,17,17,17}, /* A */
    {30,17,17,30,17,17,30},
    {14,17,16,16,16,17,14},
    {28,18,17,17,17,18,28},
    {31,16,16,30,16,16,31},
    {31,16,16,30,16,16,16},
    {14,17,16,23,17,17,14},
    {17,17,17,31,17,17,17},
    {14,4,4,4,4,4,14},
    {7,2,2,2,2,18,12},
    {17,18,20,24,20,18,17},
    {16,16,16,16,16,16,31},
    {17,27,21,21,17,17,17},
    {17,25,21,19,17,17,17},
    {14,17,17,17,17,17,14},
    {30,17,17,30,16,16,16},
    {14,17,17,17,21,18,13},
    {30,17,17,30,20,18,17},
    {15,16,16,14,1,1,30},
    {31,4,4,4,4,4,4},
    {17,17,17,17,17,17,14},
    {17,17,17,17,17,10,4},
    {17,17,17,21,21,27,17},
    {17,17,10,4,10,17,17},
    {17,17,10,4,4,4,4},
    {31,1,2,4,8,16,31}, /* Z */
    {14,17,19,21,25,17,14}, /* 0 */
    {4,12,4,4,4,4,14},
    {14,17,1,6,8,16,31},
    {30,1,1,14,1,1,30},
    {2,6,10,18,31,2,2},
    {31,16,30,1,1,17,14},
    {6,8,16,30,17,17,14},
    {31,1,2,4,8,8,8},
    {14,17,17,14,17,17,14},
    {14,17,17,15,1,2,12},
};

/* Lowercase glyphs reuse the former legend font's VRAM. */
static const uint8_t message_lowercase[][7] __attribute__((section(".physics.rodata"))) = {
    {0,0,14,1,15,17,15}, /* a */
    {16,16,22,25,17,17,30},
    {0,0,14,17,16,17,14},
    {1,1,13,19,17,17,15},
    {0,0,14,17,31,16,14},
    {6,9,8,28,8,8,8},
    {0,0,15,17,15,1,14},
    {16,16,22,25,17,17,17},
    {4,0,12,4,4,4,14},
    {2,0,6,2,2,18,12},
    {16,16,18,20,24,20,18},
    {12,4,4,4,4,4,14},
    {0,0,26,21,21,21,21},
    {0,0,22,25,17,17,17},
    {0,0,14,17,17,17,14},
    {0,0,30,17,30,16,16},
    {0,0,15,17,15,1,1},
    {0,0,22,25,16,16,16},
    {0,0,15,16,14,1,30},
    {8,8,28,8,8,9,6},
    {0,0,17,17,17,19,13},
    {0,0,17,17,17,10,4},
    {0,0,17,17,21,21,10},
    {0,0,17,10,4,10,17},
    {0,0,17,17,15,1,14},
    {0,0,31,2,4,8,31}, /* z */
};

#define MESSAGE_COLUMNS 15u
#define MESSAGE_ROWS 4u
#define PLAYER_COLUMNS 8u
#define PLAYER_FIRST_SPRITE 33u
#define MESSAGE_FIRST_SPRITE (PLAYER_FIRST_SPRITE + PLAYER_COLUMNS)
#define MESSAGE_GLYPH_BYTES 64u
#define MESSAGE_FONT_BASE FAST_TILE_END

_Static_assert(sizeof(message_glyphs)/7*MESSAGE_GLYPH_BYTES+MESSAGE_FONT_BASE<=0x1f9c0UL,
               "Message font overlaps reserved VERA memory");
_Static_assert(sizeof(message_lowercase)/7*MESSAGE_GLYPH_BYTES<=2048,
               "Lowercase font overlaps the ball scratch sprite");
_Static_assert(MESSAGE_FIRST_SPRITE+MESSAGE_COLUMNS*MESSAGE_ROWS<=128,
               "Messages exceed the VERA sprite table");

static __attribute__((section(".physics"),noinline)) void upload_glyphs(uint32_t base,const uint8_t glyphs[][7],uint8_t count){
    addr(base);
    for(uint8_t glyph=0;glyph<count;++glyph){
        uint8_t previous=0;
        for(uint8_t y=0;y<16;++y){
            uint8_t stroke=y<14 ? glyphs[glyph][y/2]<<2 : 0;
            uint8_t shadow=(stroke>>1)|previous;
            previous=stroke;
            uint8_t pair=0;
            for(uint8_t bit=0x80;bit;bit>>=1){
                uint8_t color=stroke&bit ? FONT_STATUS_PEN : shadow&bit ? FONT_STATUS_SHADOW : 0;
                if(bit&0x55)v[3]=pair|color;
                else pair=color<<4;
            }
        }
    }
}

static __attribute__((section(".physics"),noinline)) uint16_t message_pattern(uint8_t c){
    if(c>='a'&&c<='z')return FONT_BASE/32+2u*(c-'a');
    if(c>='A'&&c<='Z')return MESSAGE_FONT_BASE/32+2u*(c-'A');
    if(c>='0'&&c<='9')return MESSAGE_FONT_BASE/32+2u*(26+c-'0');
    return 0;
}

static __attribute__((section(".physics"),noinline)) void init_messages(void){
    upload_glyphs(FONT_BASE,message_lowercase,sizeof(message_lowercase)/7);
    upload_glyphs(MESSAGE_FONT_BASE,message_glyphs,sizeof(message_glyphs)/7);
    const char player[]="Player 1";
    for(uint8_t i=0;i<PLAYER_COLUMNS;++i){
        uint16_t pattern=message_pattern(player[i]);
        if(pattern)tile(PLAYER_FIRST_SPRITE+i,pattern,405u+11u*i,244,0x40|FONT_STATUS_BANK);
    }
}

/* The lower pane owns the changing text. An empty line hides its old sprites. */
static void draw_message(const char *message,uint8_t digit,uint8_t *cache){
    uint8_t slot=0;
    uint16_t y=306;
    for(uint8_t row=0;row<MESSAGE_ROWS;++row,y+=18){
        uint16_t x=405;
        for(uint8_t column=0;column<MESSAGE_COLUMNS;++column,++slot,x+=11){
            uint8_t c=*message&&*message!='\n' ? *message++ : ' ';
            if(c=='#')c=digit;
            if(cache[slot]==c)continue;
            cache[slot]=c;
            uint16_t pattern=message_pattern(c);
            if(pattern)tile(MESSAGE_FIRST_SPRITE+slot,pattern,x,y,0x40|FONT_STATUS_BANK);
            else hide(MESSAGE_FIRST_SPRITE+slot);
        }
        while(*message&&*message!='\n')++message;
        if(*message)++message;
    }
}

#endif
