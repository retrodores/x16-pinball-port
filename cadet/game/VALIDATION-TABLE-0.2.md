# Original Table Test 0.2 validation — 2026-11-18

Stock x16emu r49, matching r49 ROM, 65C02, LLVM-MOS SDK 23.4.0.
Recorded machine-readable evidence is under cadet/evidence/table-0.2.

## Integrated native runs

The cycle interval begins at the audio/video interrupt timestamp and ends after
physics and drawing. It therefore includes the starting audio IRQ, KERNAL IRQ
tail and main-loop wakeup. Low cycle-counter byte is always read first.
The 133,333-cycle limit was retained.

| RAM | CPU | Frames | Worst cycles | Mean cycles | Frames over 133,333 | Late starts |
|---|---|---:|---:|---:|---:|---:|
| 512 KB | 8 MHz | 6,000 | 128,260 | 29,122 | 0 | 0 |
| 2 MB | 8 MHz | 6,000 | 128,371 | 29,122 | 0 | 0 |
| 512 KB | 2 MHz | 6,000 | 193,253 | 36,281 | 38 | 577 |

All three runs reported zero music stream errors. The 2 MHz column still counts
the fixed 8 MHz contract threshold; it is not a count of all 2 MHz deadlines.
At 2 MHz there were 577 updates that began after more than one video tick, so
2 MHz is not yet smooth. Best at 8 MHz.

These are measured scripted workloads, not a proof of the worst possible frame
under every shot. The integrated tests run approximately 101 seconds of video
time each at 8 MHz, with normal video/IRQ emulation (not emulator testbench mode).

## Physics and arithmetic

- Forty varied three-ball host games under address/undefined-behavior sanitizers:
  120 drains, zero escaped balls, zero detected stalls, 378 bumper hits,
  532 flipper hits, 137 ramp entries, 68 capture returns.
- Same forty games with an exhaustive search through all 1,217 edges instead of
  the spatial index: identical complete Game-state hash, 91cbf84c, and counters.
- One five-contact guard use occurred across the forty games. No escape or stall
  followed it; full continuous original solver equivalence is not claimed.
- Native and host positions, velocities and play state matched at all 50
  checkpoints spaced through a 6,000-frame physics run.
- Native exact arithmetic tests: 8,292 signed multiplication cases (including
  signed boundaries), and 3,856 bounded fraction checks against compiler
  arithmetic. All passed.
- Runtime C contains no float/double arithmetic. Small assembly helpers are
  65C02 arithmetic and native audio service; no 65816 mode is required.

The recovered original primitives/masks are used. Exhaustive-search agreement
proves the tested index optimization preserves this C solver; it does not prove
all flipper impulses, capture forces, timing or mission behavior match the
original executable. Controlled original-shot replays are still needed.

## Graphics, controls and audio

- Interactive stock emulator test: held Space animates the plunger; release
  launches; held Z and / animate both flippers; F2 starts a new game; M toggles
  music; Escape returns cleanly to BASIC.
- Captured unaffected table pixels exactly matched the packed VERA reference.
  Original-resolution art is spatially unchanged; palettes are color reduced.
- The final UI test captured audible output (RMS 3,824.92; peak 24,797 in signed
  16-bit samples) and passed the animation/exit checks.
- Original movable assets deduplicate to 145 16x16/4bpp tiles (18,560 bytes).
  Background + sprite patterns + status font end at VRAM 0x1e680.
- Twelve resident PCM clips occupy 98,056 bytes and retain the previously
  validated signed 8-bit conversion at VERA rate register 29.
- Theme stream shrank from 272,155 to 214,255 bytes. Independent decoding found
  identical register state at every one of the 31,676 musical ticks, and all
  21,801 key/control side-effect events matched in order and timing.
- The previous lab validated all 60 PCM conversions and full native theme loops
  at both RAM sizes. This checkpoint adds resident loading/event dispatch and
  compact-stream equivalence; it does not claim a new complete acoustic match
  to the original Windows mix or original GM soundfont.

## Recovery

The accepted wireframe and lab remain untouched in their existing artifacts.
The release includes generated assets/headers and complete source recovery.
No original game EXE or emulator ROM is included.
