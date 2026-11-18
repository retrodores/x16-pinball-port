# Recovery notes — CmdrX Cadet wireframe 0.2

Writer: Codex. Updated for the user's wireframe refinement and 2 MHz direction.

Project: /opt/cmdrx-cadet-direct on the connected development VM.
Branch: wireframe-rebuild. No Git remote is configured.
Accepted 0.1 checkpoint: 6a1996d4dd7ec450d8ccae75419637ba5f3dda7a.
Earlier direct-engine checkpoint: 973210b1288b62d27db575972c21b87906e867b2.
This package's SOURCE.zip is a recoverable snapshot; no missing chat is needed.

The user's current goal is a playable wireframe game in its own right: close
unintended gaps, show a moving plunger, track score clearly, soften effects, add
music and support the stock 65C02 at 2 MHz with 8 MHz recommended. Do not switch
back to the dense recovered Space Cadet geometry as the default table.

Read wireframe/AGENTS.md, README.md, VALIDATION.md and CHANGELOG.md.
layout.py generates the 49-edge table; pack.py makes the spatial index and banked
collision model. recovered-table.json preserves the earlier original layout.
engine.cpp is the integer solver. main.cpp uses the IRQ video clock for fixed
physics updates and renders ball/flippers, mechanisms, plunger and exact score.
assets.py builds bitmap/sprite/font data. sound_assets.py generates original soft
PSG effects and music; audio.s handles their bounded 60 Hz IRQ updates while
preserving both VERA address ports. Older PCM/reference data remain in the archive.

build.sh makes both CPUs. test_native.sh tests arithmetic/mechanics and PSG audio.
verify_emu.py checks full-game replay agreement, 8 MHz cycle budget, simulation
clock conservation and 2 MHz display cadence. keyboard_test.py uses real SDL keys.
boundary_test.cpp fires 3,213 directed shots at perimeter segments and corners.
soak.cpp completes 120 games and counts traps, timeouts, drains and escapes.

Keep the strict 133333-cycle 8 MHz gate. Do not claim unbroken 60 FPS at 2 MHz;
report actual cadence from the instrumented tests. No automatic rescue/teleport
may conceal a physics defect. The fallback lost-ball path is counted as an escape
and must stay at zero in perimeter and stress tests. Preserve 128-bit scores and
all attribution. Original missions/ranks, tilt, multiball and saved high scores
are not implemented. Artwork and original-table restoration are deferred.
