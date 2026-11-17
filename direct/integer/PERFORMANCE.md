# CmdrX Cadet performance preview 2 — 2026-11-16

The standard 65C02 build remains the recommended preview. Four cached static
edge records now retain neighboring collision candidates between substeps.
Q12-to-Q8.8 bound conversion and positive subdivision counts use raw integer
arithmetic, avoiding general fixed-point arithmetic. Resting/full-travel
flipper sprites skip divisions whose exact answers are known.

All recorded world, mechanisms and flipper host traces remain byte-for-byte
identical to the previous integer preview. Both CPU builds match those traces
in native emulation at 512 KB and 2048 KB; no physics coefficients, timestep,
precision, candidate order or collision subdivision limits were changed.

## Controlled timing comparison

The existing normal-ROM instrumented -Oz test runs the same 760 mixed-state
frames, including feeding, charging, launch, flight, flippers and pause.
Both RAM sizes give the same timing results. The normal distribution uses -Os
and is tested separately with actual SDL key input; these diagnostic figures
are not a cycle profile of the exact -Os distribution binary and are not an
active-play-only average.

| Build at 8 MHz | Average cycles | Maximum cycles | Maximum ms | Over 133333 cycles |
| --- | ---: | ---: | ---: | ---: |
| Previous integer preview | 96297 | 389733 | 48.72 | 88 / 760 |
| Optimized 65C02 | 78764 | 313156 | 39.14 | 44 / 760 |
| Optimized + native 65816 multiply | 78636 | 310684 | 38.84 | 44 / 760 |

The standard build reduces the observed maximum by 19.65% and average by
18.21%. The native multiplier adds only 0.79% maximum / 0.16% average reduction
relative to the optimized 65C02 build. The strict 60 Hz budget still FAILS.
This is an unfinished mechanics preview, not a completed gameplay release.

## What the 65816 experiment does

Our installed LLVM-MOS SDK 23.4.0 compiler accepts -mcpu=mosw65816, but the
included add16/add32 compiler probe still produces byte-by-byte operations.
Simply selecting -c816 does not make that C++ code use 16-bit registers.

cpu816/fastmul.s is a real native-mode 16-by-16-to-32-bit quarter-square
multiplier: it enters native mode, uses 16-bit accumulator/index arithmetic,
and returns to the 8-bit emulation-mode C++ ABI. It leaves IRQ enabled as
supplied by its caller and relies on the R47+ ROM native interrupt trampoline.
Both builds use integer-only arithmetic. The rest of the C++ core remains
8-bit generated code. This is NOT a measurement of a fully native 16-bit port.
The CPU has no hardware multiplication/division, and these routines still
perform software arithmetic and access the same banked model.

The experiment passed all 65536 byte products, 4096 wide products, carry and
signed arithmetic checks; world/mechanism/flipper trace checks; normal-ROM
charge/chute/short-pause/flipper/release/exit checks; and actual SDL controls
and screenshot checks at both 512 KB and 2048 KB. Tested with emulator/ROM r49,
not on physical hardware or a Windows host.

The original float/vendor sources are unchanged. Original float validation
remains in the prior checkpoint; new changes affect only integer adaptation.
Forty full-charge launch hold timings still clear the chute.

## Reproduce

After the standard build and validation in README.md:

```sh
sh direct/integer/cpu816/build.sh
python3 direct/integer/cpu816/verify.py --sdl
python3 direct/build/integer/cpu816/frame_budget.py  # expected FAIL
```

Do not use the experimental PRG on a 65C02. Its launcher explicitly selects
-c816. Keep its UI.BIN paired with its own PRG; the shared asset contents are
otherwise identical. Keep the stock CPU build available for hardware users.

Further native work would need to encompass larger collision/division kernels
so the wider registers benefit more than multiplication alone. The current
measurements support continuing work on the standard collision path before
making the 65816 a requirement. No 60 Hz claim is made for either preview.

Primary references:
- https://github.com/X16Community/x16-emulator/blob/master/README.md (-c816)
- https://github.com/X16Community/x16-rom/releases (R47 native IRQ support)
- https://github.com/X16Community/x16-docs/blob/master/X16%20Reference%20-%2005%20-%20KERNAL.md (native ABI)
- https://github.com/llvm-mos/llvm-mos/issues/32 (compiler native-mode work)
