# CmdrX Cadet: direct engine baseline

This branch begins a direct C++ port of k4zmu2a/SpaceCadetPinball to the
Commander X16 through LLVM-MOS. It replaces the direction of the earlier
screen-space Prog8 prototype. It is a diagnostic baseline, not a new playable
release or a complete port.

## What runs natively

- Original line intersection, circle intersection, normalization and rebound
  method bodies, extracted verbatim from the pinned recovered source.
- A four-second launch integration probe in the original world coordinates,
  with the original ball radius, gravity, damping and base-plane collision geometry.
- Banked storage for 653 physical edges (181888 bytes including the broad-phase grid).
- Differential floating-point cases against the same source compiled for the VM.
- Independent r49 runs at 512 KB and 2048 KB.

The ball clears the original chute and travels around the top into the table.
The test checks actual table coordinates, rather than the old premature launch-state
transition that let a failing launch pass.

## Provenance and adaptations

Upstream: https://github.com/k4zmu2a/SpaceCadetPinball
Pinned revision: cb9b7b886244a27773f66b0b19fdc2998392565e
License: vendor/LICENSE (MIT). Original artwork/audio remain original game assets.

vendor/ is a pristine source snapshot. tools/extract_math.py extracts selected
method bodies without changing them. src/provenance.json records the input hash.
src/port_types.h supplies the small ball data shell and a positive-finite square
root implementation missing from the target math library. The original full
TBall class and object ownership graph have not yet been ported.

tools/export_table.py builds an instrumented COPY of the original desktop engine.
It exports its initialized collision geometry, including original radius offsets,
groups, active states, elasticity, smoothness, thresholds and boosts.
data/table.json contains 1227 line/circle edges; moving flippers are separate
objects and are not included in that count.

src/world.cpp adapts the base-plane portion of pb::timed_frame and
TTableLayer::FieldEffect. It preserves the original half-ball-radius subdivision
and swept ray/contact sequence. Its fixed grid and banked records replace desktop
pointer containers. Gravity noise is held at its midpoint and the full-charge
launch starts at the settled plunger contact with a midpoint boost of 105 so traces
are repeatable. This is not yet an end-to-end port of plunger input/feed timers.
The offline packer currently reconstructs line coefficients from exported endpoints.

The native square-root shim differs slightly from desktop libm; the current 256
primitive cases agree within 0.000000554 relative-to-max(1, magnitude).
Long billiard trajectories can amplify tiny float differences; matching these
primitive tests does not prove full engine equivalence.

## Reproduce

Install LLVM-MOS SDK 23.4.0 and set MOS_CXX to mos-cx16-clang++ if necessary.
The VM default is /opt/llvm-mos-sdk-23.4.0/llvm-mos/bin/mos-cx16-clang++.

    sh direct/build.sh
    prove -v direct/t/native.t
    perl direct/t/frame_budget.pl  # expected to FAIL until optimized

The existing t/run_x16.pl supplies the bounded native emulator runner. MATH and
WORLD are headless diagnostic PRGs; WORLD.BIN must accompany the latter.
Tests report frame cost separately from correctness. The 60 Hz gameplay limit
remains 133333 cycles at 8 MHz.

To refresh the full original inventory, run tools/export_table.py, build its
direct/build/reference CMake project, and launch that desktop executable with
CMDRX_EXPORT set to an absolute JSON path from the original game asset directory.
The original Windows EXE is never part of a native package.

## Remaining work

The slowest initial measured world frame is approximately 1.12 million cycles
(140 ms at 8 MHz), so this baseline is NOT suitable for a 60 Hz gameplay release.
First optimize candidate lookup, memory access and numeric hot paths while retaining
the direct version as the comparison reference. Do not silently alter bounce
parameters or slow simulation time to disguise the performance problem.

Port the moving flippers and their contact response, actual plunger timing,
gates, ramps/collision layers, targets, drains, timers and mission rules. Connect
VERA presentation, original audio, controls, explicit start instructions and a calm
attract mode. Preserve 128-bit scores in arithmetic, display and storage.

The existing 0.2.0 game remains on master at d82a1ac for reference. Its physics are
not fixed by building these independent probes.
