# Integer preview validation — 2026-11-16

Checked using r49 plus its matching ROM, at 512 KB and 2048 KB RAM.

- Native multiply: all 65536 byte-operand pairs checked against repeated
  addition, plus 4096 wide products against a shift/add oracle. Carry extremes,
  signed fixed multiply/divide and integer square-root endpoints also pass.
- World, integrated plunger/flipper and 96 flipper records are bit-identical
  between the integer host implementation and native 65C02 at both RAM sizes.
- The 96 flipper records preserve all 40 contact scenarios. Compared with the
  retained float reference, maximum angle error is 0.000639 radians; maximum
  tip-coordinate error is 0.003493 world units, below a tenth of a display pixel.
  Maximum normal-component error is 0.001803; maximum speed error is 0.053776.
  Fixed-point bounds are separate from the unchanged float test tolerances.
- All 40 full-charge release timings clear the chute at the 120 Hz cadence.
- Normal-ROM instrumented boots pass charge, launch/chute, both flippers,
  short command taps, pause/resume and clean return to BASIC on both RAM sizes.
- Actual distribution CMDRX.PRG passes real SDL keyboard input at stock 8 MHz
  on both RAM sizes. Captures verify status changes, full charge and both
  moving flipper sprites. Both builds contain no soft-float arithmetic helpers.
- The retained floating-point suite still passes all 736 tests. Its original
  files and vendor sources have not changed.

The instrumented -Oz preview's 760-frame sequence measured **96297 cycles
average (12.04 ms)** and **389733 cycles maximum (48.72 ms)** at 8 MHz; 88 frames
exceeded 133333 cycles. These figures include feeding, charging, flight,
flippers and pause; they are not an active-play-only average. The distribution
uses -Os and was exercised separately through actual SDL keyboard input.
The strict 60 Hz gameplay gate remains FAIL; this is an improved preview,
not a performance-approved finished game. No accelerated CPU is required by
the included launcher, and no 40 MHz launcher is included.

The normal PRG is 37057 bytes. UI.BIN is 6985 bytes, WORLD.BIN 193640 bytes,
and FLIP.BIN 131072 bytes. The latter uses banks 8..23; bank 1 is presentation
and banks 32..55 hold the world. Keep all files from the same package together.

The source checkpoint retains detailed native traces, differential error
measurements, build hashes, real keyboard logs and representative captures.
