# Resume CmdrX Cadet — 0.3 development checkpoint

Author: Codex, working with Brett Estrade. Date: 2026-11-18.
Use the VM through Desktop Commander. Device 62fb2876-6dc0-4e77-abff-35f1c9d17cb4.
Worktree /opt/cmdrx-cadet-fidelity, branch spacecadet-fidelity; no remote.
Read AGENTS.md, cadet/AGENTS.md and cadet/STATUS-0.3-WIP.md before editing.

The latest accepted runnable release is Original Table 0.2, tag table-test-v0.2
at c8312ad. Its assets are preserved at /opt/cmdrx-cadet-table02-assets.
The accepted Wireframe 0.2 remains untouched at /opt/cmdrx-cadet-direct.
CURRENT cadet/play-build/CADET.PRG IS DEVELOPMENT CODE, NOT THE ACCEPTED 0.2.
Do not publish it as passing the 133333-cycle gate.

This checkpoint adds original depth-map ball masking, Euclidean ball sizing,
banked UI metadata, lossless music compression/read-ahead, and exact arithmetic
and collision filtering optimizations. Native functional checks pass, but the
integrated frame-budget test still fails on a small number of frames.
Final results are in cadet/evidence/table-0.3 and STATUS-0.3-WIP.md.
The original target-bank, rollover, gate, skill-shot and mission rules have been
investigated but are NOT integrated into this checkpoint.

Build: sh cadet/game/build.sh
Regenerate assets: sh cadet/game/build.sh assets
Runtime is integer-only 65C02. Keep exact 128-bit scoring. No 65816 requirement.
Native tests: python3 cadet/game/native_check.py 512 (or 2048);
python3 cadet/game/test_depth.py 512 (or 2048);
python3 cadet/game/test_native.py 512 (or 2048);
xvfb-run -a python3 cadet/game/test_ui.py.
Host soak: compile engine.c + soak.c with -Icadet/play-build and run 40.
Repeat with -DCADET_BRUTE; both must match state hash 91cbf84c.
test_score_host.c exhaustively checks every uint16 award and full-width carries.

RAM layout within 512 KB:
- Geometry uses banks 1..9 and 12..16. GEOM files still load unused padding and
  old bounds into 10/11/17/18; these are overwritten after game_load.
- UI bank 11: sprite descriptors A000, projection A800, squared depth thresholds
  B000, 470 three-byte depth-row descriptors B400.
- Original depth bytes (16-bit original >>8): banks 10,17,18,45..63, 22 rows/bank.
- Twelve resident PCM effects: banks 19..30.
- LZSS dictionary and read-ahead: bank 31 A000..AFFF. B000..BFFF is available.
- Compressed music: banks 32..44 (102730 bytes).
Do not overlap these. pack_model currently permits larger spatial lists; before
adding geometry, tighten its size assertion to the actual six-bank allocation.

Music keeps every byte of the compact ZSM stream. LZSS uses 12-bit backward
distances and lengths 3..18. The producer is music_prefetch (64 bytes maximum,
2048-byte target), called only on frames with time available; its cost is INCLUDED
in the frame measurement. The IRQ consumes buffered bytes. Producer rewind at the
known 214239-byte uncompressed length preserves ring position across song loops.
Changing the theme requires updating that native length and test fixture.
Do not move prefetch outside the measured interval to make the benchmark pass.

The frame interval starts at irq_start and ends after display AND prefetch.
The extra IRQ seen in some long frames is real. Testbench mode disables video
IRQs and is invalid for this integrated benchmark. Keep the existing 133333 bound.
Panel updates can wait for a quieter frame; physics, ball and flippers remain
immediate. There is no deliberate skipping of simulation frames.

Next:
1. Finish performance profiling. Remaining spikes include bumper collision
   clusters and lower-table/flipper contact. Inspect PROFILE_DISPLAY diagnostics
   and CADET_PROFILE before making further arithmetic changes.
2. Run both RAM sizes, native/host trajectory equivalence, direct depth masks,
   exact arithmetic, buffered full-theme loops, and UI/audio after the final fix.
3. Only then integrate original target-bank resets, real rollovers, gates/lamp
   state and bonus/skill-shot logic. Add source-derived event fixtures first.
4. Add dynamic target/bumper/lamp graphics and original message font/UI.

Original source oracle: direct/vendor/SpaceCadetPinball (unchanged).
Original files: /opt/spacecadet-x16-analysis/input/game/PINBALL.DAT;
inventory /opt/spacecadet-x16-analysis/evidence/inventory.json.
Toolchain /opt/llvm-mos-sdk-23.4.0/llvm-mos/bin/mos-cx16-clang.
Emulator /opt/x16emu-r49/x16emu and matching rom.bin.
Windows delivery remains flat, parent-folder x16emu.exe/rom.bin, -scale 2,
-c02 -mhz 8 -ram 512, with the game directory current.

Additional profiling item: music_start currently pre-fills 2048 decoded bytes with interrupts disabled. Startup and an M-key restart can therefore pause for more than one frame; that restart cost is outside the scripted 6000-frame workload. Move that prefill to an interruptible staged path before release. The five reported budget overruns are not the only possible user-triggered timing spikes.
