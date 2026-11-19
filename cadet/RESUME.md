# Resume CmdrX Cadet — 0.3.1 development follow-up

Author: Codex, working with Brett Estrade. Session date: November 19, 2026 (America/Chicago).

## Checkout and preservation

Use Desktop Commander on the authorized VM. Repository:
`/opt/cmdrx-cadet-fidelity`, branch `spacecadet-fidelity`.
This milestone started from verified clean commit
`08c5843429210f6e558a347bc8551164962a7916`.
Read root/cadet AGENTS.md, this file, OBS-REVIEW.md and STATUS-0.3.1-DEV.md.

Original Table 0.2 remains preserved at tag `table-test-v0.2`
(`c8312addc4c05994ae8a3de400a2d1d7dac8aeab`) and
`/opt/cmdrx-cadet-table02-assets`. The 15 accepted runtime files were compared
byte-for-byte with the delivered ZIP. Wireframe 0.2 remains unchanged in
`/opt/cmdrx-cadet-direct`, clean at `51149308b350ca485d36ec73713c6bbf2cba5e41`.
Vendor source is unchanged. This is a separately labeled DEVELOPMENT build.

## Latest feedback corrections

Lower slingshots now switch a depth-composited rubber/glow image immediately
through 27 private VERA map entries; upper rebounders also flash. DYN3 uses
bank63. Alternate fire patterns use 3456 VRAM bytes after the font/ball buffer.
Three PCM voices keep table, flipper and plunger effects independent.
A bounded 256-sample initial queue then follows 185/186 samples per VBL.
Track cumulative pcm_underruns and music_error; game restarts must not erase them.
Music starts enabled, with M and a visible ON/OFF/priming indicator.

Bank-switching trampolines MUST be resident and noinline. LLVM otherwise inlined
a bank61 switch into event_core executing in bank62, banking out its own code.
Final native event/award fixtures and ELF checks guard this boundary.

## What is implemented

Source-derived wormhole destinations/awards/replay and capture/release timing;
kickout hold, return and component-specific reset; both kickbacks and hazard gates;
yellow three-lane banks, flipper lane rotation, bumper upgrades/decay; 39 original
lamp/bumper/gate/kicker visual components driven by events and timers.
Wormhole/kickback/hazard/hyperspace base PCM effects are resident. Music startup
primes in bounded interruptible batches instead of blocking for a full refill.
Original quantized depth masking is now losslessly compressed to free banked RAM.
The powered-flipper fix is preserved, with a new stationary grazing-tip sweep.

See game/MECHANISMS-MILESTONE.md, game/AUDIO-MILESTONE.md and
game/verify_milestone_physics.md for original-source contracts, tests and limits.
OBS-REVIEW.md is historical evidence; its original missing-feature list describes
the pre-milestone build. Recordings supplement source-derived fixtures and do not
make soak results proof of fidelity.

## Build and recovery

Runtime: integer-only stock 65C02, 8 MHz, 512 KB. No 65816 requirement.
Compiler: LLVM-MOS SDK 23.4.0 at
`/opt/llvm-mos-sdk-23.4.0/llvm-mos/bin/mos-cx16-clang`.
Emulator: `/opt/x16emu-r49/x16emu`, matching adjacent rom.bin.

```sh
sh cadet/game/build.sh
# Full regeneration, when the original inputs below are available:
sh cadet/game/build.sh assets
```

Source archive includes generated headers and matching runtime assets, so rebuilding
the PRGs does not require regenerating artwork or obtaining the DAT again.
Full asset regeneration uses:
`/opt/spacecadet-x16-analysis/input/game/PINBALL.DAT`,
`/opt/spacecadet-x16-analysis/evidence/inventory.json`, recovered source under
`direct/vendor/SpaceCadetPinball`, Python/Pillow/NumPy and the existing conversion
tools. Development dependencies may be installed as already authorized.

build_native.py uses the custom linker layout and creates each PRG with its own
.RUL and .PHY companion. Never mix overlays from different builds/programs.
Both overlays execute at A000 in different physical RAM banks. Extract their
**named ELF sections**; LLVM's raw FULL(region) writer cannot distinguish the
overlapping virtual addresses and previously emitted incorrect sidecars.
test_build_native.py independently verifies the emitted bytes with LLVM objcopy.
Main RAM must leave at least 1 KB below the 9f00 software-stack start.

## Live RAM bank allocation

