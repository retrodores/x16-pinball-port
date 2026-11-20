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

#define MESSAGE_COLUMNS 11u
#define MESSAGE_ROWS 3u
#define MESSAGE_FIRST_SPRITE 33u
#define MESSAGE_GLYPH_BYTES 64u
#define MESSAGE_GLYPH_COUNT (sizeof(message_glyphs) / sizeof(message_glyphs[0]))
/* Start after the private slingshot tiles, leaving PSG memory untouched. */
#define MESSAGE_FONT_BASE FAST_TILE_END

_Static_assert(MESSAGE_FONT_BASE + MESSAGE_GLYPH_COUNT * MESSAGE_GLYPH_BYTES <= 0x1f9c0UL,
               "Message font overlaps reserved VERA memory");
_Static_assert(MESSAGE_FIRST_SPRITE + MESSAGE_COLUMNS * MESSAGE_ROWS <= 73u,
               "Message sprites overlap the music indicator");

static __attribute__((section(".physics"),noinline)) void upload_message_font(void){
    addr(MESSAGE_FONT_BASE);
    for(uint8_t glyph=0;glyph<MESSAGE_GLYPH_COUNT;++glyph){
        for(uint8_t y=0;y<16;++y){
            uint8_t dots=y<14 ? message_glyphs[glyph][y/2] : 0;
            /* Five columns over eight pixels. Tall dots hold up at cabinet scale. */
            v[3]=(dots&16)?FONT_PEN<<4:0;
            v[3]=((dots&8)?FONT_PEN<<4:0)|((dots&4)?FONT_PEN:0);
            v[3]=(dots&2)?FONT_PEN:0;
            v[3]=(dots&1)?FONT_PEN:0;
        }
    }
}

/* A trailing # stands for the changing objective count. Words are wrapped
 * explicitly by the caller so the line breaks stay stable as counts change. */
static void draw_message(const char *message,uint8_t digit,uint8_t *cache){
    uint8_t slot=0;
    uint16_t y=244;
    for(uint8_t row=0;row<MESSAGE_ROWS;++row,y+=15){
        uint16_t x=405;
        for(uint8_t column=0;column<MESSAGE_COLUMNS;++column,++slot,x+=14){
            uint8_t c=*message && *message!='\n' ? *message++ : ' ';
            if(c=='#')c=digit;
            if(cache[slot]==c)continue;
            cache[slot]=c;
            uint8_t sprite=MESSAGE_FIRST_SPRITE+slot;
            uint8_t glyph;
            if(c>='A'&&c<='Z')glyph=c-'A';
            else if(c>='0'&&c<='9')glyph=26+c-'0';
            else{hide(sprite);continue;}
            tile(sprite,(uint16_t)(MESSAGE_FONT_BASE/32)+2u*glyph,x,y,
                 0x40|FONT_STATUS_BANK);
        }
        while(*message && *message!='\n')++message;
        if(*message)++message;
    }
}

#endif
