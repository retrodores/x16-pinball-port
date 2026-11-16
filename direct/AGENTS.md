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
