# Changelog

## Direct mechanics checkpoint — 2026-11-16

- Port original moving-flipper contact, rebound, motion and swept-collision methods
  to native C++; export original constructor geometry instead of recreating it.
- Port original plunger messages and feed/charge/release callbacks, with bounded
  native timers and a single-ball ownership adapter. Integrate actual charged
  launches and moving flippers into the original-coordinate world probe.
- Reject distant static edges with conservative banked bounds; retain the original
  float formulas and compare every launch frame to the prior direct baseline.
- Fit the combined diagnostic in native main memory using banked lookup data,
  compact parameter initialization and size-oriented compilation.
- Pass 736 functional/differential checks across 512 KiB and 2 MiB. Keep the strict
  133333-cycle gameplay gate failing: 525087 launch-only cycles and 1089833
  combined-mechanics cycles are still over budget.
- Preserve pristine vendor source, the previous direct reference, and the older
  Prog8 prototype. This is a development checkpoint, not a playable release.

## 0.2.0

- Enlarge the silver ball from 5 to 7 pixels and run two solver steps per frame,
  halving the initial prototype's simulation pace.
- Replace the rough trapezoid with a baked contact field from 56 original
  base-layer wall groups. Smooth normals and safe sliding handle curved rails.
- Remove the artificial sideways jump and velocity reset during launch.
- Animate all eight original plunger frames during charge and spring return;
  move the waiting ball with the plunger.
- Replace synthesized placeholder beeps with original WAV recordings.
- Stream the complete PINBALL.MID theme as converted PCM, mixed with effects.
  PINBALL2.MID is a font resource, not a second song.
- Add independent S/M sound/music toggles, attract play with lamp cycling,
  and L music-only listening. N starts a real game.
- Redesign the side panel with cards, color, readable status and audio settings.
- Extend native regressions for walls, continuous launches, plunger animation,
  modes, independent audio, PCM streaming and bank restoration.

## 0.1.0

First native mechanics prototype with ball, flippers, bumpers, plunger, drain,
three lives, pause/restart, exact unsigned 128-bit scores and high-score saves.
