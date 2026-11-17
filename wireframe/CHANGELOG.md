# Wireframe 0.1 — 2026-11-17

- Rebuilt the game around a new 47-edge practice table with five bumpers, two
  moving flippers, nine drop targets, a standing target, three rollover lanes,
  a spinner, raised ramp, gate, timed pocket, central well and two kickbacks.
- Integer-only swept collisions, fractional acceleration and motion, explicit
  collision layers, timed captures, three-ball games and a player-controlled nudge.
- Preserved the original recovered table separately. The dense recovered layout
  failed the worst-frame budget and is not the layout shipped by this release.
- Fixed slope-transition suppression by tracking individual ramp edges.
- Added VERA sprites for ball, flippers, event lights and retracting targets/gate.
- Retained seven original PCM effects with bank-safe IRQ playback and clean exit.
- Retained exact unsigned 128-bit scoring and explicit overflow reporting.
- Added native mechanics, audio-waveform, full-game timing and real-keyboard checks.

The original Space Cadet mission/rank rules, tilt penalties, music, multiball and
persistent high scores remain unimplemented. This is a playable foundation for
future artwork and rules, not a complete original-game port.
