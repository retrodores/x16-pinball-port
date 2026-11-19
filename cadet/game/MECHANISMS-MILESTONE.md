# Mechanism milestone: development implementation

The original behavioral references are the recovered source under
`direct/vendor/SpaceCadetPinball/`, its initialized table in
`wireframe/recovered-table.json`, and the original DAT component IDs.
This is a single-ball subset. It is not a claim that the entire original
Space Cadet ruleset or all timing/rendering details have been reconstructed.

## Implemented contracts

| Mechanism | Production behavior | Original reference |
|---|---|---|
| Wormhole sinks 338/340/342 | Capture, disappear for 2 seconds, select the destination, release with that sink's DAT position/direction/speed. No selection awards 2,500; matching selection awards 5,000 and replay; different selection routes to the chosen exit and awards 7,500. Selection clears on entry. Only the selected exit's lamps/arrows flash during the hold. | `control.cpp:WormHoleControl`, `TSink.cpp`, `control_sink_score1` |
| Replay | Matching wormhole enables a replay until consumed by a drain. The original `table_set_replay(4.0)` argument is the information-text duration, not a four-second expiry. | `control.cpp:table_set_replay`, `BallDrainControl` |
| Kickouts 510/512/514 | Capture at the center with DAT captured Z, restore original Z and mask on release, clear velocity integration residue, and disable only the releasing kickout for 0.05 seconds. Geometry retains the actual DAT capture radius; field attraction uses source force 30/32. | `TKickout.cpp:Collision/FieldEffect/TimerExpired/ResetTimerExpired`; DAT attributes 305/306/408 |
| Black hole 514 | 20,000 points, 1.5-second hold, DAT release velocity. | `control.cpp:BlackHoleKickoutControl` |
| Hyperspace 512 | Five levels: 10,000, initial jackpot 20,000, 20,000, 50,000, 150,000; advance and decay after 60 seconds. Hold durations use the original control WAV lengths: 211/367/211/140/306 units of 1/120 second. Fifth hit enables gravity well. | `HyperspaceKickOutControl`, `HyperspaceLightGroupControl`, original SOUND35/36/38/39 |
| Gravity well 510 | Enabled by fifth hyperspace hit, 50,000 points, disables on capture; 286-unit hold from original SOUND7 duration. | `GravityWellKickoutControl` |
| Both kickbacks 505/507 | First contact arms for 0.7 seconds. Firing enables the original 55-unit boost, animated pose and sample; a spent kickback resets and closes its gate on the 0.1-second timer. | `TKickback.cpp`, `LeftKickerControl`, `RightKickerControl` |
| Gates 501/502 and hazards | Fresh-ball feeding opens both gates. Each three-target hazard bank awards 750 per hit and reopens its corresponding gate on completion. Individual hazard lamps flash for two seconds then stay on; completion flashes the bank for two seconds then clears. Gate lights flash for five seconds then the enabled lamp stays on; outlane entry starts the warning flash until reset. | `PlungerControl`, `Left/RightHazardSpotTargetControl`, `Left/RightKickerGateControl`, `OutLaneRolloverControl` |
| Yellow lanes | Both banks implement entry/exit rollover state and 0.1-second exit debounce. Crossing an already-lit lane toggles it off, matching 3D Pinball mode. Flippers rotate the indicators. Completing 1/2/3 flashes for five seconds and upgrades the relevant bumper bank. | `TRollover.cpp`, `ReentryLanesRolloverControl`, `LaunchLanesRolloverControl`, left/right flipper control |
| Bumpers | Four levels, six-frame firing pose, threshold-gated impulse/score, one-level decay every 60 seconds after upgrade. Attack scores 500/1,000/1,500/2,000; launch scores 1,500/2,500/3,500/4,500. | `TBumper.cpp`, `BumperControl`, `BumperGroupControl` |

