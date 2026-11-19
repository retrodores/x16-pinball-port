/* Source-derived routing fixtures: TSink/TKickout/TKickback/control.cpp. */
#include "engine.h"
#include "model.h"
#include "audio.h"
#include "audio_events.h"
#include <assert.h>
#include <stdio.h>
static uint8_t group(uint16_t original){for(uint8_t i=0;i<component_count;++i)if(original_groups[i]==original)return i;assert(0);return 0;}
static uint8_t sample(uint8_t event,uint16_t original,uint8_t kind){return audio_event_sample(event,group(original),kind,0);}
int main(void){
 for(uint16_t original=338;original<=344;original+=2){
  assert(sample(7,original,Sink)==SOUND43);
  assert(sample(8,original,Sink)==SOUND43);
 }
 assert(sample(7,512,Kickout)==SOUND35);
 assert(sample(8,512,Kickout)==SOUND57);
 assert(sample(7,514,Kickout)==SOUND57);
 assert(sample(8,514,Kickout)==255);
 assert(sample(9,505,Kickback)==SOUND17);
 assert(sample(9,507,Kickback)==SOUND17);
 assert(sample(10,501,Gate)==255);
 assert(sample(10,502,Gate)==255);
 assert(sample(11,501,Gate)==255);
 for(uint16_t original=520;original<=522;++original)assert(sample(12,original,Sensor)==SOUND26);
 for(uint16_t original=528;original<=530;++original)assert(sample(12,original,Sensor)==SOUND26);
 assert(sample(13,520,Sensor)==255);
 assert(sample(14,454,Target)==SOUND49D);
 assert(sample(15,466,Target)==SOUND55);
 assert(sample(3,338,Sink)==SOUND22);
 assert(sample(3,473,Plunger)==SOUND22);
 assert(sample(16,473,Plunger)==SOUND4);
 assert(sample(4,473,Plunger)==255); /* Original upload lacks SOUND62.WAV. */
 assert(sample(0,473,Plunger)==SOUND104);
 assert(sample(1,473,Plunger)==SOUND105);
 for(uint16_t wall=469;wall<=472;++wall){assert(sample(2,wall,Wall)==SOUND5);assert(sample(6,wall,Wall)==255);}
 assert((audio_event_sample(9,group(505),Kickback,0)>>8)==3);
 assert((uint8_t)audio_event_sample(7,255,Sink,0)==255);
 assert((uint8_t)audio_event_sample(14,group(454),Target,1)==SOUND14);
 assert((uint8_t)audio_event_sample(7,group(512),Kickout,2)==SOUND35);
 assert((uint8_t)audio_event_sample(7,group(512),Kickout,1)==255);
 assert((uint8_t)audio_event_sample(7,group(512),Kickout,3)==255);
 assert((uint8_t)audio_event_sample(7,group(512),Kickout,4)==255);
 puts("Original audio event routing PASS");
 return 0;
}
