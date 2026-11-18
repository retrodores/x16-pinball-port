# Current checkpoint: Original Table Test 0.2

Playable integration is now in cadet/game. Read cadet/game/README.md and
cadet/game/VALIDATION.md; current follow-up order is in RESUME.md.

The original pre-integration plan follows for context.

# Next playable Space Cadet milestone

Brett's accepted feedback (2026-11-18): the artwork is visually very close; audio
is useful but needs refinement. Preserve faithful score/control presentation as
well as table art. Windows distribution preference: no enclosing ZIP directory,
launcher and LAB.PRG in the extracted current directory; x16emu.exe and matching
rom.bin one level above; -scale 2 in both launcher paths. Retain drag/drop override.

The accepted wireframe establishes responsive integer simulation and useful play
testing. The original source/data establish the table geometry, mechanical rules,
scoring and event behavior. The OBS capture checks observable appearance and feel.
The wireframe renderer will become a diagnostic view of the same simulation used
by the final artwork renderer. Avoid two independently maintained physics engines.

1. Original geometry and mechanics: compact indexed line/circle tables; directed
   rails and gates; ramp planes, layer masks and specified exits; swept ball and
   flipper collisions; source-derived plunger, kickout, bumper, drain behavior.
   Reuse proven fixed-step scheduling and low-cost rendering/input techniques.
2. Reference comparison: instrument controlled original-engine shots and replay
   matching starting state/input in the fixed-point build. Compare short trajectories
   with explicit tolerances, collision events, masks/heights and score changes.
   Test forbidden crossings, high-speed contacts, flipper tips, held flippers,
   ramp underpasses, stuck balls and complete ball lifecycles. Long chaotic play
   should not be expected to follow identical pixels after fixed-point rounding.
3. Integrate VERA rendering and sounds early: actual ball/flipper/plunger poses,
   occlusion over/under ramps, lights and event-matched PCM effects. Cache common
   samples to avoid disk LOAD during play. Keep the diagnostic overlay switchable.
4. Faithful backbox and controls: use original score digit bitmaps, message fonts,
   panel coordinates, colors, player/ball indicators, mission prompts, flashing,
   bonus/game-over transitions and high-score presentation. Preserve the original
   look of controls/settings where practical on X16; record any required input
   adaptation. The asset audition's temporary instructions are not final game UI.
5. Original rules and audio refinement: migrate remaining mission/bonus state,
   then tune instrument patches, drum envelopes, effect balance and priorities
   against isolated sources and captured reference events. Preserve note/timing
   evidence separately from timbre similarity and resolve absent WAV references.
6. Measure complete gameplay at 8 MHz and 2 MHz on stock 65C02; keep 8 MHz the
   primary quality target and quantify any 2 MHz tradeoff. Test both 512 KB and
   expanded RAM and retain recoverable source and findings at each checkpoint.

Next runnable acceptance target: original table with launch, responsive flippers,
bumpers, representative ramp/gate routes, drain/new ball, actual score/ball display
and event sounds plus music. No requirement to finish all missions before exposing
this useful gameplay milestone, and no claim of fidelity based only on unit tests.

Evidence: current supplied source/assets and OBS recording are sufficient to begin.
Optional later captures with clean game audio and visible whole backbox: new game,
short/full plunger, ramp entries/exits, bonus/drain/next ball, game over/high scores,
and original control/settings panels. An input overlay or stated key presses would
make movement comparisons easier. Missing/uncertain behavior should be requested
specifically when identified, rather than asking for another long generic video.

The VM already has the reference executable, LLVM-MOS, cc65, stock x16emu, Xvfb,
image processing and audio/capture tools. Routine project-local setup is covered
by existing authorization; there is no additional permission or paid software
requirement blocking the next milestone.
