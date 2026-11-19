#include "engine.c"
#include "verify_milestone_input.h"
#include <stdio.h>
int main(void){if(!game_load())return 1;game_start();for(uint16_t i=0;i<12000;++i){uint8_t before=milestone_placement_index;milestone_setup(i);game_frame(i%43<12,i%67<14,game.state==Serving&&game.charge<80,false);if(game.state==GameOver)game_start();if(before!=milestone_placement_index)printf("frame%u target#%u eventgroup%u kind%u events%u state%u\n",i,before,original_groups[game.last_group],game.last_kind,game.events,game.state);}return 0;}