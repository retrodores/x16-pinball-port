# Milestone physics verification — 2026-11-19

## Implemented correction

The stationary tip-circle sweep closes an observed outside-to-outside grazing miss on both flippers. At the original rest pose, the left tip is at Q8 (246,3362), radius 126. Placing the ball at (46,3284), velocity (8232,11704), floor mask 1 previously crossed the tip circle with zero flipper hits. Both endpoints of the half-frame sweep lay outside the circle, so the endpoint capsule test missed it. The mirrored right-side case had the same failure.

flipper_sweep.h resolves the first circle contact with existing integer arithmetic, passive rebound, and the remaining fraction of that half-frame. The helper runs only for an unchanged flipper pose and a world sweep with zero intervening contacts. It does not approximate a reflected world path as a straight segment. The powered-flipper branch from ecd54e9 remains unchanged. The existing paddle core runs in bank 61. The static sweep calculation runs in bank 62; an unbanked wrapper restores the caller bank before the remaining world sweep can select geometry banks.

The original reference is direct/vendor/SpaceCadetPinball/TFlipperEdge.cpp: its separate tip circle and two faces, built by set_control_points, are the geometric reference. This is a targeted correction, not a full moving-flipper reconstruction.

## Repeatable checks

Run python3 cadet/game/test_routes.py after the normal model generation/build prerequisites. It builds isolated ROUTES.PRG/ROUTES.RUL/ROUTES.PHY and TIP.PRG/TIP.RUL/TIP.PHY with build_native, compares the host and native result lines, and records cadet/play-build/routes-results.json.

- ROUTES: 254 assertions pass with host ASan/UBSan and native 65C02 at both 512 KB and 2 MB.
- TIP: 10 assertions pass with host ASan/UBSan and native 65C02 at both RAM sizes. Covers each mirrored grazing contact, no energy gain, a farther parallel non-contact, and an elevated ball that must miss the floor flipper.
- Existing powered-flipper host contact fixture: all six cases pass with the proposed sweep integrated.
- Isolated ecd54e9 engine plus this sweep: 100-seed ASan/UBSan soak passed with 300 drains, zero escapes/stalls, 1399 bumper hits, 2445 flipper hits, 1252 ramp entries, 13 collision-guard hits and 267 returns. This soak predates the new mechanism rules and is not an integrated milestone performance result.

## Current rules-enabled host audit

After rules integration and paddle banking, optimized and exhaustive (-DCADET_BRUTE) ASan/UBSan builds each ran 40 seeds. Full output matches, state hash 0cfd4551: 115 drains, zero escapes/stalls, 1152 bumpers, 805 flipper hits, 455 ramp entries, 11 collision-guard hits, 383 returns. Runs stop on GameOver or at 18000 frames, so not all runs finish a game. Logs are verify-milestone-optimized.log and verify-milestone-exhaustive.log under play-build. No sanitizer violations appeared. This validates spatial-index equivalence to exhaustive candidate search for those trajectories; it does not certify original-game behavioral fidelity.

## Banked native verification

The final suites were rerun after paddle banking, static-tip banking and named ELF overlay extraction: ROUTES 254, TIP 10, and all powered/passive contact cases pass at both 512 KB and 2 MB. test_build_native.py independently compares main PRG sections and both padded overlays against LLVM readelf/objcopy output. Its TIP check and final CADET/TEST checks pass. The native suites also pass after the final large-award overflow-preflight correction. This catches an actual integration failure where raw FULL output could not distinguish sections sharing A000 and emitted the wrong overlay bytes. The final build helper extracts the named ELF sections explicitly.

## Topology scope

Fixtures check the recovered component/kind/mask/action before exercising a crossing. Each relevant segment is tested on layers 1, 2 and 4.

Directed gateway IDs: 1152 (ramp rollback 2→1), 1153 (ramp deck 2→4), 1158 (deck return 4→2), 1205 (launch entry 1→2), 1210 (underpass exit 2→1), 1211 (underpass entry 1→2), and 1203 (ramp triangle 2→2). A floor ball crossing 1203 stays on the floor.

Rail IDs: 697–700 (component 106, tunnel layer 2) and 521/523/525/527 (component 306, deck layer 4). Legal-layer collisions reflect and preserve the layer; other-layer crossings do not acquire a layer or a collision.

These are selected deterministic boundary checks, not complete route coverage. The upper underpass gateway 1209 still needs a fixture representing a legal approach; a midpoint probe encounters adjacent wall 699 first. It is not classified as a defect by this test.

## Extended integrated input

verify_milestone_inputs.py generates verify_milestone_input.h. MILESTONE_INPUT builds place deliberate mechanism interactions after frame 7000: both three-target hazard banks, both kickbacks, both three-lane banks, all three wormholes, the black-hole kickout, and hyperspace kickout. The final placement is frame 10900. Host production-engine probes confirm all 19 targeted collisions/captures, including gate-open events on hazard completion.

These placements exercise mechanism/render/audio cost and hold/release timers. They are not evidence that a player can reach every location legally. test_native.py accepts RAM, MHz, expected frame count, and program; its 133333-cycle assertion is unchanged. Root integration owns the final >6000-frame timing runs.

## Remaining limits

Moving-tip continuous collision and original tapered-face normals are unfinished. Original face normals differ about 3.612 degrees from the center-axis perpendicular because the base and tip radii differ. The port still uses its existing capsule-based face normal and moving-flipper boost approximation. Recordings remain required for perceptual shot-angle comparison.

No sustained 60 FPS or 2 MHz claim is established by these tests. The main plunger's visible animation and purple-ramp occlusion are covered by the rendering work, not this collision suite.
