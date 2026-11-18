# CmdrX Cadet — 0.3 work in progress, 2026-11-18

**This is a source/recovery checkpoint, not a new recommended game release.**
Original Table 0.2 remains the latest accepted runnable release. Its Git tag
is table-test-v0.2 (c8312ad), and its binaries remain preserved separately.

Implemented in this checkpoint:
- Original table depth-map ball masking, using the high eight bits of each
  original 16-bit depth sample; all 171550 quantized pixels verified.
- Correct Euclidean camera distance for ball sizing and depth comparison.
- Banked sprite/projection metadata; full-size original numeric glyphs retained.
- Lossless theme compression: 214239 command bytes -> 102730 stored bytes.
  A bounded main-thread producer fills a 4096-byte dictionary/read-ahead buffer;
  the IRQ consumes buffered music. Prefetch work is included in frame timings.
- Exact native arithmetic and collision-filter helpers. Collision topology and
  tested trajectories are unchanged. Score remains exact unsigned 128-bit.
- Expensive backbox changes can wait for a quieter frame; ball, flippers and
  physics update immediately. Existing original art and twelve PCM effects remain.

## Release blocker

The required limit is 133333 cycles per frame at 8 MHz. It has NOT been relaxed.

| RAM | Frames | Worst cycles | Mean cycles | Over limit | Music errors |
|---|---:|---:|---:|---:|---:|
| 512 KB | 6000 | 144411 | 39414 | 5 | 0 |
| 2048 KB | 6000 | 144308 | 39414 | 5 | 0 |

Worst measured frame is 18.05 ms, versus the
16.67 ms contract. Both integrated budget tests intentionally FAIL. These
scripted workloads do not establish a universal worst case. No new 2 MHz
performance claim is made.

## Functional checks

- Forty three-ball host games with sanitizers: 120 drains, zero escapes, zero
  stalls, 378 bumper hits, 532 flipper hits, 137 ramp entries, 68 returns.
  One five-contact guard use, as in 0.2.
- Optimized and exhaustive 1217-edge searches both hash to 91cbf84c, identical
  to the accepted 0.2 host baseline. Host/native trajectories match at 50 points.
- Native bounds helper: 14604 signed comparisons. Native pixel compositor:
  32768 VERA bytes checked. Native depth: 384 rectangles, 6144 rows plus varying
  sprite sizes, including table boundaries; both RAM sizes passed.
- Native depth quantizer: 5500 distances. Arithmetic: 8292 signed products,
  3856 narrow fractions, 4096 wide fractions, 2049 rebound ratios.
- Host score oracle: all 65536 uint16 awards, all 128 carry boundaries, and
  255 full-width overflow checks.
- Native music: 856956 bytes compared with the original compact command stream,
  covering decoder resets and buffered automatic looping. No byte differences.
  The compact stream still matches all 31676 musical ticks and 21801 key/control
  side-effect events from the original conversion.
- Current interactive emulator check passed background pixels, plunger/flipper
  animation, launch, new game, music toggle, exit and audible output. This is not
  an acoustic identity claim against the original Windows instruments/mixer.

## Still unfinished

Original target-bank resets, real rollover states, gates, bonus/skill shots,
missions, dynamic bumper/target/lamp graphics, original message text/font and
high-score controls. Research notes are in ORIGINAL-RULES-NOTES.md; these rules
have NOT been integrated. Depth currently comes from the static table map;
separate dynamic sprite depth maps are not included. The display footer still
uses the accepted 0.2 artwork because this is not a new release package.

Next priority: remove the remaining collision-frame spikes, repeat the same
strict tests, then integrate the original rules with source-derived fixtures.
Start recovery with cadet/RESUME.md. Build with sh cadet/game/build.sh.
The Windows launcher preference remains parent x16emu.exe/rom.bin, flat files,
65C02, 8 MHz, 512 KB, -scale 2, and the game directory as current directory.

Original reconstruction: Andrey Muzychenko / k4zmu2a, MIT source.
Original art/audio: Cinematronics and their respective rights holders.
X16 adaptation and validation: Codex, working with Brett Estrade.
