# Recovery notes — CmdrX Cadet wireframe

Writer: Codex. Date: 2026-11-17.

The active project is `/opt/cmdrx-cadet-direct` on the connected development VM,
branch `wireframe-rebuild`. The earlier `direct-engine` work remains preserved;
its base checkpoint is `973210b1288b62d27db575972c21b87906e867b2`.
There is no configured Git remote. This package's SOURCE.zip is a complete
recoverable snapshot; no unavailable chat is needed to build the game.

Read `wireframe/README.md`, `wireframe/AGENTS.md`, `wireframe/VALIDATION.md` and
`wireframe/CHANGELOG.md`. `wireframe/layout.py` generates the new 47-edge practice table.
`wireframe/table.json` is its geometry input; `recovered-table.json` preserves
the earlier Space Cadet geometry;
`assets/SFX.BIN` contains the seven original effects. `pack.py` generates the
banked geometry, spatial index and conservative occupancy data. `assets.py`
builds the wireframe bitmap, sprites, font data and PCM bank metadata.

`engine.cpp` is a new integer engine, separate from the recovered C++ methods in
`direct/`. `main.cpp` handles VERA rendering and real keyboard input. `sqrt.s`, `widemul.s` and `narrowmul_shared.s` provide small exact arithmetic primitives. `build.sh` creates
both CPU binaries; the 65816 build selects the existing native multiply helper.

Validation includes sustained host games, targeted native mechanics/arithmetic,
normal-ROM full-game replays, actual recorded sound waveforms, and SDL keyboard
input against the exact distribution PRGs. The frame budget is 133333 cycles at
8 MHz and must not be weakened. Consult the report for actual results.

Future artwork should replace assets and sprite art while retaining the world
projection and collision definitions. The default table is newly designed; the
recovered original layout is a preserved experiment and failed the timing gate. The first version has basic pinball rules;
the original mission/rank controller, tilt penalties, music and saved high scores
remain separate future work. Preserve vendor attribution and the older engines.
