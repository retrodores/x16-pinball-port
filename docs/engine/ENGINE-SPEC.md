# Space CmdrX16 engine: implementation and hand-coder specification

Version 1.0 • Author: Codex, writer/creator • 2026-11-19
Implementation baseline: `9534fb8ed127092b0e9580ab75bfaf5d010e9b94`, branch `spacecadet-fidelity`.

## Purpose and authority

This describes the existing single-ball X16 engine, not an idealized replacement.
It is intended for a programmer implementing the engine by hand, including in
another language. Read this with `engine-contract.json`, its JSON Schema,
`reference-data.json`, and the cited source modules. Source paths are relative
to the repository root. The generated reference data contains decoded collision
records and lookup tables, file hashes and a symbol index. It is a snapshot, not
a supported level-authoring format or a new runtime loader.

“MUST” denotes a compatibility requirement; “current” describes behavior which
may deliberately be improved. Unfinished behavior is not a promise of fidelity.
Old lab README files describe earlier prototypes; this document concerns
`cadet/game`. The current display is tiled 640×480, not the older 320×240 bitmap
prototype. No engine code or artwork was changed to produce this specification.

The code still includes table-specific group IDs, rules, camera coefficients,
asset packing and bank allocation. Reusing it as a general physics library requires
separating these contracts. No level editor, universal table loader, scrolling
camera or multiball system exists in this baseline.

## Module boundaries and entry points

| Source | Responsibility |
|---|---|
| cadet/game/engine.h | Game, Edge, Meta, enums and public entry points |
| cadet/game/engine.c | Integer integration, indexed sweeps, contacts, flippers, state |
| cadet/game/rules.inc | Table-specific scoring, captures, gates, lanes and timers |
| cadet/game/flipper_sweep.h | Stationary tip-circle continuous collision |
| cadet/game/play.c | Loading, input, projection, sprites, panel and main loop |
| cadet/game/depth.c, depth_rect.s, depth_quant.s, mask_pixels.s | Depth visibility and masked ball |
| cadet/game/dynamic.c | Budgeted background patches and instant slingshots |
| cadet/game/audio.s, music_lz.s.inc | IRQ, PCM mixer, YM/PSG and music buffering |
| cadet/game/pack_*.py, prepare_runtime.py | Offline conversion and generated tables |
| cadet/game/build_native.py, linker/link.ld | Main program and banked overlays |

Public simulation API:
- `game_load() -> bool`: load geometry and overlays; invalidate candidate cache.
- `game_start()`: clear Game/rules, retain visual epoch continuity, start 3 balls.
- `game_frame(left,right,pull,nudge)`: advance exactly one simulation step;
  restore caller RAM bank.
- `game_place(x,y,vx,vy,mask)`: test placement, not a complete game reset.
- `add_score(u16)`: exact checked addition; see scoring below.
- `game_lamp(original_group)`, `game_pose(original_group)`: table visual queries.
- `sound(id)`: dispatch using Game.last_group, last_kind and sound_value.

Game is an in-memory C structure, NOT a portable disk record. A replacement
implementation should serialize named fields explicitly; never assume a host
compiler's struct alignment matches LLVM-MOS. The Edge disk record below is
explicitly packed, little endian, 32 bytes.

## Hardware, memory and ownership

Target: stock 65C02 at 8 MHz; minimum 512 KB banked RAM; test 2048 KB too.
No 65816 instructions or floating-point runtime physics. RAM bank register is
$00; $A000–$BFFF is the 8192-byte bank window. A pointer into that window is
valid only while its bank is selected.

Main PRG starts at $0801, with a two-byte little-endian load address.
Link region length is $96FF. Software stack starts $9F00, BSS end MUST be
at most $9B00 (1024 bytes of reserve). Zero-page allocation is compiler-owned;
linker declares BASIC ZP range $0002–$0080. This is not a free scratch area for
a replacement IRQ. Assembly helper calling conventions MUST be adapted when
changing compiler.

