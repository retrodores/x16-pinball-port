/* Holiday sprites share one 8x8 pattern per colour. Slots 100..126
 * are separate from the gameplay sprites and behind the ball. */
#include "christmas_lamp_data.h"

#define CHRISTMAS_PATTERN 0x1f980UL
#define CHRISTMAS_FIRST_SPRITE 100
extern volatile uint8_t christmas_cue;
static uint8_t holiday_shown[27], holiday_cursor;

static __attribute__((noinline,section(".holiday"))) void christmas_init(void){
 addr(CHRISTMAS_PATTERN);
 for(uint8_t i=0;i<sizeof(holiday_patterns);++i)v[3]=holiday_patterns[i];
}

static __attribute__((noinline,section(".holiday"))) void christmas_lamps(void){
 uint8_t cue=music_enabled?christmas_cue:0;
 uint8_t energy=cue&15,phase=cue>>4;
 /* Map the sixteen score positions to the eighteen physical inserts. */
 uint8_t head=phase+(phase>>3);
 uint8_t mirror=17-head;
 uint8_t width=(energy+1)>>1;
 bool exclusive=game.state==Ready||game.tilted||game.ring_flash;
 for(uint8_t work=0;work<7;++work){
  uint8_t i=holiday_cursor;
  if(++holiday_cursor==27)holiday_cursor=0;
  uint8_t color=0;
  if(energy&&!exclusive&&!game_ring_lamp(i)){
   if(i<18&&game.mission<Practice){
    uint8_t forward=i+18-head;
    if(forward>=18)forward-=18;
    uint8_t backward=mirror+18-i;
    if(backward>=18)backward-=18;
    if(forward<width)color=1+(phase&1u);
    else if(energy>=3&&backward<width)color=2-(phase&1u);
   }else if(i>=18&&energy>=6){
    /* Grow two arms from the top of the inner ring. Keep rank lamps above
     * these accents. The score explicitly releases the lights after hits. */
    uint8_t spoke=i-18;
    uint8_t radius=spoke<=4?spoke:9-spoke;
    if(radius<energy-5)color=1+((spoke+phase)&1u);
   }
  }
  if(holiday_shown[i]==color)continue;
  holiday_shown[i]=color;
  uint8_t sprite=CHRISTMAS_FIRST_SPRITE+i;
  if(!color)hide(sprite);
  else tile(sprite,0x8000u | (CHRISTMAS_PATTERN/32u+2u*(color-1)),holiday_x[i],holiday_y[i],0);
 }
}
