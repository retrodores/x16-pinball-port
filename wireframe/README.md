# CmdrX Cadet — wireframe 0.2

A standalone wireframe pinball game for Commander X16, with integer physics,
a new original table, a moving plunger, live score, soft effects and quiet music.
The stock 65C02 is the primary CPU. Playable at 2 MHz; best at 8 MHz.
The experimental 65816 build remains available for compatibility.

## Run

Use X16 emulator and matching ROM r49, with 512 KB RAM or more. Extract the
entire ZIP and place its folder beside x16emu.exe and rom.bin.

- `RUN-WINDOWS.bat`: stock 65C02, recommended 8 MHz.
- `RUN-2MHZ-WINDOWS.bat`: the same PRG at 2 MHz.
- `RUN-65816-WINDOWS.bat`: optional 65816, 8 MHz.

From an emulator directory:

```text
x16emu -c02 -ram 512 -mhz 8 -fsroot "path/to/65c02" -prg "path/to/65c02/CADET.PRG" -run
```

Change `-mhz 8` to `-mhz 2` for the slower CPU setting. Keep CADET.PRG and the
four BIN files together. No emulator, ROM or original Windows executable is bundled.

| Key | Action |
| --- | --- |
| N | New three-ball game |
| Hold Space, then release | Pull the visible spring plunger and launch |
| Left / right Shift | Left / right flipper |
| Up | Nudge, with a short cooldown |
| P | Pause / resume, including music |
| M | Music on / off independently |
| S | All sound on / off |
| Esc | Stop and return to BASIC |

Full plunger charge takes about 1.7 seconds of game time. The S/M lamps above
the charge bar show enabled sound/music in green. The red bottom segment marked
DRAIN is the intended exit. The other boundary segments are joined and closed;
the two lower slopes guide lost balls toward that drain. The next ball appears
automatically after a drain and needs a new Space press/release.

## Play and scoring

- Five pop bumpers: 100 points each. The standing target awards 100.
- Nine retracting targets in three banks: 250 each; bank completion awards 1,000,
  opens the gate for ten seconds and enables the central kickout well.
- Three rollover sensors: 50 points. Spinner: 100. Ramp crossings: 25.
- The side pocket and central well capture briefly, award 500 and return the ball.
- Side kickbacks award 100 and return the ball upward. Sling faces rebound it.
- The raised ramp has distinct entry, top exit and rollback exit paths.

The current score appears directly below SCORE and updates using sprite digits.
All 128 bits are retained and all 39 possible decimal digits fit in four rows.
Overflow is explicit; scores never silently wrap. High scores are not saved yet.

Sound now uses original triangle-wave effects with attack/decay envelopes and
an original, quiet two-voice music loop. The earlier PCM effects remain preserved
in SOURCE.zip as reference assets; this build does not play them.

## Performance and validation

The physics clock remains 60 Hz at both CPU speeds. The renderer can skip an
intermediate drawing and catch up with fixed physics steps when a 2 MHz frame
runs long. It retains elapsed simulation time and polls controls between short
batches. At 8 MHz the intended display rate is 60 FPS. See VALIDATION.md for
measured frame rates, worst display gaps and test coverage; 2 MHz is not a promise
of an uninterrupted 60 FPS display.

The new perimeter is tested with deliberate outward shots and long game runs.
There is no automatic teleport or rescue to conceal a trap. Real X16 hardware
has not been tested in this session.

## Source and recovery

SOURCE.zip contains the project checkpoint, original reference materials,
new engine, generated-table source and test scripts. Read RECOVERY.md to resume
without an older chat. The accepted 0.1 build remains a separate checkpoint.

Build dependencies: LLVM-MOS SDK 23.4.0, g++, Python 3/Pillow and DejaVu Sans Mono.
Validation additionally uses numpy, r49 emulator/ROM, Perl, Xvfb, xdotool and
ImageMagick. Run from the source root:

```sh
sh wireframe/build.sh
sh wireframe/test_native.sh
TEST_CPUS=c02 TEST_MHZ=2 TEST_TAG=-2 python3 wireframe/verify_emu.py
TEST_CPUS=c02 TEST_MHZ=8 TEST_TAG=-8 python3 wireframe/verify_emu.py
xvfb-run -a python3 wireframe/keyboard_test.py c02 512 2
```

This is the original wireframe table, not the Space Cadet layout. Original
missions/ranks, tilt penalties, multiball and persistent high scores remain
future work. The focus is a complete, enjoyable small wireframe game before
further artwork or original-table restoration.

## Attribution

The earlier reference game/table/assets are by Cinematronics, Maxis and Microsoft;
k4zmu2a's SpaceCadetPinball project provided the recovered C++ reference. Its
license and provenance remain in SOURCE.zip and REFERENCE-LICENSE.txt. The new
table, wireframe art, PSG effects and music are separate original work.
The font is DejaVu Sans Mono; FONT-LICENSE.txt preserves its license.
