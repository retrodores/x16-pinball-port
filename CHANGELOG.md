# Changelog

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
