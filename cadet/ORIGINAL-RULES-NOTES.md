# Original rule findings — not yet integrated

Codex, 2026-11-18. Oracle: unchanged direct/vendor/SpaceCadetPinball at upstream
cb9b7b886244a27773f66b0b19fdc2998392565e. Recheck the named handlers before coding
fixtures. These are implementation notes, not claims about current gameplay.

- TPopupTarget disables on a hit above its threshold and hides its sprite.
  TPopupTargetEnable waits 0.25 seconds before restoring it. Reset restores it
  immediately. Groups 432..440 are the nine drop targets. Current engine's
  individual ten-second reset is incorrect.
- BoosterTargetControl: targets 1..3 give 500 for the first two and 5000 for
  completing the bank. Successive completions enable flag lights, jackpot,
  bonus, then bonus hold; once all are enabled there is an additional award.
  Reset all three through the 0.25-second mechanism.
- MedalTargetControl: targets 4..6 give 1500 initially. Bank completions progress
  10000, 50000, then extra ball. Medal level decays after 30 seconds.
- MultiplierTargetControl: targets 7..9 give 500 initially, completion 1500 at the
  OLD multiplier, then advance multiplier index (values 1,2,3,5,10). Decay 30 s.
  Never narrow multiplied awards to uint16 or compromise the 128-bit total.
- Fuel targets 10..12: 750, lights 70..72. Individual lights flash two seconds
  then stay lit; completing all three refills fuel and flashes then clears them.
- Mission targets 13..15: 1000, lights 101..103, individual two-second flash then
  lit, all-three two-second flash then clear.
- Hazard targets 16..18 (groups 454,456,458) score 750 and light 104..106.
  Complete them to open gate 1. Targets 19..21 (460,462,464), lights 107..109,
  similarly open gate 2. Completion lights flash two seconds then clear.
- Target 22 (466): 750 and wormhole destination advance.

TRollover has two sets of directed faces: 600 uses ActiveFlag, 603 uses
RolloverFlag. The first crossing scores and switches RolloverFlag on; the second
crossing disables ActiveFlag for 0.1 s and clears RolloverFlag, then its timer
re-enables it. Current engine incorrectly ignores the initially inactive mirrored
faces. Do not apply this state machine to TTripwire simply because both are
currently represented by Kind Sensor.

ReentryLanesControl: roll3 -> lite8, roll2 -> lite9, roll1 -> lite10; initial
award 2000. Crossing an unlit lane lights it; crossing a lit one clears it in
3DPB mode, unless the group is flashing. Complete all three to flash/clear for
five seconds and raise attack-bumper level. Levels 0..3 score 500/1000/1500/2000.
Bumper group level decays after 60 seconds, one level per timer interval.

LaunchLanesControl: roll110/111/112 -> lite169/170/171, initial award 500;
same three-light mechanism raises launch bumpers. Their level awards are
1500/2500/3500/4500. Each new completion resets the 60-second decay timer.

TBumper has eight original poses: rest/fire for four levels. Its fire interval
is 0.1 seconds (DAT 407 for groups 372,380,388,396,405,413,421). Threshold is
temporarily raised while fired. Current flash/boost interval is only eight
120-Hz units and needs correction together with sound/award threshold behavior.

TGate groups 501/502: Reset/Enable => active and sprite 0; Disable => inactive
and hidden. Gate closure is tied to its kickback reset, not a guessed short timer.
TKickback groups 505/507: first contact starts a 0.7-second arming timer with
large threshold; then threshold becomes zero for the boost phase, a 0.1-second
timer, sprite 1 and sound. Boosted contact clears its active state. The following
timer restores sprite 0 and re-enables the corresponding gate.

Skill shot: plunger one-way enables five-second shoot-again. Trip1..5 add
lite68,69,131,132,133 while lite67 is on. Escape one-way 4 awards by active count:
15000,30000,75000,30000,15000,7500. Deployment one-way 10 clears the skill lights.
Read the original control handler for all lamp-reset/reflex details before porting.

Normal AddScore accumulates unmultiplied bonus/jackpot values (capped at 5M),
then multiplies the displayed award by 1/2/3/5/10. SpecialAddScore bypasses that
behavior; read it before implementing special awards. Initial bonus is 10000;
normal drain resets it to 25000 unless bonus hold. BallDrain also handles
shoot-again, extra balls and resets component/lamp/multiplier state. Those rules
and the full mission machines are still missing.

Rendering provenance:
- proj::z_distance is sqrt(cx*cx+cy*cy+cz*cz), NOT camera cz alone.
- NormalizeDepth uses (distance - 19.5013065338135) * 4303.9697265625.
- The original zdrv flat painter keeps a ball pixel when table z > ball z.
- Group 107 depth data: 365x470, stride 368 uint16, bottom-up, 14-byte header.
- This checkpoint stores the high byte of each original depth sample, preserving
  all 171550 quantized samples. It does not reproduce the complete 16-bit map.
- Dynamic sprite depth maps (bumper/flipper etc.) still need their own integration.

Useful visual groups: seven bumper bases above (eight consecutive frames each);
drop targets 432..440; gates 501/502; lane lamps 128..130 and 214..216;
hazard lamps 185..190; skill lamps 173..175 and 193..195.
