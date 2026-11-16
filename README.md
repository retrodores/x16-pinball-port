# Active branch: direct engine port

The user selected a direct C++ port of the recovered original engine. See
[direct/README.md](direct/README.md) for current implementation, tests, measured
performance and unfinished work. The Prog8 prototype below remains a reference.

# CmdrX Cadet 0.2.0

A playable Commander X16 mechanics prototype based on the supplied Space Cadet
table artwork. This is a native prototype, using the selected 320x240,
256-color layout. Prog8 handles the game loop; small 65C02 routines handle
keyboard state, wide score arithmetic, decimal conversion, and digit drawing.

## Run on Windows

Extract this folder beside your r49 x16emu.exe distribution and matching ROM.
Double-click RUN-WINDOWS.bat, or from Git Bash in the emulator directory:

```sh
./x16emu.exe -run -scale 2 -fsroot ./CmdrX_Cadet_0.2.0 -prg ./CmdrX_Cadet_0.2.0/CMDRX.PRG
```

Keep all seven asset files beside CMDRX.PRG (six .BIN files plus MUSIC.PCM). The Windows installer EXE is not an
X16 program. A ROM is not included in this package.

At scale 2, the emulator displays a 1280x960 image; the 235-pixel table asset
is about 940 screen pixels tall. Use fullscreen if desired; preserve the 4:3
aspect ratio. The internal resolution stays 320x240.

| Key | Action |
| --- | --- |
| Space, held then released | Charge and launch |
| Z or Left Shift | Left flipper, held continuously |
| / or Right Shift | Right flipper, held continuously |
| P | Pause/resume |
| S | Sound effects on/off |
| M | Music on/off |
| L | Music-only listening / return |
| N | Save current best and start a new three-ball game |
| Esc | Save best, restore keyboard handling, return to BASIC |

## Implemented

- A ball, gravity, a launch lane, outer boundaries, seven bumpers, original static walls, two animated
  flippers, draining, three lives, pause and restart.
- Original table artwork and converted ball/flipper/bumper graphics.
- Original WAV effects and the complete original MIDI theme, converted to PCM.
  Music streams from disk so it does not need to fit in banked RAM.
- Unsigned 128-bit scoring, saturation at the maximum, exact decimal display,
  full-width comparison and versioned high-score storage in CMDRX.HI.
- A maximum score of 340282366920938463463374607431768211455.
  Awards and carry chains cannot silently wrap the total.
- Score presentation queues complete values: conversion uses two simulation
  frames and the 39-digit display is drawn in three following frames. Pending
  values remain coherent while further points accumulate.

BEST shows the stored best from startup/new game. The current score is observed
for a new best during play and saved on game over, N, or Esc. Close the program
with Esc to save an unfinished game's best. The CHARGE value beside BALLS shows launch charge (0-64); a 1 beside it indicates pause.

## What this prototype leaves for the next stage

The physics remain a screen-space model. The static wall field is baked from
56 original base-layer wall groups; ball contact normals are smoothed for the
low-resolution grid. Bumper radii and responses remain approximate. Flipper pivots, projected endpoints, artwork and bumper centers
come from the original resources, but the engine does not yet reproduce all
1,229 original collision edges. Ramps, height/occlusion, slingshots, most target rules, missions, rank progression, multiplayer,
and a complete high-score table are not implemented. No physical X16 hardware
test has been performed. The extra artwork does not imply active collisions.

At startup, attract mode automatically plays and cycles lamps. Press N or Space
to play. Idle games return to attract mode after 30 seconds while waiting for a
ball. Demo scores are excluded from saved best scores. L plays the theme without
simulation, and automatically enables music; M can still mute it independently.

The theme uses the original MIDI notes rendered through TimGM6mb instruments.
It is approximately 8 minutes 57 seconds long and loops. Both music and original
WAV effects are converted to mono signed 8-bit PCM at about 8 kHz for stock VERA.
This preserves the original recordings/composition, but is not bit-identical to
Windows MIDI synthesis. Effects and music are mixed into the PCM FIFO.

The current goal is to judge size, controls, motion and flipper response before
spending effort reproducing the entire table.

## Build and test

Development and native emulation were performed on the connected Linux VM:
`/opt/cmdrx-cadet`. The previous study remains at
`/opt/spacecadet-x16-analysis`.

Required: Java 21, Prog8 14.0-BETA3 (e98adeaf), 64tass, Perl/prove with TAP::Parser
and Math::BigInt, plus r49 x16emu and its matching ROM.
Set PROG8C to your compiler launcher, or JAR to its JAR file.
Set X16EMU and X16ROM when they are not installed at the VM paths used by tests.

```sh
./build.sh
prove -v t/native.t
X16_RAM_KB=2048 prove -v t/native.t
```

The suite executes the actual production modules as native 65C02 code:
128-bit boundaries and randomized reference vectors, decimal conversion,
save/load, raw key press/release and alias behavior, VERA asset loads, mechanics,
a deterministic 5000-frame soak, continuous natural launches, eight-frame
plunger animation, attract/listening modes, independent audio controls, sector
streaming, and measured 8 MHz frame budgets.

Tested contact scenarios include both resting and moving flippers plus the
maximum 39-digit score. Test results and actual cycle measurements are under
evidence/. They cover those scenarios, not every possible future table state.
Music sector refills and mixing are included in the active-play budget tests.
Initial loading and high-score saves are outside that budget.

To regenerate artwork, supply your own PINBALL.DAT and an inventory made by the
study's analyze_dat.pl, then run:

```sh
python3 tools/build_assets.py /path/to/PINBALL.DAT --inventory /path/to/inventory.json
```

Pillow, NumPy and SciPy are offline conversion dependencies. The additional
VM scripts tools/build_boundaries.py and tools/build_audio.py use the retained
analysis workspace. Audio rendering uses FluidSynth and TimGM6mb.

Pillow is an offline conversion dependency only. No Python, Perl, or Prog8
compiler is needed to play the PRG on an X16.

## Credits and resources

- Original Space Cadet game/table: Cinematronics, Maxis, Microsoft; game assets
  came from the user's supplied package. Those assets are separate from the new
  code's license; this package does not relicense them.
- Andrey Muzychenko / k4zmu2a:
  https://github.com/k4zmu2a/SpaceCadetPinball
  Reference commit cb9b7b886244a27773f66b0b19fdc2998392565e.
  Its MIT license is retained in REFERENCE-LICENSE.txt.
- Prog8 by Irmen de Jong and contributors; X16 community emulator, ROM and VERA
  documentation; 64tass by Soci.