| Banks | Live contents |
|---|---|
| 1–3 | Per-layer spatial index |
| 4–9 | Variable-length edge candidate lists |
| 10 | Compressed depth block index |
| 11 | Sprite descriptors, projection and depth-quantization tables |
| 12–16 | 32-byte collision records |
| 17,18,45–50 | Compressed depth blocks |
| 19–30,51–57 | Resident PCM, logical stream jumps from bank 30 to 51 |
| 31 $A000–$AFFF | 4096-byte music dictionary/read-ahead ring |
| 32–44 | Compressed music |
| 58–60,63 | Dynamic background descriptors and patches |
| 61 | .rules overlay: rules and powered paddles |
| 62 | .physics overlay: dispatch, limiter and stationary tip sweep |

Geometry initially streams padding/obsolete data through banks later reused by
depth/UI. Load order MUST finish replacements before gameplay. Geometry bounds
are also in Edge; do not treat temporary bulk geometry occupancy as permanently
live. Bank 0 is not allocated by this engine.

Bank-changing trampolines MUST execute in resident RAM and MUST NOT inline into
an overlay. Save old bank, select overlay, call, restore old bank. A nested
rules call from bank62 must return to bank62 before executing its caller.
Copy banked Edge into resident memory before event dispatch. Never retain an
Edge pointer across a helper that changes its bank. Interrupt code restores
bank selection. Rendering depends on bank11 selected after UI loading and on
helpers restoring it.

Both overlays have virtual address $A000 but different physical banks. Extract
named ELF sections .rules/.physics independently, pad each to 8192 bytes, and
emit matching NAME.RUL and NAME.PHY. Do not use a raw overlapping-VMA image to
extract them. Never mix overlays and PRG from different builds.

## Arithmetic and simulation clock

Coordinates x/y/z, velocity and acceleration use signed 16-bit values scaled
by 256 (Q8). Normals use 256 = 1. Products use signed or unsigned 32-bit
intermediates as appropriate. Collision time fraction is 0..256. Projection
and rebound rescaling use 4096 = 1 (Q12). Ramp coefficients in the current
generated Meta are Q8, despite older route-prototype documentation using Q12.

C signed division truncates toward zero. Preserve this for negative values:
an arithmetic right shift or Python // is not an interchangeable substitute.
Unsigned shifts and masks must retain their exact widths. Integer square root
returns floor(sqrt(n)). fraction(n,d) returns min(256,floor(256*n/d)); callers
provide valid nonzero denominators. ratio12 returns floor(4096*n/d), with its
zero-denominator behavior defined in engine.c.

One game_frame is nominally 1/60 second. Main loop calls once when the VBL
counter changes; it does NOT catch up missed frames. Rules timers use units
of 1/120 second and normally decrement by 2 per call. A timer of 211 expires
after 106 calls. game.tick advances by 2 and wraps as uint16.
Actual VGA refresh is 25,000,000/(800*525), approximately 59.52381 Hz.
Physics is therefore slightly slower than exact 60 Hz wall time; music has
separate compensation.

Per InPlay step:
1. Tick rules; decrement active flash/disable counters and nudge lockout.
2. Detect flipper key transitions; rotate lane bits and emit press/release cues.
   Phase range 0..120; press adds 50 capped at120; release subtracts25 floored0.
3. Process plunger. Serving returns before integration. Between/Captured process
   wait and transition then return.
4. Nudge, if permitted: alternate vx ±768, vy -=1536; ignore=60.
5. Resolve a gravity well/capture; otherwise choose ramp force or default
   (fx=0, fy=3068).
6. acc += force; dv=trunc(acc/60); velocity += dv-trunc(velocity/300);
   acc -= dv*60. Limit max(abs(vx),abs(vy)) to15360 by proportionally
   scaling both components using truncation.
