# Collision and audio preview 3 validation — 2026-11-16

Tested with emulator/ROM r49 on Linux at 8 MHz, both 512 KB and 2048 KB RAM,
and both 65C02 and experimental 65816 CPU variants.

- 33 targeted contact checks: all seven bumpers hit from all four cardinal
  directions (28 rebounds/boosts/flashes), wrong-layer rejection, six resting
  and six swept contact positions on each paddle, and seven ramp transitions.
- Eight short key press/release sequences through the actual keyboard handler
  remain latched, including both flipper key aliases and the S sound toggle.
- World, mechanisms, flipper and targeted contact traces match the integer host
  exactly on both CPU/RAM combinations. Restoring the four-record cache changes
  no host trace. All 40 full-charge release holds still clear the chute.
- Arithmetic oracle covers 65536 byte products and 4096 wide products; all 96
  flipper differential records and 40 contacts remain within existing explicit
  fixed-point bounds. Original float/vendor method files remain unchanged.
- Normal-ROM instrumented checks and real SDL keyboard/screenshot checks pass
  feed, charge, launch, flippers, pause and clean return to BASIC on all four
  configurations. No runtime soft-float helpers are linked.
- Seven actual VERA PCM recordings pass waveform comparison against their
  source samples on all four configurations (minimum correlation
  0.96162, required >0.95).
  Full waveforms cover RAM-bank boundaries. IRQ tests stress multiplication
  during playback and check bank preservation, mute, stop and vector cleanup.
  The recorder stays active at exit because r49 does not finalize paused WAVs.

## Current timing

Both normal and instrumented builds use -Oz. These figures describe the
instrumented 760-frame mixed sequence, not an exact cycle profile of the normal
binary or an active-play-only average. The added layers/audio change the workload
and trajectory, so historical preview-2 percentages are not current speed claims.

| CPU | Average cycles | Maximum cycles | Maximum ms | Over 133333 cycles |
| --- | ---: | ---: | ---: | ---: |
| 65c02 | 92739 | 451279 | 56.41 | 80 / 760 |
| 65816 | 92370 | 449391 | 56.17 | 78 / 760 |

The strict 133333-cycle gate remains FAIL; this is an incomplete mechanics
preview, not a stock-speed 60 Hz gameplay release. Launchers use neither warp
nor overclocking. No physical hardware or Windows-host test was performed.

## Assets and memory

WORLD.BIN is 219824 bytes: 854 edges, including
65 ramp edges and seven bumpers. Its CY signature differs
from the earlier integer world. Banks 32..58 hold the model; flipper lookup data
uses banks 8..23; UI is bank 1; PCM effects use banks 24..31 and 2.
UI.BIN is 7039 bytes. Standard/native CMDRX.PRG sizes are
34836 / 34836 bytes.
Each variant must keep its paired UI.BIN. All nine BIN files are required.

Other table mechanisms, rules/missions, scoring/saves, music and ramp/tunnel
visual occlusion remain unfinished. The original sound effects use one
priority-based PCM voice, not the complete original sound mixer.

BUILD.json identifies the source commit and every shipped runtime hash. Source,
exported ramp data, original converted SFX input, native traces and reproducible
tests are included. This worktree has no GitHub remote; no push is claimed.
