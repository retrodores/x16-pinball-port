// Original initialized TPlunger constructor parameters.
#pragma once
static void initialize_plunger(TPlunger& p) {
 p.MaxPullback=100.0f;
 p.PullbackIncrement=1.0f;
 p.PullbackDelay=0.0250000004f;
 p.Elasticity=0.5f;
 p.Smoothness=0.5f;
 p.bitmaps.count=8;
}
constexpr float serve_y=10.0848541f;
