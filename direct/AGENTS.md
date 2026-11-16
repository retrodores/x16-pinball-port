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

Current scope: verbatim line/circle/rebound math and a base-plane world integration
probe. Ramps, targets, moving flippers, gates, mission rules, runtime rendering,
audio, controls and score integration in the C++ target are unfinished.
Use data/table.json as the complete initialized original line/circle inventory.
world_manifest.json states the physical subset currently packed into WORLD.BIN.
