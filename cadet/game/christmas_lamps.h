/* Holiday sprites share one 8x8 pattern per colour. Slots 80..106
 * are separate from the gameplay sprites and behind the ball. */
#include "christmas_lamp_data.h"

#define CHRISTMAS_PATTERN 0x1f9c0UL
#define CHRISTMAS_FIRST_SPRITE 80
extern volatile uint8_t christmas_cue;
static uint8_t holiday_shown[27], holiday_cursor;

static __attribute__((noinline,section(".holiday"))) void christmas_init(void){
 addr(CHRISTMAS_PATTERN);
 for(uint8_t i=0;i<sizeof(holiday_patterns);++i)v[3]=holiday_patterns[i];
}

static __attribute__((noinline,section(".holiday"))) void christmas_lamps(void){
 uint8_t cue=music_enabled?christmas_cue:0;
 uint8_t energy=cue&15,phase=cue>>4;
 bool exclusive=game.state==Ready||game.tilted||game.ring_flash||game.mission!=NoMission;
 for(uint8_t work=0;work<7;++work){
  uint8_t i=holiday_cursor;
  if(++holiday_cursor==27)holiday_cursor=0;
  uint8_t color=0;
  if(energy&&!exclusive&&!game_ring_lamp(i)){
   if(i<18){
    uint8_t clockwise=i+18-phase;
    if(clockwise>=18)clockwise-=18;
    uint8_t counter=17-i+phase;
    if(counter>=18)counter-=18;
    if(clockwise<energy)color=1;
    else if(energy>=3&&counter<energy)color=2;
   }else if(energy>=8&&i-18<(energy-7)*3){
    color=(i&1)+1;
   }
  }
  if(holiday_shown[i]==color)continue;
  holiday_shown[i]=color;
  uint8_t sprite=CHRISTMAS_FIRST_SPRITE+i;
  if(!color)hide(sprite);
  else tile(sprite,CHRISTMAS_PATTERN/32u+color-1,holiday_x[i],holiday_y[i],holiday_palette[color-1]);
 }
}
