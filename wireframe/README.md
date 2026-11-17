# CmdrX Cadet — wireframe 0.1

A new wireframe pinball game for Commander X16, with an original, deliberately
simple table and integer-only physics. This is the clean rebuild requested after
the recovered Space Cadet layout produced overlapping collisions. The earlier
direct-port experiments and recovered table remain preserved in SOURCE.zip.

## Run

Use X16 emulator and matching ROM r49, 512 KB RAM or more, at 8 MHz. Extract the
entire ZIP. Put its folder alongside `x16emu.exe` and `rom.bin`, then double-click
`RUN-WINDOWS.bat`. `RUN-65816-WINDOWS.bat` selects the experimental 65816 build
with `-c816`; the default build uses the stock 65C02. Sound is enabled.

From an emulator directory, the equivalent command is:

```text
x16emu -c02 -ram 512 -mhz 8 -fsroot "path/to/65c02" -prg "path/to/65c02/CADET.PRG" -run
```

For the second CPU, change `-c02` to `-c816` and both directory names to `65816`.
Keep the PRG and all six BIN files together. The emulator and ROM are not bundled.

| Key | Action |
| --- | --- |
| N | Start a new three-ball game |
| Hold Space, then release | Charge and release the plunger; a full charge takes about 1.7 seconds |
| Left / right Shift | Left / right flipper |
| Up | Nudge, with a short cooldown |
| P | Pause / resume |
| S | Sound on / off |
| Esc | Stop sound and return to BASIC |

After a drain, the next ball appears automatically; hold and release Space again.
There is no automatic rescue or teleport to hide a stalled physics state.

## Implemented mechanics

- Swept ball collisions with walls, bumpers and targets; integer gravity,
  friction, fractional position and acceleration, and bounded collision iteration.
- Moving and resting flippers, plunger strength, side kickbacks, drains and a
  complete three-ball lifecycle.
- A raised ramp with separate entry, top exit and rollback exit; rollover sensors,
  a spinner, nine drop targets, a standing target, a timed pocket and a kickout well.
- Visible event flashes and target/rollover lamps. Completing one of the three
  drop-target banks opens the gate for ten seconds and enables the central well.
- Seven original PCM effects: flipper up/down, bumper, launch, pullback, drain and
  wall contact. Priority-based playback, mute, pause and clean shutdown.
- Unsigned 128-bit score with all decimal digits available on screen; overflow is
  explicitly reported rather than wrapping.

This is a new basic pinball ruleset and layout. It is not the Space Cadet table.
Original Space Cadet
missions, ranks, multiball rules, tilt penalties, high-score saving and music are
not implemented. The collision layers and core mechanisms are present; this is
not a claim of full original-game parity. Artwork can replace the wireframe later.

## Source and build

`SOURCE.zip` includes the complete project checkpoint, recovered table data,
original reference source, assets needed for this build, and validation scripts.
The active implementation is `wireframe/`; its entry point is `main.cpp`.

Build dependencies: LLVM-MOS SDK 23.4.0, host g++, Python 3 with Pillow, and the
DejaVu Sans Mono fonts. Validation additionally uses numpy/scipy, emulator r49,
Perl, Xvfb, xdotool and ImageMagick. Run from the source root:

```sh
sh wireframe/build.sh
sh wireframe/test_native.sh
python3 wireframe/verify_emu.py
xvfb-run -a python3 wireframe/keyboard_test.py c02 512
```

`layout.py` generates the original practice table; `table.json` is the geometry
input. `recovered-table.json` preserves the earlier Space Cadet geometry.
Re-exporting the recovered reference requires the separate original game-data
workspace; ordinary builds do not.
See `VALIDATION.md` for exactly what was tested and remaining limits.

## Attribution

Space Cadet's original game, table and sound assets are the work of Cinematronics,
Maxis and Microsoft. The recovered C++ reference is k4zmu2a's SpaceCadetPinball
project, https://github.com/k4zmu2a/SpaceCadetPinball, whose license and attribution
are preserved in the source archive and `REFERENCE-LICENSE.txt`. Generated
wireframe art and the new X16 engine are distinct from those original assets.
Wireframe art uses DejaVu Sans Mono; its license is included.
No original Windows executable or X16 ROM is included.
