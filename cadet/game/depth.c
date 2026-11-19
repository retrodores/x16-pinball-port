#include <stdint.h>
extern uint16_t depth_decode(uint16_t,uint16_t,uint8_t);
/* Outside-table pixels stay visible. Decode one clamped span for edge rows. */
uint16_t depth_mask(int16_t x,int16_t y,uint8_t depth){
 if(y<0||y>=470||x<=-16||x>=365)return 65535;
 if(x<0){uint8_t shift=-x;return (depth_decode(0,y,depth)<<shift)|((1u<<shift)-1);}
 if(x>349){uint8_t shift=x-349;return (depth_decode(349,y,depth)>>shift)|(uint16_t)(65535u<<(16-shift));}
 return depth_decode(x,y,depth);
}
