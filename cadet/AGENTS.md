# Space Cadet fidelity work

## Current release work

Start at the [1.0 handoff](../docs/release-status/v1.0/HANDOFF.md) for the fixed release inputs and
validation. Keep the exemplar under `releases/1.0/exemplar/`. These earlier
fidelity notes still apply when working on the engine.

The user now authorizes restoring the original table, artwork, sounds and music
on top of the accepted integer 65C02 foundation. Work in this separate worktree.
Preserve wireframe-v0.2 and /opt/cmdrx-cadet-direct unchanged. Use the VM via DC.
Original recovered C++ and game assets are the fidelity oracle; keep vendor pristine.
Track C/assembly adaptations and original source provenance. Compiler choice follows
measured native results. Do not call a graphics/audio audition a playable port.
Keep the 133333-cycle frame budget at 8 MHz and exact 128-bit scoring.
Separate musical note/timing fidelity from instrument-timbre fidelity.
Retain tests, attribution and recoverable source. No original EXE or ROM in releases.

User correction: the wireframe mostly worked, but allowed routes across boundaries
that should be impossible in Space Cadet. Smooth wireframe performance is not
validation of original-table topology. Restore original rails, one-way gates,
ramp height/layers and legal transfers; test forbidden crossings explicitly.
Do not place original artwork over unrelated practice-table collisions.
Use VERA fully and convert effects/music to native X16 audio.

Delivery preference: preserve extraction-root launcher/PRG layout (no wrapper folder),
parent-folder x16emu.exe/rom.bin by default, and -scale 2 on both launcher paths.
Preserve faithful score/backbox/control presentation; see NEXT-MILESTONE.md.