7. rem += velocity; displacement=trunc(rem/60); rem -= displacement*60.
8. Sweep movement and resolve contacts. For y>1800 on mask1, use two half
   steps with intermediate flipper phase, stationary tip checks and paddles.
   Recompute second displacement from changed velocity after a collision.
9. Ramp z=dot(x,y,ax,ay)+az+77. Drain and increment escapes if x outside
   [-3072,3072], y>3900 or y<-4352.

The speed cap bounds each full-step component displacement to256 Q8 units.
Changing cap, subdivision or world bounds requires revisiting the circle
discriminant overflow proof and spatial-index expansion.

## Spatial model and binary geometry

Current model: 1217 edges, 144 components, 33 metadata entries.
Group is a dense index, not an original component ID; original_groups maps it.
Arrays reserve160 component entries. Layer masks are1,2,4; collision accepts
edge.mask & game.mask. Grid is48×64 per layer, cells128 Q8 units wide, origin
(-3072,-4096). Query uses the motion midpoint.

Index cell: gx=trunc((x+trunc(dx/2)+3072)/128), gy similarly with4096.
Reject out-of-grid; ci=gx+48*gy plus3072 for layer2 or6144 for layer4.
Read LE u16 list offset at bank1+(ci>>12), offset2*(ci&4095).
List lives bank4+(offset>>13), at offset&8191: u16 count then count u16
edge IDs. Lists never cross an8192-byte bank. Runtime cell buffer128 words;
generator enforces <127 candidates before layer filtering. Current maximum67.

Edge ID uses bank12+(id>>8), offset32*(id&255).

| Byte offset | Type | Field / meaning |
|---|---|---|
| 0,2 | i16 | x,y; line start or circle center |
| 4,6 | i16 storage | ex,ey; line end OR low/high unsigned radius-squared words |
| 8,10 | i16 | nx,ny; line normal Q8 |
| 12 | i16 | radius Q8; circles only |
| 14,16,18,20 | i16 | xlo,ylo,xhi,yhi bounds |
| 22 | u8 | dense component group |
| 23 | u8 | smoothness numerator /256 |
| 24 | u8 | kind enum |
| 25 | u8 | layer mask |
| 26 | u8 | elasticity numerator /256 |
| 27 | u8 | boost in whole velocity units |
| 28 | u8 | Meta index |
| 29 | u8 | flags |
| 30 | i16 | inward-speed boost threshold Q8 |

Flags: bit0 circle; bit1 active; bit2 rollover state pair; bit3 required lamp
state for that pair. Kind values in contract JSON exactly match enum order.
Circle radii <=181, squared radius carried across ex/ey, NOT recomputed from
signed ex. Current arc_bounds=0.

Offline generation quantizes with Python round(value*256), clamps to
[-32767,32767]; normals are derived from line direction before quantization.
It expands candidate-cell coverage by131 Q8 units and tests actual shape/cell
overlap. Do not substitute an unexpanded grid or independently reorder edge
IDs: deterministic ties choose the smaller ID.

## Collision algorithm

Filter candidates by bounds, flags/lamp, open gate, active mask, disabled group,
ramp-ignore set and gravity-well enable. Swept bounds extend by5 Q8 units.

Line: delta=dot(displacement,normal). Require delta<0. Starting signed
distance d0 must be >=-3 and d0+delta<=0. Time is0 if d0<=0, otherwise
fraction(d0,-delta). Hit point must be within segment bounds along its
dominant axis. Earliest t wins, ties use smaller edge ID.

Circle: reject nonapproaching projection or an already-inside starting point.
Use a=dx²+dy²; projection=-dot(start-center,displacement) without Q8 divide;
cross=(sx*dy-sy*dx). Discriminant=a*r²-cross². Tangency (cross²>=a*r²)
does not hit. t=fraction_wide(projection-isqrt(discriminant),a), clamped
to0 when numerator<=0; reject numerator>a. Normal is (hit-center)/radius
in Q8. Source has conservative early-outs and sorted circle candidates;
exhaustive/reference mode must yield equivalent game state.

