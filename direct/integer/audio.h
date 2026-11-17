#pragma once
#include <stdint.h>
// Original sample bank events. Native probes keep this adapter silent.
enum SoundEffect:uint8_t {FlipperUp,FlipperDown,Bumper,Launch,Pullback,Drain,Wall};
#if defined(__CX16__) && defined(CMDRX_AUDIO)
extern "C" {
void audio_install();void audio_uninstall();void audio_stop();
void audio_toggle();void audio_effect(uint8_t);
extern volatile uint8_t audio_enabled;
}
#else
inline void audio_effect(uint8_t){}
inline void audio_stop(){}
#endif
