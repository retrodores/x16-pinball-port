# Validation — wireframe 0.1

Tested 2026-11-17 with X16 emulator/ROM r49 at 8 MHz. The shipped layout is the
new original practice table, not the recovered Space Cadet layout.

## Sustained play and timing

| CPU | RAM | Frames | Worst cycles | Average cycles | Over budget | Balls drained |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| c02 | 512 KB | 13,065 | 81,384 | 28,968 | 0 | 9 |
| c02 | 2048 KB | 13,065 | 81,384 | 28,968 | 0 | 9 |
| c816 | 512 KB | 13,065 | 82,132 | 28,955 | 0 | 9 |
| c816 | 2048 KB | 13,065 | 82,132 | 28,955 | 0 | 9 |

Each configuration plays three complete games with different plunger charges and
flipper periods. Native replay snapshots match the host integer engine. The
unpruned collision reference produces the same host replay. The strict budget
remains 133,333 cycles per frame; measured work includes physics, rendering and
sound IRQ service. Instrumented playback runs with emulator warp only to shorten
testing; launchers use normal 8 MHz timing. This is measured test coverage, not a
proof of every possible shot.

The separate host stress run completed 120 games / 360 balls with five timed
capture returns, no detected stalls, no timeouts and no collision-iteration guard
exhaustions. A stall is less than 30 Q8 position units of net motion at consecutive
one-second samples for more than eight seconds while in play. No automatic rescue
is used. Human play remains useful for tuning table difficulty.

## Mechanics and controls

- Twenty targeted mechanics/arithmetic assertions pass on the host and all four
  CPU/RAM combinations: five bumpers from four directions each; both resting and
  moving flippers at six contact positions each; captures, kickbacks, ramp rollback,
  bank completion, 128-bit scoring/overflow and the three-ball lifecycle.
- The exact distribution PRGs pass actual SDL key tests for new game, full-charge
  launch, moving flippers, pause/resume and clean exit. Nudge and sound-toggle keys
  are sent; recorded audio is non-silent. The screenshots and logs are retained.
- Seven individual recorded PCM effects match the source samples in all four
  configurations. IRQ bank preservation, arithmetic during playback, mute, stop
  and cleanup pass.
- The preserved earlier engine also passes `prove -v t/native.t` with both 512 KB
  and 2048 KB RAM. It is separate regression coverage, not the shipped game.
- No runtime floating-point helper symbols are present in either PRG.

## Limits

This is a new wireframe practice table and basic ruleset. It does not implement
the original Space Cadet missions/ranks, tilt penalties, multiball, music or saved
high scores. Windows launchers are provided; the PRGs were exercised under Linux
SDL emulation. Real X16 hardware has not been tested in this session.
