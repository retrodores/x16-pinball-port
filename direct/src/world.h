#pragma once
#include "port_types.h"
#include "world_params.h"
#include <stdint.h>
struct Edge {
 uint8_t type,kind;uint16_t component;
 float elasticity,smoothness,threshold,boost;
 union {line_type line;circle_type circle;} shape;
};
static_assert(sizeof(Edge)==68,"portable packed record layout");
namespace world {
extern TBall ball;
extern bool drained;
extern uint16_t contacts;
bool load();
void launch();
void frame(float dt);
void start();
void input(bool left,bool right,bool pullback);
void tick();
}
