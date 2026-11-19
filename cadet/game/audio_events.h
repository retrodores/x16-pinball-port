/* Original component-specific sample routing.
 * Include after engine.h and generated audio.h. 255 means intentional silence.
 * High byte is table-voice priority, low byte is the resident effect.
 * Flippers and the main plunger have independent voices in play.c.
 */
#ifndef CADET_AUDIO_EVENTS_H
#define CADET_AUDIO_EVENTS_H
static uint16_t audio_event_sample(uint8_t event,uint8_t group,uint8_t kind,uint8_t value){
 uint8_t sample=255,rank=2;
 if(group>=sizeof contact_sound/sizeof contact_sound[0])return 255;
 switch(event){
 case 0:sample=SOUND104;rank=1;break;
 case 1:sample=SOUND105;rank=1;break;
 case 2:sample=contact_sound[group];break;
 case 6:sample=kind==Wall?255:contact_sound[group];break;
 /* Launch is its own event now; prior return-count test muted later plunges. */
 case 3:sample=SOUND22;rank=3;break;
 /* DAT group59 literally names SOUND62.WAV for pull. That file is absent
    even from the supplied original archive; keep this event silent. */
 case 4:break;
 case 16:sample=SOUND4;rank=3;break;
 case 7:
  sample=capture_sound[group];rank=3;
  /* Advanced hyperspace cues are not resident. Keep them explicitly silent;
     tiers 0 and 2 share original SOUND35. Do not reuse it for other tiers. */
  if(sample==SOUND35&&value!=0&&value!=2)sample=255;
  break;
 case 8:sample=release_sound[group];rank=3;break;
 case 9:sample=contact_sound[group];rank=3;break;
 case 10:sample=gate_open_sound[group];break;
 case 11:sample=gate_close_sound[group];break;
 case 12:sample=contact_sound[group];break;
 /* Lane completion has no extra sound in the recovered control handler.
    Keep its already-issued rollover sound; do not invent an upgrade jingle. */
 case 13:break;
 case 14:sample=value?SOUND14:SOUND49D;rank=value?3:2;break;
 case 15:sample=contact_sound[group];break;
 default:break;
 }
 (void)kind;
 return (uint16_t)sample|((uint16_t)rank<<8);
}
#endif
