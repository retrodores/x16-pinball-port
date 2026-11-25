/* Slots 96..126 sit behind the ball. Slot 127 belongs to the red X. */
#include "christmas_lamp_data.h"

#define CHRISTMAS_PATTERN 0x1f980UL
#define CHRISTMAS_FIRST_SPRITE 96
#define HOLIDAY_COUNT (sizeof(holiday_x) / sizeof(holiday_x[0]))
extern volatile uint8_t christmas_cue;
static uint8_t holiday_shown[HOLIDAY_COUNT], holiday_cursor;

static __attribute__((noinline,section(".holiday"))) void christmas_init(void){
 addr(CHRISTMAS_PATTERN);
 for(uint8_t i=0;i<sizeof(holiday_patterns);++i)v[3]=holiday_patterns[i];
 for(uint8_t i=0;i<HOLIDAY_COUNT;++i){
  addr(0x1fc00UL+(uint16_t)(CHRISTMAS_FIRST_SPRITE+i)*8);
  word(0x8000u | (CHRISTMAS_PATTERN/32u));word(holiday_x[i]);word(holiday_y[i]);
  v[3]=0;v[3]=0;
 }
}

static __attribute__((noinline,section(".holiday"))) void christmas_lamps(void){
 uint8_t cue=music_enabled?christmas_cue:0;
 uint8_t energy=cue&15,phase=cue>>4;
 uint8_t head=phase+(phase>>3),mirror=17-head,width=(energy+1)>>1;
 const uint8_t *scene=energy>=HOLIDAY_FIRST_SCENE && energy<HOLIDAY_FIRST_SCENE+3
                      ? holiday_scenes[energy-HOLIDAY_FIRST_SCENE][phase] : 0;
 bool exclusive=game.state==Ready||game.tilted||game.ring_flash;
 for(uint8_t work=0;work<8;++work){
  uint8_t i=holiday_cursor;
  if(++holiday_cursor==HOLIDAY_COUNT)holiday_cursor=0;
  uint8_t color=0;
  if(energy&&!exclusive){
   if(scene){
    color=scene[i];
    if(i<18&&game.mission>=Practice)color=0;
   }else if(i<18&&game.mission<Practice){
    uint8_t forward=i+18-head;
    if(forward>=18)forward-=18;
    uint8_t backward=mirror+18-i;
    if(backward>=18)backward-=18;
    if(forward<width)color=1+(phase&1u);
    else if(energy>=3&&backward<width)color=2-(phase&1u);
   }else if(i>=18&&i<27&&energy>=6){
    uint8_t spoke=i-18;
    uint8_t radius=spoke<=4?spoke:9-spoke;
    if(radius<energy-5)color=1+((spoke+phase)&1u);
   }
   if(color && (i<27?game_ring_lamp(i):game_claims_accent(holiday_accent_groups[i-27])))color=0;
  }
  uint8_t old=holiday_shown[i];
  if(old==color)continue;
  holiday_shown[i]=color;
  uint8_t sprite=CHRISTMAS_FIRST_SPRITE+i;
  if(!color){hide(sprite);continue;}
  /* Pattern addresses differ only in their low byte. Position, size and
   * palette are fixed, so color swaps need just one VERA data write. */
  uint32_t attr=0x1fc00UL+(uint16_t)sprite*8;
  addr(attr);v[3]=(uint8_t)(CHRISTMAS_PATTERN/32u+2u*(color-1));
  if(!old){addr(attr+6);v[3]=12;}
 }
}
