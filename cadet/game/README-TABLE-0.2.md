# CmdrX Cadet — Original Table Test 0.2

A playable integration checkpoint for stock Commander X16 65C02. This follows
the accepted Wireframe 0.2 and Fidelity Lab 0.1. It is not the completed Space
Cadet port. The previous builds remain preserved.

Extract the ZIP into its own game folder, with x16emu.exe and matching rom.bin
in the parent folder. Double-click RUN-WINDOWS.bat. It keeps the game folder as
the current directory and starts CADET.PRG at 8 MHz, 512 KB, scale 2. You can also
drag x16emu.exe onto the BAT. No enclosing folder is added inside the ZIP.

Controls:
- Space: hold to pull the plunger; release to launch.
- Z or left Shift: left flipper.
- / or right Shift: right flipper.
- F2: new three-ball game.
- M: toggle theme music.
- Escape: exit to BASIC.

What is integrated:
- 1,217 original collision edges, exact circle primitives, directed line faces,
  three collision masks, and original ramp transfer metadata.
- Integer swept ball movement, original-style rebound calculation, moving
  tapered flipper capsules, plunger, bumpers, captures/returns and drain/new ball.
- Original-resolution 365x470 table and backbox, original animated flipper,
  plunger and seven ball bitmaps, original numeric score/player/ball glyphs.
- 128-bit score storage and 40 decimal digits internally. The original nine-digit
  panel displays normal scores; larger values produce an explicit notice and
  exact decimal emulator log, rather than silently truncating the stored score.
- Twelve resident original PCM effects mapped to component references, plus the
  full native YM2151/VERA PSG theme. No disk reads occur during normal gameplay.
- All graphics fit in VERA; only sprite attributes change during animation.
  Geometry occupies RAM banks 1–18, PCM 19–30, music 32–58. Runs with 512 KB.

Known limits of this checkpoint:
- Mission progression, bonuses, extra balls, high-score entry, full lamp/target/
  gate state machines, tilt and original UI messages are unfinished. Current
  awards cover initial bumpers, targets, spinners and two lower rebounders.
- Collision primitives and ramp masks are original data, but the fixed-point
  solver is an adaptation. Flipper response and capture field forces still need
  controlled replay comparison against the original executable.
- Bumpers and lamps do not yet visually animate. Ball occlusion beneath artwork
  is unfinished: crossing above an opaque rail on screen does not by itself
  mean collision masks crossed. Track and report the location if encountered.
- Plunger feed begins at rest; original feed animation, launch randomness and
  several timing details remain to be matched.
- The small status text is provisional. Original numeric glyphs are used.
- One PCM effect voice uses priority arbitration, so overlapping effects are not
  an exact Windows audio mix. Twelve of the 60 available WAVs are resident.
  Six DAT references have no matching WAV in the supplied install/installer.
  The missing plunger pull sound is not replaced with an invented sound.
- Music event timing and note allocation are retained; FM timbres/percussion are
  adaptations. This is not a claim of an identical original soundfont.

Read VALIDATION.md for measured performance and the scope of testing. 8 MHz is
the recommended setting. The 2 MHz run is a stress baseline and has visible
timing hitches; it is not a 60 FPS target already achieved.

Source and recovery:
- SOURCE.zip contains source, original recovered table data, generated headers,
  converted runtime assets, tests and attribution. It does not include the
  original game executable or an X16 ROM.
- VM: /opt/cmdrx-cadet-fidelity, branch spacecadet-fidelity.
- Build existing generated assets: sh cadet/game/build.sh
- Regenerate: sh cadet/game/build.sh assets
  Regeneration additionally needs the authorized original files and DAT inventory
  at the paths documented in cadet/RESUME.md, plus Python numpy/scipy/Pillow.
- Compiler: LLVM-MOS SDK 23.4.0, mos-cx16-clang; target remains 65C02.
- Original reconstruction: Andrey Muzychenko / k4zmu2a, SpaceCadetPinball,
  upstream cb9b7b886244a27773f66b0b19fdc2998392565e, MIT code license included.
- Original game/art/audio: Cinematronics and their respective rights holders.
  X16 adaptation and validation: Codex, working with Brett Estrade.
