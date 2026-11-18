#ifndef CADET_RULES_H
#define CADET_RULES_H
#include <stdint.h>
typedef struct { uint8_t bytes[16]; uint8_t overflow; } cadet_score;
uint16_t cadet_bumper_award(uint8_t bank, uint8_t level);
uint16_t cadet_rebounder_award(void);
void cadet_add_score(cadet_score *score, uint32_t award);
#endif