Move loop resolves at most5 contacts per substep. After event:
- Update remaining time by (256-t)/256.
- Non-solid event: remember ramp edge (up to8), otherwise temporarily disable
  component where applicable; move one Q8 unit along each nonzero motion axis.
- Solid: respond, then separate by normal/64 (integer truncation).
- Recompute remaining displacement from velocity/60, remaining fraction and
  substep count. Increment guard_hits if the fifth iteration is reached.
The guard is a limit, not evidence that all remaining movement was solved.

Rebound requires inward=-dot(v,n)>0. With s=smoothness, e=elasticity:
speed=isqrt(vx²+vy²); normal_part=floor(inward*(s+e)/256);
temp=(v*s+n*normal_part)/256; final_speed=speed-floor(inward*(256-e)/256).
Normalize temp using ratio12(final_speed,|temp|). Then add n*boost and limit.
Boost is disabled below the inward threshold. Bumper fire inhibits repeat
boosts for12 timer units. Rebounder visual fire does not inhibit another kick.

## Flippers

Each side has pivot and121 precomputed tips. Closest position on pivot-tip
segment uses Q8 fraction f. Contact radius is156-floor(30*f/256), tapering to126.
Push an overlapping ball to radius+2. Front-face impulse depends on phase
delta, side, distance from pivot, angular coefficient and normal alignment;
the exact operation order is paddle_core in engine.c. Radius is a capsule
approximation; it is not a full tapered-face normal solution.

Crucial regression: a powered front-face paddle MUST impart impulse even when
the ball is stationary or moving outward along its normal. Passive inward<=0
contacts must not acquire that powered impulse. Back-face elasticity decreases
with pivot distance; do not model both sides as an identical moving wall.

flipper_sweep.h covers outside-to-outside grazing of a STATIONARY tip circle
(radius126). It is invoked only after a world sweep with no contacts and
unchanged phase. It does not provide continuous collision for a rotating tip.
Full moving-tip/face CCD remains unfinished. Preserve test_flipper_contact.c
and test_routes_tip.c as behavior examples rather than claiming this gap solved.

## State, table events and exact scoring

State numeric order: Ready0, Serving1, InPlay2, Captured3, Between4, GameOver5.
Start sets balls=3, multiplier=1 and serves; ball_number=4-balls.
Serving positions at generated serve_x, plunger_y-2, z77, mask1.
Pull begins charge1, advances via charge_clock in2/3 increments, capped100.
Release when Serving launches vy=-min(charge,60)*256. Plunger animation/sounds
also work away from the plunger, without launching a distant ball.

Drain: Between, wait120, zero velocity/mask, clear ramp; consume replay if
armed, otherwise decrement balls. On timeout serve or GameOver. Captures zero
velocity and remainders, wait the metadata delay, then apply exit position,
velocity/layer/height. Sink340 has explicit vy=-7168 exit correction.
Kickout releases retain pre-capture layer/height and disable only that component
for6 timer units; sinks disable their exit for2.

Rules include two three-lane bit banks, lane rotation, bumper levels0..3,
7200-unit decay, hazards/gates, kickbacks, wormhole destinations/replay and a
five-stage hyperspace sequence. Rules are table policy, not collision primitives.
Examples: all three lanes trigger600-unit flashing and upgrade; hazards flash240;
wormhole awards2500/5000/7500; hyperspace awards10000/20000/20000/50000/150000
with hold211/367/211/140/306. Exact mappings and timer order are in rules.inc;
reference-data includes that normative policy source with its hash.

Score is16 unsigned little-endian bytes (0..2^128-1). Decimal digits are40
numeric bytes, least-significant first, updated in parallel.
MUST preflight the entire award before mutation. Overflow sets overflow flag,
preserves binary score and decimal digits, and prevents further additions.
Large u32 awards are preflighted before splitting into50000 chunks.
The panel displays9 low digits; larger scores trigger an explicit panel-overflow
message and exact decimal debug output. No complete persistent save format is
implemented by this Game structure; do not promise one.

