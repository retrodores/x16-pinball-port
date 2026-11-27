# 1.0

- Publish Space CmdrX16 2D Pinball in standard 512 KB and 2 MB builds and a
  Christmas 2 MB build.
- Ship the approved blended Christmas table and the 74.2-second melody-first
  *Carol of the Bells* arrangement with synchronized lamps and laser accents.
- Build all three variants from the repository. Keep the reference exemplar
  under [releases/1.0/exemplar](releases/1.0/exemplar/).
- See the [current release handoff](docs/release-status/v1.0/HANDOFF.md) for build inputs and verification.

# 2026-11-25 — Christmas Carol of the Bells 1.0 Beta

- Carry the Christmas theme onto both flippers, the seven bumper caps, the ball and the plunger across all their animation poses.
- Play the full audition ZSM with synthesized stereo drums and the original table effects.
- Drive the Christmas lamp sequences from the native song clock.
- [Playable package, tests and known limits](cadet/game/CHRISTMAS-PREVIEW.md).

# 2026-11-25 — Christmas Winter Village 1.0 Beta

- Add holiday title holly, berry-red and green lettering, snowy firs, a moonlit chalet and candy canes.
- Keep the Encore soundtrack and fit the new scene into existing video memory.
- [Package hashes, timing and emulator checks](cadet/game/CHRISTMAS-PREVIEW.md#winter-village-artwork-and-validation).

# 2026-11-25 — Space CmdrX16 Christmas Encore 1.0 Beta

- Bring two guitar entrances into the first 21 seconds of the full Shchedryk arrangement.
- Follow the chords with center, side and upper lane inserts while keeping gameplay signals visible.
- Verify the full loop on a fresh 2 MB extraction and the return to BASIC at 512 KB.
  [Measurements and package hashes](cadet/game/CHRISTMAS-PREVIEW.md#encore-validation)

# 2026-11-19 — Original Table 0.3.1 development follow-up

- Restore lower slingshot rubber/glow and upper rebounder animations; immediate
  lower tile-map swaps preserve the original six-frame firing interval.
- Mix table, flipper and plunger PCM independently at the original sample rate;
  use a short queue and cumulative underrun diagnostics.
- Send explicit feed/release cues, support independent plunger input, and avoid
  duplicated powered-contact sounds while preserving flipper physics.
- Keep the soundtrack enabled by default with M and a visible music indicator.
- Force bank-changing trampolines resident/noinline; move event dispatch and the
  pure speed limiter into bank62 without changing their numerical behavior.
- Test both RAM sizes and retain the strict failing 133333-cycle budget.
  See cadet/STATUS-0.3.1-DEV.md for costs and remaining gaps.

# 2026-11-18 — Original Table 0.3 development milestone

- Implement source-derived wormhole/kickout capture, destination, release and
  scoring subsets; both kickbacks, hazard gates, yellow lane banks and upgrades.
- Connect 35 original visual components to gameplay events and timers. Retain
  original artwork, eight-pose main plunger, exact 128-bit score and numeric UI.
- Add five original PCM effects and bounded music-start priming; retain explicit
  gaps for advanced hyperspace/gravity cues and multichannel mixing.
- Compress original quantized depth without loss to free banked RAM. Load rules
  and paddle code in bank61, stationary tip sweep in62. Keep stock 65C02/512 KB.
- Preserve powered flipper contact and fix stationary tip grazing; moving-tip
  continuous contact and tapered face normals remain unfinished.
- Preflight large awards across all 128 score bits before chunked addition; preserve
  binary and decimal score atomically on overflow.
- Add source-derived mechanism/topology tests and a 12000-frame workload with
  deliberate captures, kickbacks and music restarts beyond frame 6000.
- Correct overlapping-VMA overlay extraction; verify .RUL/.PHY against named
  ELF sections independently before packaging.
- Deliver a flat development ZIP with source and parent-emulator launchers.
  Strict 133333-cycle timing remains failing; see cadet/STATUS-0.3-WIP.md.
  Neither accepted 0.2 release nor recovered vendor source is changed.

# 2026-11-16 — Collision and audio preview 3

- Reject deeply backward wall-circle contacts that undo bumper rebounds; consume
  each ball substep's remaining distance only once.
- Include all seven bumpers and original ramp masks, transitions and field/height
  planes. Animate bumper hits with the original 100 ms cooldown.
- Latch short flipper taps alongside held input, so slow frames cannot lose them.
- Connect seven original PCM effects with IRQ-driven refill, priority, S mute,
  pause/exit cleanup and bank preservation, including the native 65816 multiplier.
- Use 120 UPS for both integer simulation entry points; retain original methods
  and float/vendor reference. Add targeted contact, short-tap and audio tests.
- Both builds use -Oz and four cached edges to fit main RAM. This is still an
  incomplete preview, with a failing strict stock-clock frame-budget gate.

# 2026-11-16 — Performance preview 2 and 65816 experiment

- Reuse four collision edge records, simplify exact raw-coordinate bounds and
  subdivision arithmetic, and avoid endpoint sprite divisions. Recorded
  integer physics traces are unchanged.
- Reduce mixed-sequence diagnostic worst frame from 389733 to 313156 cycles
  at 8 MHz; over-budget frames fall from 88 to 44 of 760. Gate still fails.
- Add a tested native 65816 multiplier and separate experimental build. It
  achieves 310684 worst-frame cycles; the C++ core still uses 8-bit arithmetic.
- Validate both CPU variants at 512 KB and 2 MB, including real SDL controls.
  See direct/integer/PERFORMANCE.md for scope, timings and reproduction.

# 2026-11-16 — Integer-only runtime preview

- Converted world physics, flippers, plunger and projection to fixed-point
  integers, retaining float methods and pristine vendor sources as reference.
- Added a tested 65C02 quarter-square multiplier and integer square root;
  removed runtime floating-point helpers. Precomputed flipper geometry uses
  512 orientations per side in banks 8..23.
- Added exact rational time multiplication and integer line-plane rejection.
- Tested native/host equality, 96 flipper differential records / 40 contacts,
  40 launch timings and actual 8 MHz SDL controls at 512 KB and 2 MB. Float
  regression suite remains 736/736. Stock-speed launcher only.
- Measured instrumented preview: 12.04 ms average, 48.72 ms maximum across
  760 mixed-state frames. Strict 60 Hz gate still fails during heavy contacts.

# 2026-11-16 — Runnable direct-engine preview

- Added a normal-boot CMDRX.PRG, original table/sprites, charge bar, status and
  N/Space/flipper/P/Esc controls, with a calm start screen.
- Banked the display module in RAM bank 1 to retain main memory for C++ mechanics.
- Matched the recovered engine default of 120 physics updates/second; the former
  60 Hz adapter could miss the original plunger release window. Forty release
  timings now clear the chute. Original extracted method bodies remain unchanged.
- Latched short command taps in the keyboard IRQ so slow frames cannot lose them.
- Added normal-ROM and actual SDL keyboard tests at 512 KB and 2048 KB, Windows
  launchers, and explicit scope/performance notes. Gameplay CPU gate still fails;
  audio, scoring, missions, ramps and other table mechanisms remain unfinished.

# Changelog

## Direct mechanics checkpoint — 2026-11-16

- Port original moving-flipper contact, rebound, motion and swept-collision methods
  to native C++; export original constructor geometry instead of recreating it.
- Port original plunger messages and feed/charge/release callbacks, with bounded
  native timers and a single-ball ownership adapter. Integrate actual charged
  launches and moving flippers into the original-coordinate world probe.
- Reject distant static edges with conservative banked bounds; retain the original
  float formulas and compare every launch frame to the prior direct baseline.
- Fit the combined diagnostic in native main memory using banked lookup data,
  compact parameter initialization and size-oriented compilation.
- Pass 736 functional/differential checks across 512 KiB and 2 MiB. Keep the strict
  133333-cycle gameplay gate failing: 525087 launch-only cycles and 1089833
  combined-mechanics cycles are still over budget.
- Preserve pristine vendor source, the previous direct reference, and the older
  Prog8 prototype. This is a development checkpoint, not a playable release.

## 0.2.0

- Enlarge the silver ball from 5 to 7 pixels and run two solver steps per frame,
  halving the initial prototype's simulation pace.
- Replace the rough trapezoid with a baked contact field from 56 original
  base-layer wall groups. Smooth normals and safe sliding handle curved rails.
- Remove the artificial sideways jump and velocity reset during launch.
- Animate all eight original plunger frames during charge and spring return;
  move the waiting ball with the plunger.
- Replace synthesized placeholder beeps with original WAV recordings.
- Stream the complete PINBALL.MID theme as converted PCM, mixed with effects.
  PINBALL2.MID is a font resource, not a second song.
- Add independent S/M sound/music toggles, attract play with lamp cycling,
  and L music-only listening. N starts a real game.
- Redesign the side panel with cards, color, readable status and audio settings.
- Extend native regressions for walls, continuous launches, plunger animation,
  modes, independent audio, PCM streaming and bank restoration.

## 0.1.0

First native mechanics prototype with ball, flippers, bumpers, plunger, drain,
three lives, pause/restart, exact unsigned 128-bit scores and high-score saves.
