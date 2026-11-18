/* Plain-C adaptation of control.cpp BumperControl/RebounderControl.
 * Upstream cb9b7b886244a27773f66b0b19fdc2998392565e (MIT).
 * These are event awards, not the complete mission/scoring system.
 * The 128-bit accumulator is the X16 user's explicit extension.
 */
#include "rules.h"
static const uint16_t attack_scores[4] = {500,1000,1500,2000};
static const uint16_t launch_scores[4] = {1500,2500,3500,4500};
uint16_t cadet_bumper_award(uint8_t bank, uint8_t level) {
    if (level > 3 || bank > 1) return 0;
    return bank ? launch_scores[level] : attack_scores[level];
}
uint16_t cadet_rebounder_award(void) { return 500; }
void cadet_add_score(cadet_score *s, uint32_t award) {
    uint8_t i;
    uint16_t carry, v;
    carry=0;
    for(i=0;i<16;++i) {
        v=(uint16_t)s->bytes[i]+carry;
        if(i<4) { v+=(uint8_t)award; award>>=8; }
        s->bytes[i]=(uint8_t)v;
        carry=v>>8;
        if(i>=3 && !carry) break;
    }
    if(carry) {
        s->overflow=1;
        for(i=0;i<16;++i) s->bytes[i]=255;
    }
}
