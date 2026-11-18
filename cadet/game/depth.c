#include <stdint.h>
/* Slow boundary fallback; the in-bounds ball uses depth_rect.s. */
uint16_t depth_mask(int16_t x,int16_t y,uint8_t depth){
 if(y<0||y>=470)return 65535;
 uint8_t saved=*(volatile uint8_t*)0;*(volatile uint8_t*)0=11;
 const uint8_t*index=(const uint8_t*)(0xb400+y*3);
 uint16_t address=index[0]|((uint16_t)index[1]<<8);uint8_t bank=index[2];
 *(volatile uint8_t*)0=bank;const uint8_t*row=(const uint8_t*)address;uint16_t mask=0;
 for(uint8_t i=0;i<16;++i){int16_t at=x+i;if(at<0||at>=365||row[at]>depth)mask|=(uint16_t)1<<i;}
 *(volatile uint8_t*)0=saved;return mask;
}
