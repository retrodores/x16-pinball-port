# X16 Pinball Spinner Preview

The left and right flag spinners now turn in response to a passing ball. Their
rotation slows with time, awards points as the flag steps, and advances an
enabled wormhole destination when a flag returns to pose zero. Both spinners
use the existing mechanical PCM effect. The mixer lets its audible part
finish before it plays the same sample again.

The red X flashes during the opening on cold start and F2. Its sprite can
remain visible while the nearby slingshot changes pose.

## Run

Extract the ZIP for your edition and RAM size into its own folder. Place
x16emu.exe and the matching ROM in the parent folder and double-click
RUN-WINDOWS.bat. The executable, three matching overlays, runtime assets and
engine specifications are included.

The 512 KB editions use the compact soundtrack. The 2 MB editions retain the
credited cover soundtrack. The Quick Reset release and its ZIPs remain
available.

## Validation and remaining work

Both editions were exercised from fresh extractions in Linux x16emu r49 at
8 MHz with stock 65C02 and the stated RAM size. Native fixtures exercised
spinner crossings in both directions at different speeds, score and wormhole
updates, actual VERA pose readback, and the PCM source waveform. The Windows
launcher was inspected and has yet to be run on Windows.

Both RAM profiles exceeded 133,333 cycles in the extended gameplay fixture.
See VALIDATION.json for paired measurements against Quick Reset. This is a
preview. Time Warp, the spinner score boost, the skill-shot sequence, broader
lamp coverage, and the center drain blocker remain open.
