# Direct mechanics validation

`prove direct/t/native.t`: PASS, 736 top-level checks, both 512/2048 KiB.
Native nested probes include 22 plunger assertions and 12 integrated mechanics
assertions per RAM configuration. Flipper comparison has 96 records and 40
contacts per configuration. Every launch frame matches the retained native
baseline exactly. Native traces match between RAM configurations.

`perl direct/t/frame_budget.pl`: expected FAIL, exit 2. Limit 133333 cycles.
Launch-only worst frame: 525087 cycles (65.636 ms at 8 MHz).
Integrated worst measured frame: 1089833 cycles (136.229 ms).
The earlier baseline measurement before optimization was 1123772 cycles.
The integrated workload adds mechanical functions and is a different scope.

Vendor sources are unchanged. Generated method bodies were checked verbatim
against their pinned sources. Original exported static geometry is unchanged.
No hardware test or full-game parity claim is made.
