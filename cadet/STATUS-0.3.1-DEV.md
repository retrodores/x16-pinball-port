# CmdrX Cadet 0.3.1-dev — slingshots, control audio and music

Author: Codex, working with Brett Estrade. November 19, 2026 (America/Chicago).
Baseline: 08c5843429210f6e558a347bc8551164962a7916. This is a development build.

## Corrections

- Original slingshot rubber and triangular lightning glow animate together for six frames. Upper rebounders also flash on qualifying impacts.
- Separate PCM voices for table effects, flippers and plunger preserve simultaneous original effects. Input reversals sound without duplicate collision cues.
- Plunger input now works while the ball is elsewhere; feed/release cues are explicit and the original pull cadence is retained.
- Low-latency PCM scheduling keeps the original sample rate. New cues do not flush another voice; underrun telemetry survives game restarts.
- Original converted soundtrack remains enabled by default. M toggles music with a visible ON/OFF/priming indicator.
- Preserved stock integer-only 65C02, 512 KB support, original artwork and exact 128-bit scoring.

The submitted recording confirms missing lower slingshot effects at 37.72/41.95s.
Original video shows rubber and lightning for about 0.1s. The submitted plunger
release matches the original sample at its original playback rate. These fixes
address cue delivery, overlap and latency rather than altering pitch.
See evidence/obs-2026-11-19 and game/FEEDBACK-0.3.1.md.

## Final integrated measurements

| RAM | Frames | Worst cycles | Mean cycles | Over133333 | PCM underruns | Music errors |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 512 KB | 12000 | 214329 | 68691 | 94 | 0 | 0 |
| 2048 KB | 12000 | 214193 | 68692 | 95 | 0 | 0 |

Both strict timing checks retain their failing exit status. Mixing adds real CPU
cost and more overruns than 0.3. The measured workloads have no PCM starvation or
music-buffer errors. No sustained 60 FPS claim.

## Verification

- 80 input/rebounder contracts, 216 mechanism assertions and native 128-bit award boundaries pass on host/native at 512 KB and 2 MB.
- 254 route/layer checks, 10 tip checks and powered/passive contacts pass both RAM sizes after final bank relocations.
- 40-seed optimized/exhaustive sanitizer soaks agree at 689df8e0: 117 drains, zero escapes/stalls; seven contact-guard uses remain.
- 21577 graphics checks and 234 actual collision-to-render checks pass per RAM size; lower flashes change on the first zero-budget update and expire after six frames.
- Final 12000-frame integrated runs include deliberate captures/kickbacks and music restarts beyond frame6000, with zero cumulative PCM underruns and music-buffer errors.
- Interactive UI passes both RAM sizes: artwork, lamps, plunger/flippers, play, F2, music OFF/ON/restart and exit. Under concurrent tests the 2 MB music restart took 1.600 seconds.
- Native arithmetic, music streams, depth quantizer, pixels, bounds and 50 host/native checkpoints pass both RAM sizes.
- Independent ELF extraction matches final PRGs and distinct overlays. Bank-changing trampolines are resident and noinline.
- 18 packaging tests cover flat layout, matching source/runtime and four DYN banks. Prior 0.3 and accepted 0.2 packages are preserved.

Recorded audio passes both RAM sizes: three overlapping PCM voices, 128 short
cues without queue growth, actual music ON/OFF and restart. A complete 32050-VBL
soundtrack loop passes at 512 KB with zero PCM/music errors. The extra 2 MB
full-song run stopped at its clean 20000-frame checkpoint and remains partial.
Measured flipper onset is 23.38 ms in the capture fixture.
Detailed measurements accompany the evidence.
The package is also extracted, rebuilt and run independently before delivery.

## Remaining limitations

- Strict 133333-cycle budget still fails: 94/95 of 12000 frames exceeded it at 512 KB/2 MB; worst about 26.8 ms. Mixing raises CPU cost. This is not stable or sustained 60 FPS.
- The supplied original installer lacks sound62.wav, referenced for pull-start by its DAT. No unrelated sample was substituted. Feed and release use supplied original cues.
- Music instrument timbre remains an X16 conversion; three-way PCM uses headroom attenuation and is not the Windows mixer.
- Moving-flipper continuous contact, tapered-face normals, advanced hyperspace/jackpot/blocker/extra-ball/reflex rules, missions and some cues remain unfinished.
- Spinner callbacks, randomized throws, individual lamp phases and other dynamic-object depth maps remain incomplete.
- Only the two lower slingshot composites have immediate map swaps; other large dynamic changes remain incremental.
- Windows launcher flags/quoting are statically checked; Windows execution was not available.

## Run

Extract all files below parent x16emu.exe and matching rom.bin.
RUN-WINDOWS.bat retains game cwd and -c02 -mhz 8 -ram 512 -scale 2.
Keep CADET.PRG, CADET.RUL, CADET.PHY and every BIN together.
Space pulls/releases; Z/left Shift and slash/right Shift operate flippers;
F2 starts a game; M toggles music; Escape exits.
Music starts enabled, shows ... while priming, then ON; OFF means muted music.
SOURCE.zip and RESUME.md contain build and recovery instructions.
