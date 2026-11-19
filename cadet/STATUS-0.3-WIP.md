> Historical 0.3 milestone. Current follow-up: STATUS-0.3.1-DEV.md.

# CmdrX Cadet 0.3-dev — playable development milestone

Author: Codex, working with Brett Estrade. Session date: November 18, 2026 (America/Chicago).

This is a runnable development playtest, not a stable or complete Space Cadet port.
Original Table 0.2 and Wireframe 0.2 remain accepted and preserved. Source-derived
fixtures establish the listed contracts; recordings and soaks are supporting
evidence, not proof of complete fidelity.

## Implemented

- Wormhole capture, selected exit, hold, release, replay and scoring; kickout capture/return and basic hyperspace levels.
- Both side kickbacks with firing/reset timers, real access gates and hazard-target completion.
- Both yellow 1/2/3 lane banks, flipper rotation, completion and four bumper levels.
- 35 original bumper/lamp/gate/kicker components respond to actual events and timers; original artwork, plunger and score UI retained.
- Five additional original PCM effects; music starts/restarts with bounded priming instead of blocking the game.
- Original quantized depth masking compressed without loss; stationary grazing flipper-tip collisions fixed while retaining powered-flipper behavior.
- Exact 128-bit score and decimal carries retained; large awards now fail atomically at overflow.

## Final integrated measurements

| RAM | Frames | Worst cycles | Mean cycles | Over133333 | Music errors |
| --- | ---: | ---: | ---: | ---: | ---: |
| 512 KB | 12000 | 192560 | 58485 | 36 | 0 |
| 2048 KB | 12000 | 192631 | 58484 | 36 | 0 |

Both strict budget tests FAIL as expected and retain their nonzero exit status.
Worst complete frame is about 24.1 ms at8 MHz. The workload includes music restarts
at 6101/6501/6503 (including priming cancellation) and 19 deliberate source-geometry
placements at 7000..10900. These placements verify costs/events, not player-route
reachability. No sustained60 FPS or new2 MHz claim is made.

## Verification

- Original source/DAT contracts:216 mechanism assertions pass under host ASan/UBSan and native65C02 at512 KB and2 MB.
- 254 route/layer checks,10 stationary-tip checks and powered/passive flipper regression pass on host/native at both RAM sizes.
- Exact score oracle:65536 uint16 awards,128 carry boundaries,255 overflows; additional1920 large-award carry,240 limit and15 latch cases. Real hyperspace boundary test:29host/32native assertions perRAM.
- 40-seed optimized/exhaustive sanitized host soaks agree at0cfd4551 with zero escapes/stalls.115drains; some games reach18000-frame cap;11 guard uses remain.
- Native arithmetic, four exact music-stream comparisons, depth quantizer, pixel compositor, bounds and50 host/native checkpoints pass on both RAM sizes.
- All171550 quantized depth pixels preserved;384 native depth rectangles and14104 dynamic VERA byte checks pass on both RAM sizes.
- 17resident PCM samples match converted source bytes; five new played waveforms correlate above0.94 on both RAM sizes. Staged music restart/cancellation tests pass.
- Final12000-frame runs include measured music restarts/cancellation and 19 deliberate mechanism placements beyond frame7000; zero music-buffer errors in both.
- Interactive emulator checks pass at512 KB/2 MB: table pixels, lamp flashes, main plunger, flippers, launch, F2, M, Escape and audible output.
- Final PRG sections and both distinct overlays independently match ELF extraction. Main BSS9592/977d preserves the1KB stack guard.
- 15 packaging checks pass; bank allocation fits512 KB, with bank63 free. AcceptedOriginalTable0.2/Wireframe 0.2 and vendor source unchanged.

Evidence is retained in evidence/milestone-0.3 and evidence/audio-milestone.
The final UI reports include PRG/RUL/PHY SHA256 values. Tests exposed and corrected
an overlapping-VMA linker output bug: named ELF sections must supply the two
separate banked sidecars. The new independent output test guards this.

## Unfinished

- Frame budget still fails: 36 of 12000 frames exceeded133333 cycles on each RAM configuration; worst about 24.1 ms. Not stable or sustained60 FPS. No new2 MHz performance claim.
- Moving-flipper continuous tip collision and original tapered-face normals remain incomplete;11 contact-guard uses appeared in the40-seed soak.
- Advanced hyperspace jackpot/blocker/extra-ball/reflex rules, missions, rank/bonus messages and broader scoring interactions remain incomplete.
- Advanced hyperspace tiers1/3/4 and gravity-well audio cues are absent. PCM uses one priority channel; music instrument timbre is not note-perfect.
- Spinner full-rotation callbacks and randomized original throws remain unfinished. Lamps share a blink phase rather than individual DAT phases.
- Large visual changes may take2–3 frames; dynamic bumper depth maps are absent. Selected layer-route tests are not exhaustive topology proof.
- Windows BAT quoting/flags were statically tested on Linux; actual Windows execution was not available.

## Run and resume

Extract the whole flat development ZIP; keep x16emu.exe/rom.bin in its parent.
RUN-WINDOWS.bat uses the game directory and -c02 -mhz 8 -ram 512 -scale 2.
Keep CADET.PRG, CADET.RUL, CADET.PHY and every BIN together.
Controls: Space hold/release plunger; Z/leftShift left flipper; slash/rightShift
right flipper; F2 new game; M music; Escape exit.
See RESUME.md for build, bank allocation, test commands, source inputs and next work.
SOURCE.zip contains committed code, recovered references and matching runtime data.
