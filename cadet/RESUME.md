# Resume CmdrX Cadet fidelity work

Author: Codex. User: Brett Estrade. The VM is the working environment; use DC.
This checkpoint is an art/audio audition and initial C modules, NOT completion
of the original-table port. Read README.md, VALIDATION.md and AGENTS.md here.

- Active worktree: /opt/cmdrx-cadet-fidelity, branch spacecadet-fidelity.
- Preserved playable practice game: /opt/cmdrx-cadet-direct, wireframe-rebuild;
  tag wireframe-v0.2 = 51149308b350ca485d36ec73713c6bbf2cba5e41.
- No configured remote. SOURCE.zip is a recovery copy, not evidence of a push.
- Original recovered C++: direct/vendor/SpaceCadetPinball. Existing adaptations
  from the earlier direct port are present; this fidelity pass leaves them alone.
- Pristine upstream identity: cb9b7b886244a27773f66b0b19fdc2998392565e.
- Original installation: /opt/spacecadet-x16-analysis/input/game.
- Original installer: /opt/spacecadet-x16-analysis/input/space-cadet-upload.exe.
- DAT inventory: /opt/spacecadet-x16-analysis/evidence/inventory.json.
- DAT analyzer: /opt/spacecadet-x16-analysis/analyze_dat.pl.
- Reference executable/exporter: /opt/cmdrx-cadet-direct/direct/build/reference/bin.
- OBS attachment: 2026-11-17 22-59-31.mp4, 83.816667 s, 1920x1080/60.
  Compressed audio derivative, contact sheet and provenance are in cadet/capture.
- Toolchain: LLVM-MOS 23.4.0, cc65 comparison, X16 emulator r49 stock 65C02.
- Build: sh cadet/build.sh. Asset conversion: sh cadet/build.sh --assets.
- Runtime: cadet/build/LAB.PRG plus MAP/TILES/PAL/FONT, MUSIC*.BIN, PCM/.

User priorities: recognizable Space Cadet, ultimately near-original pixels and
notes; integer-only, stock 65C02 preferred, best at 8 MHz and aim for usable 2 MHz;
native X16 audio and full VERA use. Preserve the accepted wireframe's responsiveness.
The wireframe allowed impossible routes across boundaries; do not treat its good
feel as original-table topology correctness or overlay original art on its physics.

Next integration work, in order:
1. Generate compact banked collision tables/spatial index from recovered-table.json
   (1227 edges: 802 lines and 425 circles). There are 9 one-way components with
   opposing pass/block faces and 65 ramp edges. Keep collision masks 1/2/4 and
   source-specific entry/exit/event distinctions; do not allow arbitrary transfers.
2. Integrate swept integer ball movement, original circle responses and moving
   flippers. Add original-reference replay fixtures for legal and forbidden routes,
   ramp height/underpass separation, plunger shots and no-stall/no-escape play.
   routes.c is only directed-line/state groundwork, not a full collision solver.
3. Connect original component events to the recovered sound references. Preload
   frequent PCM into banks; the audition's per-effect disk LOAD is not game design.
   Resolve the six DAT-referenced WAVs absent from the actual supplied installer
   by tracing call sites; do not invent their content or silently claim full coverage.
4. Render the actual ball, flipper poses, lights and scores using VERA sprites and
   tile updates. Re-budget the audition's temporary text/font VRAM before animation.
5. Port remaining original rule/mission state machines to C, then measure native
   complete frame costs at 8 MHz and 2 MHz. LLVM-MOS wins the first scoring kernel
   comparison; this does not prove every subsystem or the whole game is fast.
6. Refine palette fitting, FM instruments and percussion. The score preserves all
   starts, but current timbres and some GM expression are explicitly adaptations.

Tests and findings:
- Full music loop on 512/2048 KB; 66,525 YM + 50,952 PSG writes agree with decoder.
- 14,139 note starts, zero active-note stealing, 60 Hz event grid.
- VGA refresh is 59.5238 Hz: music requires 126 ticks per 125 frames. Do not regress
  to one 60 Hz stream tick per video frame (it drifts ~4 s over the theme).
- PCM: signed 8-bit mono, rate 29 = 11062.6220703125 Hz. Mute after completion;
  stopping rate alone holds the last sample. All 60 recorded sequences verified.
- Emulator cycle counter MUST be read low-byte first to latch the other bytes.
  cc65 volatile uint32 reads high-first, which produced a bogus early benchmark;
  current probes explicitly sequence byte reads.
- C route probe: 3766 assertions host + native, using 538 actual directed edges.
- Integer score probe: six cases including carry beyond 32 bits and 128-bit limit.
- Keyboard integration compares exact packed table pixels before/during audio.
- OBS matching remains tentative: 41 >=0.5 candidates, one >=0.7; DAT is stronger
  evidence for effect mapping than this mixed AAC recording.

Do not report new background progress unless work was actually executed. Keep this
file and validation current at each new runnable checkpoint so lost chats are recoverable.
