# Wireframe 0.2

- Stock 65C02 is the primary target; add a 2 MHz Windows launcher while recommending
  8 MHz. Fixed 60 Hz physics catches up across slower render frames without losing
  elapsed simulation time. The same PRG runs at either clock rate.
- Reject balls outside each flipper's actual capsule before expensive projection
  arithmetic. Preserve identical collision results against the unpruned replay;
  this removes most low-clock pauses around the lower slings.
- Join the perimeter at its offset-line intersections, close the upper corners,
  and replace the open lower edges with two slopes feeding one marked drain.
  Close sling collision polygons and render their continuous physical outlines.
- Add an animated wireframe spring plunger that compresses with Space and snaps
  forward on release. Keep the charge meter as a second indicator.
- Move the live score directly below SCORE. Use cheap sprite glyph updates and
  retain exact 128-bit values, including all 39 decimal digits and overflow handling.
- Replace harsh PCM playback with seven original, soft triangle-wave effects with
  envelopes and separate flipper/ball voices. Add quiet, original two-voice music.
- Add M for independent music, S for all audio, visible S/M indicators and music
  pause/resume. Preserve both VERA address ports, RAM banks and the prior IRQ.
- Add directed perimeter shots, escape counts, low-clock render/physics cadence
  checks, music-loop/pitch/quietness tests and real-keyboard plunger/music checks.

The accepted 0.1 checkpoint is preserved. Original-table restoration is deferred
while this wireframe table is refined as a playable standalone game.

# Wireframe 0.1 — 2026-11-17

Established the new practice layout, integer swept-collision engine, basic
mechanisms, three-ball lifecycle, original PCM effects and emulator test suite.
Original Space Cadet missions/ranks, tilt, multiball and high-score persistence
remain future work.