## VERA rendering and VRAM contract

VERA I/O base $9F20. addr helper selects ADDR0, increments by1 via high byte
$10|(address>>16); DATA0 at$9F23. DATA1 at$9F24 is used for dual-port masking.
Display setup: DC_VIDEO=$51, HSCALE=119, VSCALE=117, border0;
L0_CONFIG=$12, MAPBASE=0, TILEBASE=$0B, scrolling0.
This is a 64×32 map of16×16 4bpp tiles, enabled layer0 and sprites over
640×480 output. Scale registers intentionally enlarge/crop the logical scene.
A map entry is LE u16:10-bit tile index, flip bits, high-nibble palette bank.
Background palettes are16 banks of16 VERA12-bit colors.

Current VRAM:
- $00000..$00FFF:4096-byte tile map, row stride128 bytes.
- $01000..$190FF:770 base tile patterns,128 bytes each.
- $19100..$1D9FF: sprite patterns (SPRITE_BASE102656, FONT_BASE121344).
- $1DA00..$1E1FF:64 glyphs,32 bytes each.
- $1E200..$1E27F: masked16×16 ball scratch.
- Following space: private slingshot patterns; runtime tile960..972 at
  $1F000..$1F67F reserved for compact-footer copies.
- $1F9C0:PSG registers; $1FA00:512-byte palette; $1FC00:sprite attributes.

Generated dynamic descriptors are authoritative for private pattern addresses.
Do not extend sprite/font output into dynamic/footer/PSG space.
graphics.json's old sprite_reserve_start is not the active SPRITE_BASE.

Sprite attributes are8 bytes: address/32 word, x word, y word, depth/flip byte,
size/palette byte. Current tile helper uses depth byte12 and descriptor sizes.
Reservations: ball0; left flipper1..9; right10..18; plunger19..21; score22..30;
player31; ball number32; status33..72; music73..75; controls76 onward.
Hide by zeroing depth byte. Unused cells in a multi-tile pose are hidden.
Glyph controls are sprites; they consume the same finite128-sprite budget.

Projection is not direct screen-space physics:
depth=6317-(y*104+z*234)/256, clamped2048..10232.
camera_y=(y*(-234)+z*104)/256+971.
scale=projection_scale[(depth-2048+4)>>3].
screen=(191-projected(x,scale),243-projected(camera_y,scale)).
projected preserves sign around abs(value)*scale>>12.
Choose one of7 ball sizes by squared camera-distance cutoffs in ui.h.
Do not replace this with a constant pixel/world scale.

UI bank11: descriptors at$A000, projection1024 u16 at$A800, depth cutoffs
256 u32 at$B000; reserved legacy row table follows$B400.
Depth table is365×470; quantized depth uses source high byte. Each row pads
to384 with255, then splits into six64-pixel blocks. Index has2820 LE u16
offsets (5640 bytes). Deduplicate encoded blocks and prevent bank crossings.
PackBits variant: tag1..127 copies literal bytes; tag128|n repeats next byte n
times. Decode exactly64; this is not the signed-control TIFF PackBits convention.
Logical block offset maps banks17,18,45..50. Pixel visible iff stored depth
is greater than ball quantized depth; out-of-table regions are visible.
Depth255 yields no in-table visible pixels.

Fully visible ball uses original sprite; fully hidden ball hides; partial
visibility copies/masks into scratch, preserving other scene layers.
Dynamic background runs apply (old & ~mask)|(value & mask) so neighboring
4-bit pixels survive. Descriptor record: run_count u8, pose_count u8,
byte_count u16; then run_count records (address_low u16,address_high u8,
length u8); mask byte_count; then byte_count bytes for each pose.
At most128 pixel bytes per allowed normal update. Two fast slingshots instead
swap private tilemap entries immediately on visual_epoch change, even when
normal update budget is0. Transitions may span frames; this is not an atomic
full-background repaint.