Timers advance at the runtime's 60-Hz frame boundary, using integer units of
1/120 second. Odd hold values round up to the next frame. Lane awards are
2,000 for reentry and 500 for launch. Existing exact 128-bit score accumulation
and decimal presentation are retained. The generated geometry keeps all 1,217
original edge indices in the same order; no approximate replacement walls were
added for these rules.

`game_lamp(original bitmap ID)` and `game_pose(original component ID)`
expose event-driven visuals. `game.visual_epoch` invalidates the renderer on
changes and remains monotonic across a new game. `game.sound_value` carries
the pre-increment hyperspace level or hazard completion flag. Completed lane
events restore rollover context before playing their sample.

## Validation

Run `python3 cadet/game/test_mechanisms.py` from the checkout.

The host fixture runs under AddressSanitizer and UndefinedBehaviorSanitizer.
Its 216 assertions cover both lane banks, rotation/toggling/completion/decay,
both actual swept kickback contacts and boost/reset/gate rules, hazard awards,
all 12 entry/destination wormhole combinations, replay persistence and drain
consumption, capture/release position/velocity/Z, isolated kickout cooldown,
five hyperspace holds/awards, gravity enable/capture, and completed-lane sound
context.

The native fixture is split into three programs so the test harness itself
fits the X16's unbanked memory: lane contracts (27 assertions), kickback
contracts (30), and capture contracts (159). Each uses the production banked
engine and is run on stock 65C02 r49 with both 512 KB and 2 MB.

Native result is recorded in `cadet/play-build/mechanisms{1,2,3}-{512,2048}.log`.
The original raw-image overlay duplication was detected by the native capture
fixture and fixed by the integrator: rules and physics overlays must be
extracted from their named ELF sections. After that packaging fix, all three native shards pass in both memory configurations: 27 + 30 + 159 = 216 assertions for 512 KB, and the same 216 for 2 MB. The host sanitizer run also passes all 216 assertions with no sanitizer findings.

## Known unfinished fidelity work

- Hyperspace's drain blocker, extra-ball lamp/award branch, reflex-shot window,
  mission awards, accumulated jackpot/bonus flags, and multiball are not
  implemented by this subset. Its jackpot tier currently uses the original
  initial 20,000. The game's general multiplier/mission system remains incomplete.
- Destination-target selection is implemented. Spinner destination changes
  currently occur on contact; the original spinner's repeated timed bitmap
  steps and full-rotation callback are not reconstructed yet.
- Original throw-angle/speed random variation is not reproduced; releases
  use the deterministic DAT direction and speed.
- Lamps use a shared integer blink phase. Source event durations and poses
  are connected, but independent per-lamp DAT on/off delays and phases still
  need reconstruction.
- Hyperspace tiers 1/3/4 and gravity-well control cues are not resident in the
  present 512-KB audio allocation. Their hold durations follow the source WAVs;
  they must not be described as complete original audio.
- Drain/reset behavior here supports the implemented single-ball rules.
  Original launch skill shot, ball-save/bonus/multiball/mission interactions
  need further work.
- These fixtures establish specific mechanism contracts, not visual fidelity,
  a sustained frame-rate guarantee, or completion of the whole original game.

## Final 128-bit boundary regression

After the large-award preflight fix, the complete 216-assertion mechanism
suite was rerun successfully on the sanitized host and native 512-KB/2-MB
configurations.

`python3 cadet/game/test_large_award.py` additionally exercises the real
hyperspace capture wrapper at the unsigned 128-bit score limit. It verifies
that a 150,000-point award overflowing by one point or by 50,000 preserves
all 16 score bytes and 40 decimal digits, while an award reaching the exact
maximum succeeds. Subsequent scoring after overflow stays unchanged.
The host passes 29 assertions with ASan/UBSan; each native configuration
passes 32, including three assertions that the production overlay wrapper
restores the previous RAM bank. Logs: `large-award-host.log`,
`large-award-512.log`, and `large-award-2048.log`.
