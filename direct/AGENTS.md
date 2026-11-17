# Direct engine port
The user selected the most direct practical port of the recovered original
engine before revisiting Prog8. Work in this C++ branch; do not continue tuning
the pixel-map approximation as the main physics implementation.

Keep vendor/ pristine at the pinned revision. Extracted math method bodies
must match it verbatim. Put platform adaptations in port_types.h or separate
adapters and record them. Maintain attribution and license.

Build with sh direct/build.sh; run prove -v direct/t/native.t from repository root.
Use the VM and native r49 emulation at both 512 KB and 2048 KB.
The diagnostic probes are not a playable release. They may measure an over-budget
implementation, but no gameplay release may exceed 133333 cycles per frame.
Do not count differential tests as proof of parity for the full original engine.

Retain the 128-bit score requirement when connecting the game/rules layer.
Original graphics, original audio, separate switches, listening mode, a calm
attract screen, and obvious start/launch instructions remain requirements.

Current scope: verbatim line/circle/rebound math, moving flipper geometry/contact
and motion methods, original plunger input/feed/charge/release callbacks, and a
single-ball base-plane world integration probe. See direct/README.md for platform
adapters and the exact remaining limitations. Vendor code remains pristine.

The optimized static world must stay bit-identical to reference/world_baseline.cpp
for every frame of the launch comparison. Flipper comparisons cover 96 records,
including 40 contacts. Run all native probes on both RAM sizes. The strict
frame-budget gate currently fails; preserve that result until performance is fixed.

Use data/table.json for original initialized geometry and mechanical parameters.
world_manifest.json describes the physical subset in WORLD.BIN. Bank 55 now holds
broad-phase bounds; total model size is 193640 bytes. Main-memory headroom is small.
Keep source and a complete checkpoint recoverable; this VM repository has no
configured GitHub remote. Do not claim that a VM commit was pushed upstream.

Runnable preview: direct/PREVIEW.md and direct/build-preview.sh. Source is
src/preview.cpp plus bank-1 src/preview_ui.asm. Rendering must not use compiler
zero page registers. Keep banks 32..55 for the world. world::preview_tick follows
the original 120 UPS default; world::tick retains the earlier 60 Hz diagnostics.
Do not regress plunger release timing: t/preview_launch.cpp tests forty holds.
Run t/preview_native.py and actual SDL t/preview_boot.py at both RAM sizes. The
preview is explicitly over budget and incomplete; never relabel it as a finished
or stock-speed gameplay release. New/Pause/Exit commands must latch short taps.

User correction: the float preview was too slow to test; runtime must now be
integer-only. Current adaptation is direct/integer, generated from retained
float methods. Build with integer/build.sh and integer/build-preview.sh. Never
edit generated build/integer/src. All runtime math, including projection, is
fixed point; verify absence of soft-float symbols in the linked PRG. Keep the
original float reference and its test tolerances intact. Run integer/verify.py,
integer/preview_native.py and actual SDL tests on both RAM sizes. Fixed-point
comparison bounds are explicit in verify.py. Keep normal/test UI addresses
paired correctly. Float WORLD.BIN is incompatible with the integer loader.
FLIP.BIN uses banks 8..23. Exact integer time division avoids dt quantization.
Current normal and instrumented builds both use -Oz. Do not represent the latter
as an exact timing profile of the former. Frame spikes still exceed 133333 cycles;
only label this as a preview until the strict gameplay gate passes.

Performance preview 2: the integer static-edge cache has four slots. Preserve
bit-identical integer traces when making data-reuse optimizations. Optional
cpu816/build.sh replaces only multiplication with native 16-bit assembly;
it is not a full native-mode core. Its PRG requires -c816 and its own paired
UI.BIN. Both CPU variants still fail the strict frame gate. Consult
integer/PERFORMANCE.md before making CPU speed claims.

Collision/audio preview 3: integer world data now comes from data/layers.json,
with signature CY, seven bumpers and original ramp layer/field transitions.
Its banks are 32..58; the older 32..55 descriptions above apply to the retained
float world. Audio uses banks 24..31 then 2; UI stays in 1 and flippers in 8..23.
Both integer tick entry points use 120 UPS; the legacy 60 Hz diagnostic could
miss the 25 ms plunger release window after correcting remaining ray travel.
Run build-contact-tests.sh and verify_audio.py in addition to existing checks.
Contacts tests compare all seven bumpers, both paddles and ramp transitions on
host and both CPUs/RAM sizes. Real audio capture must verify all seven effects,
IRQ banking/native arithmetic, mute/stop and vector restoration. Keep the strict
frame gate unchanged, and do not call this a completed gameplay release.