## Audio and interrupts

Install saves the prior IRQ vector and chains it, preserving registers and RAM
bank; uninstall restores hooks and sound state as implemented in audio.s.
Keyboard hook is at$032E; callback maintains128 key states using high-bit release.

VBL IRQ increments lab_ticks, runs PCM and music. Music gets an additional tick
every125 frames, giving126 nominal60-Hz ticks/125 VBLs. Preserve VERA control
and address state around IRQ PSG access. Avoid compiler-owned zero-page scratch
in interrupt assembly. Multi-byte shared counters require brief atomic access.

PCM is signed8-bit mono, rate register29:11062.6220703125 samples/second.
Initial lead256 samples; regular quota185 or186 from fractional accumulator
55840/65536 per VBL. Three independent voices: table, flipper, plunger.
Table voice uses rank priority; weaker events do not interrupt stronger ones.
One voice unattenuated, two each shifted right arithmetically1, three each2.
Streams cross8192-byte pages and jump bank30→51. Do not truncate samples or
reuse music banks. Silence/reset FIFO behavior and underrun counters are in
audio.s; counters survive game restarts.

Music is compact ZSM command bytes without its16-byte file header, LZSS packed:
LSB-first flags,0=literal,1=LE u16 token; distance=(token&4095)+1,
length=(token>>12)+3. Overlapping copies are allowed.4096-byte dictionary.
Current uncompressed stream length214239 is embedded in the assembly reader;
changing tune requires updating that contract and tests, not just replacing BINs.
ZSM commands:0..63 PSG register plus byte;65..127 FM register/value pair count;
128=end;129..255 delay low7 bits. See music_service for extension handling.
Main-thread decompression emits at most64 bytes per call towards2048-byte lead.
music_enabled0=off,2=priming,1=ready. Publish ready atomically only when primed;
M can cancel priming. IRQ does not decompress.

## Frame scheduling, diagnostics and limitations

The strict acceptance limit is133333 cycles at8 MHz, including IRQ, physics,
render and prefetch. Main display permits panel/normal patch work when
elapsed<80000; prefetch only when elapsed<100000. Always count work in the
same interval; do not move slow work outside measurement to pass a test.

Cycle and debug ports$9FB8..$9FBB and testbench termination$9FB4 are emulator
instrumentation, not portable hardware timers. Current player uses the cycle
reads for optional-work scheduling as well as diagnostics. Real-hardware
timing/scheduling must be validated separately; do not infer it from emulator
logs or assume those expansion registers provide a timer on physical X16.

Saved 12000-frame evidence (not rerun for this documentation):
512KB mean67549/max211847,89 over budget;2048KB mean67548/max211825,89 over.
Both record zero missed starts/music errors/PCM underruns. Reports lack a
source-commit binding, so these are historical saved results, NOT certification
of this exact artwork/presentation commit. Sustained60FPS is not established.

Other known gaps: moving-flipper CCD/tapered normals, seven historical contact
guard uses needing investigation, advanced mission/rank/bonus/reflex/extra-ball
policies, randomized throws, complete cue/timbre fidelity, dynamic depth and
multi-frame patch fidelity. A release label does not remove these limitations.

## Build, files and hand-coder acceptance

Build from repo root: `sh cadet/game/build.sh`. Compiler defaults to
/opt/llvm-mos-sdk-23.4.0/llvm-mos/bin/mos-cx16-clang; override MOS_CC.
Generated headers/BINs must already exist, or regenerate via assets argument
with the original locally supplied inputs and Python dependencies.
Full regeneration can replace customized artwork; preserve release artwork and
use its own generation procedure. This specification does not redistribute ROMs
or original executable/DAT files.

