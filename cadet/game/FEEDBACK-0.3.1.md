# Development 0.3.1: source-backed feedback corrections

The November 19 OBS feedback identified missing lower rebounder animation,
mechanical sounds lost during wormhole holds, and inconsistent plunger sound.

## Engine corrections and original references

- **Rebounders 469–472:** `TWall::Collision` shows the fire bitmap for 0.1 seconds only when `TCollisionComponent::DefaultCollision` returns true. That requires projected inward speed **strictly greater than 1.0**, the recovered DAT threshold. A qualified hit awards 500 points; passive contact does not. The previous engine awarded the lower pair on any fresh contact and never exposed their fire pose.
- **Lower triangular lights:** `control::FlipperRebounderControl1/2` turn on `lite84/lite85` (DAT 180/181) for the same 0.1 seconds. `game_pose(469..472)` and `game_lamp(180/181)` now expose these actual events. Repeat qualified hits refresh the six-frame timer; firing animation does not suppress another rebounder impulse.
- **Rebounder audio:** source component 468 supplies the hard-hit SOUND5 cue and no soft-hit sample. Engine hard events use event 2; passive event 6 is intentionally silent in the component audio routing. The original threshold still permits a physical impulse at equality, while the control callback/score/visual requires strictly greater speed; this distinction is preserved.
- **Flipper sound timing:** `TFlipper::Message` plays its extend/retract cue on the input transition. The engine previously required reaching phase 0/120, dropping cues during rapid reversals, and also replayed the extend cue after a powered ball contact. A two-bit input latch now drives cues and lane rotation, including while captured. The duplicate contact cue is removed. Powered-flipper collision/impulse arithmetic is unchanged.
- **Plunger events:** `TPlunger::Message` accepts input independently of ball position in 3D Pinball mode. Pull/release now emit their events during play and capture as well as while serving. Only a ball already serving receives the existing launch velocity. Returning to the plunger while holding it preserves accumulated pull.
- **Plunger timing:** the DAT supplies eight poses. Original 3DPB pullback increment is `floor(100/(8*8)) = 1`, first applied immediately on press and then every 0.025 seconds. The engine now includes that immediate increment and retains the integer 25-ms cadence. Full pull therefore remains approximately 2.5 seconds, as in the source.
- **Explicit feed:** `SoundFeed = 16` is emitted by `serve()`; feed, pull (4), and release (3) carry component 473 / Plunger context. Feeding no longer depends on a display redraw. A new game clears the input latches and charge.

The threshold-based scoring correction intentionally changes score totals on
passive rebounder touches. Immediate plunger charge also shifts release power
by one charge unit for some input durations. These are source-backed changes,
not unexplained replay/hash regressions.

The sound bank has no supplied SOUND62.WAV, the original plunger pull sample.
The event is explicit, but playback remains intentionally silent until that
asset is available. SOUND5 belongs to the rebounders and must not substitute
for it. Feed and release retain their own original samples.

## Verification

`python3 cadet/game/test_feedback_events.py` passes **80 assertions** on the
ASan/UBSan host build and on native stock 65C02 r49 with both **512 KB and 2 MB**.

The fixture checks real swept contacts against all four recovered rebounders;
passive versus qualified scoring/sound events; six-frame pose/light expiry and
repeat-hit refresh; explicit feed/pull/release context; immediate pull and
25-ms stepping; partial flipper reversals while captured; global plunger
input during play/capture; preservation of held charge on ball return; new-game
reset; and retention of the powered impulse without duplicate input sound.
Logs are `feedback-host.log`, `feedback-512.log`, and `feedback-2048.log`
under `cadet/play-build/`.

The existing 216-assertion mechanism suite and exact 128-bit large-award
wrapper suite are rerun after these final engine edits; final results are
recorded below. Graphics/audio integration checks and frame-cycle measurements
are separate from these engine contracts.

Final engine regression results: the existing mechanism suite passes all
**216 assertions** on the ASan/UBSan host and each native RAM configuration.
The large-award suite passes **29 host assertions** and **32 native assertions**
at both 512 KB and 2 MB, including exact-maximum success, atomic overflow
preservation and RAM-bank restoration through the actual capture wrapper.
These runs use the final global-plunger and rebounder event changes.

Real-frame lower rebounder fixtures supplied to the graphics integration
test are `game_place(986,2249,-944,-396,1)` for 469/180 and the mirrored
`game_place(-986,2249,944,-396,1)` for 470/181. One `game_frame(0,0,0,0)`
produces one contact and starts both the fire pose and lamp timer at 12
units (six frames).

After event dispatch was moved into physics bank 62 to preserve the software
stack reserve, these same three suites were rerun successfully on host and
both native configurations: feedback 80, mechanisms 216, large-award 29 host /
32 native. Native lane and capture fixtures detected compiler inlining of
bank-changing wrappers into the overlay. The final `BANK_TRAMPOLINE`
attribute keeps those wrappers in unbanked text and prevents inlining.
The large-award fixture's three RAM-bank restoration assertions now also
exercise event bank 62 calling rules bank 61 and returning to its caller.
