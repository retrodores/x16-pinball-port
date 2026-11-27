#ifndef CADET_SPRITES_H
#define CADET_SPRITES_H
#include <stdint.h>
#define SPRITE_BASE 102656UL
typedef struct __attribute__((packed)) {uint16_t address;uint8_t x,y,palette,size;} SpriteTile;
typedef struct __attribute__((packed)) {int16_t x,y;uint8_t width,height,count;const SpriteTile* tiles;} SpriteFrame;
#define sprites ((const SpriteFrame*)0xa000)
#endif