Runtime cwd MUST contain CADET.PRG, CADET.RUL, CADET.PHY plus:
MAP/TILES/PAL/SPRITES/FONT/UI.BIN, GEOM0..2.BIN, MUSIC0..1.BIN,
PCM0..2.BIN, DEPTH00..08.BIN, DYN0..3.BIN.
Load geometry/overlays, VRAM, music, PCM, depth, dynamic, UI; clear sprites;
initialize display/input/IRQ/game/dynamics; start music. On failure report load
failure and restore bank/screen. On quit restore keyboard, IRQ, RAM bank and
BASIC display. Launch from runtime directory:
`x16emu -c02 -mhz 8 -ram 512 -fsroot . -prg CADET.PRG -run -scale 2`.

Recommended reconstruction sequence:
1. Reproduce binary layouts, integer primitives and generated tables.
2. Make host-only game_frame pass existing score/math/route/flipper fixtures.
3. Match indexed and exhaustive seeded state hashes and investigate guards.
4. Implement resident/overlay loader and verify named ELF sidecars.
5. Implement static map, sprites, projection, depth and dynamic tests.
6. Integrate input and bounded audio IRQ with explicit compiler ABI adapters.
7. Run native suites at512/2048KB, then long timing/audio workloads.
8. Independently test physical hardware scheduling and distribution launchers.

Existing tests are executable specifications, not merely documentation:
test_score_host.c/test_award_large.c, test_math.c, test_routes.py,
test_flipper_contact.py, test_mechanisms.py, test_large_award.py,
test_feedback_events.py, test_build_native.py, native_check.py,
test_depth.py, test_dynamic.py, test_slingshot_render.py, test_audio_mix.py,
test_audio.py, test_ui.py and test_native.py. See RESUME.md for invocations.
Do not rebuild over another agent's release output without coordination.

Small normative arithmetic examples: trunc(-61/60)=-1 with remainder-1;
fraction(1,3)=85; isqrt(15)=3; score255+1 gives low bytes00,01;
max128+1 leaves max128 unchanged and sets overflow.
Powered stationary-ball and stationary-tip grazing fixtures must remain.

## Prog8 feasibility (assessment only)

Yes. Prog8 supports the65C02 X16 target, typed integer data, memory-mapped
variables, structs and assembly subroutines. It can express this architecture.
A hybrid is the lowest-risk route: Prog8 for state/rules/input/orchestration,
assembly for IRQ/mixing, bank trampolines, multiply/fraction/sqrt and measured
collision/render hotspots. Reuse packed assets and behavior fixtures.

This is a rewrite, not a drop-in compiler switch. Adapt LLVM-MOS register ABI,
zero-page ownership, ELF overlays and assembly syntax to the selected Prog8/
64tass build. Explicitly preserve interleaved LE word records (Prog8 word arrays
may split low/high bytes unless @nosplit). Banked variables require caller-managed
bank selection. Handle unsigned32 intermediate math deliberately; retain16-byte
score arithmetic. Parenthesize casts in compound arithmetic.

Pure Prog8 may be possible, but equivalent performance is unmeasured and the
current mixed implementation already exceeds the worst-frame gate. Do not
promise60FPS or assume high-level translation is faster. VERA FX optimization
would be a separately measured change with register-ownership implications.

Official documentation consulted2026-11-19 (stable pages report12.3.5):
https://prog8.readthedocs.io/en/stable/compiling.html
https://prog8.readthedocs.io/en/stable/programming.html
https://prog8.readthedocs.io/en/stable/variables.html

## Provenance and maintenance

Retain direct/vendor/LICENSE and source attributions. Engine code, converted
artwork/audio and original game data have different provenance; a private Git
remote does not change asset rights. Refer to the repository's existing notices.
Regenerate snapshot with `python3 docs/engine/export_contract.py`, then run
`python3 docs/engine/verify_contract.py`. Changes to the engine require review
of this prose as well as regeneration; the exporter cannot infer semantics.
