/* Slots 96..126 sit behind the ball. Slot 127 belongs to the red X. */
#include "christmas_lamp_data.h"
#include "carol_lamp_score.h"

#define CHRISTMAS_PATTERN 0x1f980UL
#define CHRISTMAS_FIRST_SPRITE 96
#define HOLIDAY_COUNT (sizeof(holiday_x) / sizeof(holiday_x[0]))
extern volatile uint16_t christmas_song_tick;
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
 /* The IRQ advances a 16-bit score clock. A rollover between byte reads
  * would briefly send the show up to four seconds away from the beat. */
 __asm__ volatile("php\nsei":::"memory");
 uint16_t tick=christmas_song_tick;
 uint8_t enabled=music_enabled;
 __asm__ volatile("plp":::"memory");
 uint8_t cue=enabled&&tick<CAROL_SONG_TICKS?carol_cues[tick>>2]:0;
 uint8_t pattern=cue&15,phase=cue>>4;
 const uint8_t *scene=pattern>=HOLIDAY_FIRST_SCENE && pattern<HOLIDAY_INNER_PING
                      ? holiday_scenes[pattern-HOLIDAY_FIRST_SCENE][phase] : 0;
 uint8_t spoke=18+(phase>=9?phase-9:phase);
 bool exclusive=game.state==Ready||game.tilted||game.ring_flash;
 for(uint8_t work=0;work<8;++work){
  uint8_t i=holiday_cursor;
  if(++holiday_cursor==HOLIDAY_COUNT)holiday_cursor=0;
  uint8_t color=0;
  if(pattern&&!exclusive){
   if(scene){
    color=scene[i];
    if(i<18&&game.mission>=Practice)color=0;
   }else if(pattern==HOLIDAY_INNER_PING && (i==spoke||i==27)){
    color=1+((phase+(i==27))&1u);
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