| Banks | Contents |
| --- | --- |
| 1..9, 12..16 | Original indexed collision geometry |
| 10 | Compressed depth index |
| 11 | Sprite/projection/quantization UI metadata |
| 17,18,45..50 | Compressed original quantized depth blocks |
| 19..30,51..57 | 17 PCM samples |
| 31 A000..AFFF | Music dictionary/read-ahead |
| 32..44 | Losslessly compressed theme commands |
| 58..60,63 | Dynamic patches and instant slingshot composites |
| 61 | Rules and powered-paddle code (.RUL) |
| 62 | Tip sweep, event dispatch and speed limiter (.PHY) |

Geometry loading temporarily writes obsolete padding into 10/11/17/18; later
loaders replace it before gameplay. All live banks fit 512 KB.
Compressed depth reproduces all 171550 quantized pixels exactly. Dynamic patches
preserve neighboring nibbles and write at most 128 bytes per permitted update.

## Required verification

```sh
python3 cadet/game/test_build_native.py CADET TEST
python3 cadet/game/test_feedback_events.py
python3 cadet/game/test_slingshot_render.py
python3 cadet/game/test_audio_mix.py
python3 cadet/game/test_mechanisms.py
python3 cadet/game/test_large_award.py
python3 cadet/game/test_routes.py
python3 cadet/game/test_flipper_contact.py
python3 cadet/game/native_check.py 512
python3 cadet/game/native_check.py 2048
python3 cadet/game/test_depth.py 512
python3 cadet/game/test_depth.py 2048
python3 cadet/game/test_dynamic.py
python3 cadet/game/test_audio.py
xvfb-run -a python3 cadet/game/test_ui.py
CADET_RAM=2048 xvfb-run -a python3 cadet/game/test_ui.py
python3 cadet/game/test_native.py 512 8 12000
python3 cadet/game/test_native.py 2048 8 12000
python3 cadet/game/test_package_development.py
```

Check each runner's CLI before changing fixtures. Large awards preflight the full 32-bit award before chunking, preserving both score
and decimal digits atomically on overflow. test_award_large.c adds sanitized
carry/limit regression; test_large_award.py exercises real banked hyperspace awards.
Host score tests cover every
uint16 award and all 128-bit carries. Host optimized and exhaustive 40-seed soaks
now agree at hash `689df8e0`, with zero escapes/stalls; some games reach the
18000-frame cap. Seven contact-guard uses still need investigation.
The integrated TEST includes measured music restarts/cancellation after frame6100
and 19 deliberate source-geometry placements at frames7000..10900. These placements
exercise cost and mechanisms, not proof of legal player routes.

The strict budget remains 133333 cycles. Measurement includes physics, rendering
and music prefetch, including IRQ costs. Do not move work outside the measured
interval or relax the threshold. The current development build does not pass
the sustained-60-FPS gate. See STATUS-0.3.1-DEV.md and evidence/feedback-0.3.1.

## Packaging and next work

Commit source, notes and selected evidence before running package_development.py.
Supply the tested commit and actual native results in the validation JSON.
The ZIP is flat; CADET.PRG, CADET.RUL, CADET.PHY and all BIN files are required.
RUN-WINDOWS.bat keeps game-directory cwd, uses parent x16emu.exe/rom.bin and
`-c02 -mhz 8 -ram 512 -scale 2`. No emulator, ROM or Windows executable is bundled.

Continue profiling collision clusters and depth/graphics work. Complete moving-tip
continuous collision and tapered flipper face normals, advanced hyperspace
jackpot/blocker/extra-ball/reflex rules and missing cues, spinner callbacks,
mission/rank/bonus/message UI, randomized throws and per-lamp phase fidelity.
Dynamic object depth maps and some multi-frame visual updates remain imperfect.
Do not describe the development build as a complete or note/pixel-perfect port.

## Engine and local-import checkpoint

The PCM mixer keeps its within-page sample offset in Y. The mixer changes the
read page only when Y wraps, including the existing bank 30 to 51 transition.
The strict test on a stock 65C02 at 8 MHz still fails. The updated 12,000-frame
runs measured 211,209 / 211,215 worst cycles and 90 / 90 over-budget frames at
512 KB / 2 MB, with zero PCM underruns, music errors, or reported frame-start gaps.
Mean cost was 67,879 cycles in both modes. The development label remains.

Use `cadet/game/import_local.py` and see `cadet/game/IMPORT.md` for the
code-only distribution and private asset conversion. The converter uses a
supported local installation and the existing checkout's two pinned reference
inputs. Its fresh build reached PLAY READY on Linux at both RAM sizes and all
30 runtime files matched the developer build byte-for-byte. Windows execution
has not been verified.
