# Resume CmdrX Cadet original-table integration

Author: Codex, working with Brett Estrade. Use the VM through DC.
Active worktree /opt/cmdrx-cadet-fidelity, branch spacecadet-fidelity; no remote.
Read cadet/AGENTS.md, cadet/game/README.md and cadet/game/VALIDATION.md first.
Previous lab handoff is preserved in RESUME-LAB-0.1.md.

Current playable checkpoint: cadet/play-build/CADET.PRG, Original Table Test 0.2.
Build: sh cadet/game/build.sh. Regenerate assets: sh cadet/game/build.sh assets.
Do not alter /opt/cmdrx-cadet-direct or accepted wireframe-v0.2.
The new engine is C with exact integer arithmetic helpers in small 65C02 assembly.
It uses the original recovered directed geometry and ramp layers, not the earlier
practice table. Native playback/rendering/keyboard integration is now present.

Read the explicit limitations before claiming fidelity. Original complete rule
machines, gate/lamp/target lifecycle, true flipper sweep equivalence, reference
shot replays and ball occlusion are unfinished. Existing host exhaustive search
agreement validates the spatial optimization; it does NOT prove the adaptation
matches every response of the original executable.

Next work:
1. Controlled original-vs-port shot fixtures, especially upper launch chute,
   left ramp/tunnel, underpass, weak launch returns, and flipper contact angles.
2. Port original component/rule state machines together with their lamps/sounds:
   rollovers, target bank reset, gate opening, skill shot, bonus and ball saving.
3. Depth-aware ball occlusion and original animated bumper/target/lamp states.
4. Original message font/UI, high-score controls, and audio timbre/overlap fidelity.
5. Further 2 MHz work after each behavior improvement; 8 MHz remains recommended.
Do not loosen 133333 cycles. Measure from the audio IRQ start through completed
rendering, not just the main-loop body. Native testbench mode disables video IRQs;
use normal dummy-video emulation for the integrated IRQ-driven tests.

Storage: geometry banks 1..18, twelve PCM effects 19..30, music 32..58. Bank 31
and banks 59..63 remain available within 512 KB. All current animation frames
are already resident in VERA; updating poses writes sprite attributes only.
Music streams are compacted by eliminating redundant register writes. Preserve
YM key/control side effects and the 126/125 video-to-music clock compensation.

The original source/assets, capture and toolchain locations remain as recorded
in RESUME-LAB-0.1.md. The Windows package is flat, uses the parent x16emu.exe and
rom.bin, -c02 -mhz 8 -ram 512 -scale 2, and keeps the game directory current.
