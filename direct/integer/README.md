# CmdrX Cadet — collision and audio preview 3, 2026-11-16

The direct engine adaptation uses integer-only physics and projection. This
preview repairs bumper contacts, retains brief flipper taps, adds the original
ramp collision layers, and plays seven original sound effects through VERA PCM.

## Run

Extract the complete package into a new folder beside x16emu.exe and its
matching r49 ROM. Use RUN-WINDOWS.bat for the 65C02, or
RUN-65816-WINDOWS.bat for the experimental native multiplier. Both use 8 MHz,
512 KB RAM and no warp mode. Keep each variant's PRG and all nine BIN files
together. WORLD.BIN has a new layout and is incompatible with older builds.
The two UI.BIN files are paired with their respective PRGs.

N feeds a ball. Wait for it to arrive, hold Space until the cyan charge bar
fills, then release. Left/Right Shift or Z and / operate the flippers.
S toggles sound; P pauses; Esc returns to BASIC. N starts again after a drain.

This remains a mechanics preview: the strict 60 Hz frame budget still fails.
Targets, gates, sinks, spinner behavior, missions, scoring/saves, music and
proper ramp/tunnel visual occlusion remain unfinished. The ramp layer adapter
is tested, but that does not establish full original-table gameplay parity.
No physical X16 or Windows-host testing has been performed.

## Implementation

Positions have 12 fractional bits. Runtime multiply/divide/square root and
projection use integer operations; host asset conversion may use floating point.
Both simulation entry points use two 120 Hz steps per display frame, preserving
the original plunger release window. Host/native trace comparisons are separate
from the unchanged floating-point reference tolerances.

Static circles cannot report contacts farther behind the ball than the ray's
existing backward tolerance. This prevents overlapping wall-corner circles from
undoing bumper rebounds. Remaining travel is consumed once per substep.
All seven bumpers have their original masks, boost and 100 ms flash cooldown.
Original ramp records switch collision masks and supply height/field planes.
Short flipper key presses latch until consumed, alongside the held-key state.

Bank 1 contains presentation code; banks 8..23 hold precomputed flipper geometry;
banks 32..58 hold the layered world. Original signed 8-bit mono effects occupy
banks 24..31 and 2. IRQ refill uses no compiler zero-page registers and restores
the previous bank; exit restores the original IRQ vector. SFX are priority-based
single-voice playback, not the original multi-channel mixer. Both CPU variants
fit 512 KB banked RAM. The optional 65816 build replaces only multiplication
with native 16-bit assembly; it is not a full native-mode C++ port.

Both normal and instrumented programs use -Oz. Four cached edge records and a
separate physics function leave room for the extra mechanics/audio. Recorded
diagnostic timing is not an exact cycle profile of the normal distribution.

## Build and test

Requires LLVM-MOS SDK 23.4.0, 64tass, g++, Python/Pillow/NumPy/SciPy, Perl,
X16 emulator/ROM r49, xvfb-run, xdotool and ImageMagick. Paths default to the VM;
MOS_BIN overrides the SDK location. From SOURCE.zip's source directory:

```sh
sh direct/build.sh
sh direct/integer/build.sh
sh direct/integer/build-preview.sh
sh direct/integer/build-contact-tests.sh
sh direct/integer/cpu816/build.sh
python3 direct/integer/verify.py
python3 direct/integer/preview_native.py
xvfb-run -a python3 direct/integer/preview_boot.py 512
xvfb-run -a python3 direct/integer/preview_boot.py 2048
python3 direct/integer/preview_screens.py
python3 direct/integer/cpu816/verify.py --sdl
python3 direct/integer/verify_audio.py
python3 direct/integer/frame_budget.py  # strict gate; expected FAIL
```

The checked-in layers.json and assets/SFX.BIN make the new runtime assets
reproducible without rerunning the original Windows program. export_layers.py
creates a disposable instrumented copy of the recovered engine if the original
game assets are available. Edit direct/integer, not generated build/integer/src.
Original method files and vendor remain unchanged. The future score requirement
remains unsigned 128-bit; no score implementation has been narrowed.

Original Space Cadet game/artwork/audio: Cinematronics, Maxis, Microsoft, from
the user's supplied assets, retaining their original ownership.
Recovered engine: Andrey Muzychenko / k4zmu2a and contributors,
https://github.com/k4zmu2a/SpaceCadetPinball at
cb9b7b886244a27773f66b0b19fdc2998392565e; MIT license included.
X16 platform/toolchain: Commander X16 community, LLVM-MOS and 64tass.
