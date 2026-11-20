#ifndef CADET_ATTRACT_H
#define CADET_ATTRACT_H
#include "engine.h"

enum AttractInput {DemoLeft=1, DemoRight=2, DemoLaunch=4, DemoNudge=8,
                   DemoToggle=16, DemoNew=32, DemoReset=64};
enum AttractCaption {DemoBumpers=1, DemoRamps=5, DemoTourComplete=7, DemoFinalScore=8};
extern uint8_t attract_caption;
uint8_t attract_input(uint8_t buttons, uint16_t now);

#endif
