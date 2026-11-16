# CmdrX Cadet — direct-engine preview, 2026-11-16

This is the runnable **direct C++ engine port**. It is an unfinished mechanics
preview, with original table artwork, a visible ball, original plunger and
flipper methods, and keyboard controls. It is not the earlier Prog8 prototype.

## Windows: run it

1. Extract the ZIP. Keep CMDRX.PRG and all six BIN files together.
2. Place the extracted folder beside your X16 r49 emulator and matching ROM,
   or place x16emu.exe in the extracted folder.
3. Double-click RUN-WINDOWS.bat. Press **N**, wait for the ball, then hold
   **Space** until the cyan charge bar fills. Release Space to launch.

From PowerShell in the emulator directory, you can also run:

```powershell
.\x16emu.exe -run -scale 2 -ram 512 -fsroot .\CmdrX_Cadet_Direct_Preview_20261116 -prg .\CmdrX_Cadet_Direct_Preview_20261116\CMDRX.PRG
```

The launcher uses the standard 8 MHz CPU. This float-heavy engine is currently
slow at that speed; this is not a frame-budget-approved gameplay release.
To inspect motion faster, RUN-FAST-WINDOWS.bat explicitly uses the emulator's
40 MHz benchmark mode. That mode does not represent stock X16 hardware.
Both launchers use the same PRG and unchanged physics parameters.

| Key | Action |
| --- | --- |
| N | Start or reset the single-ball preview |
| Space, held then released | Charge and launch; wait for the ball to arrive first |
| Z or Left Shift | Left flipper |
| / or Right Shift | Right flipper |
| P | Pause or resume |
| Esc | Restore the text screen and return to BASIC |

The start screen is still until N is pressed. After a drain, press N for another
ball. There is no attract autoplay. No original Windows executable or emulator
ROM is included, and no compiler is required to run this package.

## Scope and limits

The preview uses the recovered engine's base-plane collision math and geometry,
moving flipper methods and plunger callbacks. Its two 120 Hz physics updates
per display frame match the recovered desktop engine's default update cadence.
Timers advance in 8/8/9 millisecond steps, preserving the original 25 ms plunger
release window. The display/keyboard code is an X16 platform adaptation.

Still missing: ramps and collision layers, gates and other table mechanisms,
mission rules, full game/ball lifecycle, original audio, scoring and saves.
Visible artwork does not mean every pictured mechanism is active. RNG remains
deterministic. There is no hardware test yet. The final game retains the original
audio, separate audio switches, listening mode and unsigned 128-bit score goals.

## Verification and source

Tested with r49 and its matching ROM at 512 KB and 2048 KB. The package includes
the source checkpoint and validation notes in SOURCE.zip. Recovered method
bodies and vendor sources remain unchanged. The strict gameplay frame limit is
still 133333 cycles at 8 MHz, and the existing performance gate still fails.

Original game and artwork: Cinematronics, Maxis and Microsoft, from the user's
supplied assets; these assets are not relicensed by this project.
Recovered engine: Andrey Muzychenko / k4zmu2a and contributors,
https://github.com/k4zmu2a/SpaceCadetPinball at
cb9b7b886244a27773f66b0b19fdc2998392565e. Its MIT license is included.
X16 platform and toolchain: Commander X16 community, LLVM-MOS and 64tass.
