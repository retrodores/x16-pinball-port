# CmdrX Cadet — integer performance preview 2, 2026-11-16

This build replaces the preview's runtime floating-point arithmetic with
fixed-point integers. Collision detection, gravity, rebounds, moving flippers,
plunger timing and ball projection all use integer operations. Original method
bodies and floating-point probes remain available as the comparison reference.

## Run on Windows

Extract into a **new folder** beside x16emu.exe and its matching r49 ROM.
Keep CMDRX.PRG and all seven BIN files together, including the new FLIP.BIN.
Double-click RUN-WINDOWS.bat. It explicitly runs the standard **8 MHz** CPU;
no overclock or warp mode is enabled.

Press **N** for a ball. Wait for it to arrive, hold **Space** until the cyan bar
fills, and release. Use **Left/Right Shift** or **Z and /** for flippers,
**P** to pause/resume, and **Esc** to return to BASIC. Press N after a drain.

This is still an unfinished mechanics preview. Ramps/layers, other table
mechanisms, missions, scoring/saves and original audio are not integrated.
It is faster than the previous float build, but the strict 60 Hz frame budget
still fails during heavy contacts. See VALIDATION.md for measured limits.
Use this package's WORLD.BIN and FLIP.BIN; the float preview's WORLD.BIN is
not compatible with this program.

## Integer implementation

- Positions and scalar values retain 12 fractional bits (1/4096 world unit).
  Multiplication, division and square root use 16/32-bit integer operations.
  Quarter-square lookup tables accelerate the 65C02's 16-by-16 multiplication.
- Physics still uses two 120 Hz updates per displayed frame. Frame intervals
  use exact integer division by 120, 60 or 100, avoiding Q12 timestep rounding.
- Flipper control points are exported at 512 orientations per side from the
  original initialized geometry. FLIP.BIN occupies banks 8..23. This avoids
  repeatedly rotating and normalizing the same geometry on the 65C02.
- World data remains in banks 32..55; display code remains in bank 1. The
  entire configuration fits 512 KB of banked RAM.
- Asset conversion and reference tests may use floating point on the build
  host. The delivered PRG links **no runtime floating-point helpers**.

The adapted files are generated under direct/build/integer/src. Edit the
adapter/generator in direct/integer, not generated files or original methods.
The bounded fixed-point arithmetic is for this table's mechanical quantities;
it is not a general-purpose arbitrary-range numeric library. No scoring has
been narrowed: the final score requirement remains unsigned 128-bit.

## Build and verify from SOURCE.zip

Requires LLVM-MOS SDK 23.4.0, 64tass, g++, Python/Pillow, Perl and X16 r49.
Paths default to the development VM; MOS_BIN can select another SDK directory.

```sh
sh direct/build.sh
sh direct/integer/build.sh
sh direct/integer/build-preview.sh
python3 direct/integer/verify.py
python3 direct/integer/preview_native.py
xvfb-run -a python3 direct/integer/preview_boot.py 512
xvfb-run -a python3 direct/integer/preview_boot.py 2048
python3 direct/integer/preview_screens.py
prove -v direct/t/native.t
```

The normal PRG uses -Os with a compact main loop. The instrumented behavioral
probe uses -Oz to fit its extra diagnostics. Actual SDL keyboard tests run the
normal distribution PRG. No physical X16 or Windows emulator test was performed.

Original Space Cadet game/artwork: Cinematronics, Maxis, Microsoft, from the
user's supplied assets. These assets retain their original ownership.
Recovered engine: Andrey Muzychenko / k4zmu2a and contributors,
https://github.com/k4zmu2a/SpaceCadetPinball at
cb9b7b886244a27773f66b0b19fdc2998392565e; MIT license included.
X16 platform/toolchain: Commander X16 community, LLVM-MOS and 64tass.

## Performance preview 2 and the 65816 experiment

See PERFORMANCE.md for measured improvements and unchanged trace validation.
The standard build now caches four static edges and simplifies exact bounds
and step arithmetic. The optional cpu816/build.sh and cpu816/verify.py --sdl
build/test a native 16-bit multiplier while retaining 8-bit C++ elsewhere.
Use -c816 and that build's own UI.BIN for the experimental version.
Both variants still exceed the strict 60 Hz frame budget on heavy contacts.
