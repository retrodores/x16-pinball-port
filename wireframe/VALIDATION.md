# Validation — wireframe 0.2

Release date: 2026-11-17. Tested with X16 emulator and matching r49 ROM.
The shipped table is the new original wireframe practice table. Stock 65C02
is the primary target; the optional 65816 build is compatibility coverage.

## Sustained play and timing

| CPU | RAM | MHz | Simulation steps | Worst work cycles | Mean work cycles | Draw calls/s | Distinct draw ticks/s | Longest draw gap |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| c02 | 512 KB | 2 | 14,638 | 114,561 | 17,515 | 59.69 | 57.08 | 66.7 ms |
| c02 | 2048 KB | 2 | 14,638 | 114,561 | 17,515 | 59.69 | 57.08 | 66.7 ms |
| c02 | 512 KB | 8 | 14,638 | 74,828 | 17,003 | 60.00 | 60.00 | 16.7 ms |
| c02 | 2048 KB | 8 | 14,638 | 74,828 | 17,003 | 60.00 | 60.00 | 16.7 ms |
| c816 | 512 KB | 8 | 14,638 | 75,245 | 16,963 | 60.00 | 60.00 | 16.7 ms |
| c816 | 2048 KB | 8 | 14,638 | 75,245 | 16,963 | 60.00 | 60.00 | 16.7 ms |

Each configuration completed three games / nine drains. Every 120-step native
snapshot matches the host integer solver, and the optimized host replay matches
the unpruned collision reference. Each run advances 14,638 physics steps across
14,638 video ticks: no accumulated game-time loss at either CPU clock.

The strict 8 MHz budget remains 133,333 cycles per rendered update. Every measured
8 MHz update passes; all four configurations complete one draw per video tick.
Work includes physics, rendering, instrumented autoplay and IRQ audio service.
A low-clock catch-up batch may perform two physics steps before drawing.

At 2 MHz there are 14,563 draw calls across 14,638 video ticks. Some catch-up
draws land within the same tick, so 59.69 draw calls/s is not the same as 59.69
distinct screen refreshes/s. About 57.08 distinct video ticks/s receive a draw.
Only 13 draw intervals per run exceed two ticks; the longest is four ticks
(66.7 ms). Physics time remains correct. Recommend 8 MHz for uniform motion.
Warp mode only shortens the wall-clock test; launchers use normal emulator speed.

## Boundaries, physics and controls

- 3,213 directed perimeter shots, including endpoints/corners: zero escapes.
- 120 host games / 360 balls: zero stalls, timeouts, off-table escapes or collision
  iteration guard exhaustions; six legitimate timed capture returns.
- Twenty targeted assertions pass on the host and both CPUs at both RAM sizes:
  integer arithmetic, five bumpers from four directions each, resting/moving
  flippers at six contact positions each, wells, sink, kickbacks, ramp rollback,
  target-bank completion, full-width score carry/overflow and three-ball lifecycle.
- Actual distribution PRGs pass SDL keyboard tests: new game, full-charge launch,
  visible spring compression, flipper movement, frozen pause, M music indicator,
  nudge/sound keys and return to BASIC. Coverage: 65C02 at 2/8 MHz and both RAM
  sizes; 65816 at 8 MHz and both RAM sizes. Recorded audio is non-silent.
- A separate normal-PRG keyboard run confirms the visible score advances during
  play. PREVIEW.png is an actual emulator screenshot from this run.
- No runtime floating-point helper symbols occur in either game PRG.
- Preserved legacy modules pass `prove -v t/native.t` at 512 KB and 2048 KB.

A stall check observes less than 30 Q8 units of net motion at consecutive
one-second samples for more than eight seconds while in play. No automatic
teleport or rescue conceals a trap. Finite stress coverage is not proof that
every possible shot is safe; continued human play remains useful.

## Sound and music

Actual emulator WAV captures pass at both RAM sizes on 65C02 (2 and 8 MHz)
and 65816 (8 MHz). Tests cover seven non-silent triangle-wave effects, a complete
17.07-second two-voice music loop and wrap, independent music mute/resume, pause,
all-sound mute, stop, IRQ cleanup, RAM-bank preservation, arithmetic during
audio and preservation of both VERA address ports and CTRL.

Effect envelopes use short attacks and decays. Recorded effect energy above
6 kHz stays below 4%; peak output stays below 12,000 on a signed 16-bit scale.
These checks catch clipping, missing music and harsh high-frequency regressions;
preferred listening volume remains subjective. The music is an original short
loop, not the original Space Cadet theme.

## Limits

Original Space Cadet missions/ranks, tilt penalties, multiball and persistent
high scores remain future work. Windows batch launchers are provided; validation
used Linux SDL emulation. Real X16 hardware has not been tested in this session.
