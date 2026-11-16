# CmdrX Cadet: direct mechanics checkpoint

This is a direct C++ port of the recovered k4zmu2a/SpaceCadetPinball engine to
Commander X16 through LLVM-MOS. The current programs are native diagnostic
probes, not a playable game or a complete port. The older Prog8 prototype is
preserved on master and under src/; building these probes does not change it.

## Implemented and exercised natively

- Original line/circle intersection, normalization and rebound methods.
- Original flipper contact detection, rebound, motion, substep scheduling and
  swept contact against a stationary ball. Seven flipper/control method bodies
  are extracted verbatim; table geometry comes from the initialized desktop engine.
- Original plunger input/messages, charge/release response and feed/pullback/release
  timer callbacks, also extracted verbatim. The integrated probe waits for ball
  feed, lets the ball settle, holds charge and releases through the original chute.
- Base-plane world coordinates, gravity, damping, half-ball-radius subdivisions,
  653 static physical edges and banked broad-phase lookup.
- Conservative integer rejection of distant edges, followed by the unchanged
  floating-point contact formulas. A retained unoptimized world implementation
  is compared against the optimized one at every frame of the launch trace.

Native tests run independently at 512 KiB and 2 MiB. Flipper tests cover full
extension/retraction, reversal, rest/moving/held/retracting contact and moving
flippers striking stationary balls. Dedicated plunger tests cover partial/full
charge, exact timer boundaries, occupied-feed retry, reset cancellation and
original relaunch/tilt paths. Tests also require identical results at both RAM sizes.

## Provenance and platform adaptations

Upstream: https://github.com/k4zmu2a/SpaceCadetPinball
Pinned revision: cb9b7b886244a27773f66b0b19fdc2998392565e
License: vendor/LICENSE (MIT). Original artwork/audio retain their original origin.

vendor/ remains pristine. tools/extract_math.py copies the selected method bodies
without rewriting them; src/*provenance.json records their sources.

The platform shells replace SDL ownership, dynamic component lists and heap timers:

- TBall retains only fields needed by this stage. The ownership adapter supports
  one ball, not the original multiball/object graph.
- Flipper constructor state is exported from the original initialized objects.
  A compact offset/value initializer reduces target code size. Both exported
  flippers have collision group 1, checked by the packer.
- port_types.h supplies the positive-finite square-root shim and sin/cos
  polynomials for the flippers' approximately +/-1.215-radian travel. These are
  not general-purpose libm replacements. Native/desktop flipper records must
  agree within 2e-5*(1+abs(reference)).
- A fixed eight-entry timer pool preserves millisecond deadlines, insertion order,
  and the original two-callback/overdue policy. The integrated tick is 60 Hz.
  Timer exhaustion is reported; no heap allocation is used.
- Plunger sound and rules callbacks are counted but are not yet connected to
  audio playback or mission rules. Random values are held at .5 for repeatable
  diagnostics; gameplay RNG is not integrated.
- world.cpp adapts the single-ball base-plane portion of pb::timed_frame and
  TTableLayer::FieldEffect. It interleaves ball and flipper substeps in the
  original order. Its 16-contact guard is a bounded diagnostic safeguard.
- The broad-phase bounds live in banked RAM, with a one-edge unbanked cache.
  WORLD.BIN uses 193640 bytes beginning at bank 32; its final bounds are in bank 55,
  so it fits the 512 KiB configuration. The packer still reconstructs static
  line coefficients from exported endpoints.

The retained reference world is the previous direct baseline, not the full
original desktop engine. Matching its trajectory and the primitive/component
checks does not establish complete game parity.

## Reproduce

Use LLVM-MOS SDK 23.4.0. MOS_CXX can override the VM default:
/opt/llvm-mos-sdk-23.4.0/llvm-mos/bin/mos-cx16-clang++.

    sh direct/build.sh
    prove -v direct/t/native.t
    perl direct/t/frame_budget.pl

The last command is the strict gameplay release gate and is currently expected
to fail. Its limit remains 133333 cycles per 8 MHz frame; do not raise it.
The native build uses -Oz to fit the combined mechanics in unbanked RAM.

MATH, WORLD, REFERENCE, FLIPPER, MECHANISMS and PLUNGER are diagnostic PRGs. Run
with the bounded t/run_x16.pl testbench runner. WORLD.BIN must be in the filesystem
for WORLD, REFERENCE and MECHANISMS. They are not interactive game programs.

    perl t/run_x16.pl direct/build/mechanisms.prg direct/build

To refresh the original state export, run direct/tools/export_table.py, build its
COPY of the original engine under direct/build/reference, and run that executable
from the user's original game-asset directory with CMDRX_EXPORT set to the absolute
output JSON path. No original Windows executable or ROM belongs in a package.

## Performance and next work

The combined mechanics now fit in native main memory, but the 60 Hz CPU budget
is still not met. Exact current measurements are in evidence/direct-mechanics/.
The optimized launch-only path is about 66 ms worst case; the integrated
launch/flipper scenarios are about 136 ms. The former was about 140 ms before
collision filtering. These are different scopes and must not be compared as
though they measure the same workload.

Further work must address software-floating-point hot paths and banked code/data
layout while retaining the original implementations for behavioral comparison.
Do not change bounce coefficients, loosen comparison tolerances or slow simulation
time to hide a performance problem. Main-memory headroom is small and will need
attention before adding the rest of the engine.

Still unfinished: gates, ramps/collision layers, targets, full drain/game lifecycle,
mission rules, gameplay rendering, controls, original audio and scoring integration.
The final game still requires the original graphics/audio, separate sound/music
switches, listening mode, a calm attract screen, clear start/launch instructions,
and unsigned 128-bit scores throughout arithmetic, presentation and storage.
No physical X16 hardware verification has been performed.
