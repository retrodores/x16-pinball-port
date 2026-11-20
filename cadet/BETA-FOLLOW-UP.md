# 1.0 Beta follow-up

## Music-forward and purple panel refresh

The music converter adds 9 dB to the previous melodic settings and retains
the previous percussion setting. The PCM volume register is lower. PCM
sample bytes, note timing, and audio rate are unchanged. The matched
music-only and effects-only scenes measured a 5.60 dB music lead at 512 KB
and a 5.63 dB lead at 2 MB.

Play-state messages and the music indicator now choose a purple sprite
palette. The score and ball counter already use purple numerals. The
controls remain a static guide. Both editions passed extracted-runtime
smoke tests for purple text and visible transitions in each of the four
new-ball gate lamp regions.

### Lamp and timing work still open

- Audit lamp coverage and event hooks for the missing rules, including
  mission objectives and bonus or special-mode effects.
- Distinguish rule timing from rendering latency. The current rules share
  a six-update blink phase. Test activation, on/off cadence and expiry per
  lamp, then test the rendered states with simultaneous lamps and high
  frame load. The VERA updater limits patch bytes per frame.
- Finish the status presentation. Message size, independently timed
  announcements, and the mission/objective panel remain open.
- Split the worst native frame into physics, interrupt and rendering
  contributions. The earlier narrow probe found about 184000 cycles
  elapsed before display on frame 9424, including interrupt work.

## Initial 1.0 Beta follow-up

This earlier development work starts from `c13fbaa`.

## Audio and outlane validation

Rebuild the louder music with `python3 cadet/build_music.py`, then
`python3 cadet/game/pack_music.py`. The first step uses the local MIDI input
documented by the converter. The converter lowers YM2151 attenuation by
eight steps and doubles the VERA percussion amplitude target. The note ledger
and PCM files are byte-identical to the baseline. ZSM packing still fits 13
banks and retains the same number of writes. Playback still uses the existing
native player.

The r49 short audio capture raised music-only RMS from about 415–417 to
831–834 across 512 KB and 2 MB. The combined audio checks exercise the table,
plunger, flippers, and music in the same recording. The combined scene
peaked at 23552 of 32767 on both RAM sizes. A separate native fixture
completed one soundtrack loop with concurrent effects, zero decode errors,
and zero PCM underruns at each size. Both cabinet variants
passed Linux UI smoke tests at both RAM sizes in fresh extractions with the
new music banks. Windows launcher execution was outside these checks.

The continuous outlane fixture starts once above each outlane's rollover and
runs ordinary frame updates until the ball takes a powered return and the
gate closes. Both shots passed on the host and stock 65C02 at 8 MHz with both
RAM sizes. The old fixture still independently covers each timer and hazard
bank reopening. These are two demonstrated return trajectories, not evidence
that all approaches behave correctly.

## Frame budget and remaining behavior

The default deliberate-shot build exceeded its software stack reservation.
The test-only placement setup now lives in the physics overlay, preserving
the 1 KB linker guard, all 19 placements, and the 133333-cycle test threshold.
The rebuilt release PRG, rules overlay and physics overlay match the current
Beta ZIP byte for byte. The ordinary (non-deliberate) 12000-frame run still
failed the timing gate on both RAM sizes.

The deliberate harness used stock 65C02 at 8 MHz in r49 Pyrite
(`af102408`). Its ROM SHA-256 is
`b81654cc8c87ed96e3ffc7c8e7c312c9f3b7b870c7bb34de61e61eac931b819a`. Only the two music banks differ between the
512 KB baseline and gain runs.

| Music | RAM | Worst cycles | Mean cycles | Over 133333 |
| --- | ---: | ---: | ---: | ---: |
| 1.0 Beta | 512 KB | 212925 | 68786 | 70 |
| Louder | 512 KB | 212873 | 68790 | 70 |
| Louder | 2048 KB | 212859 | 68788 | 70 |

All three runs completed 12000 frames with zero music errors and PCM
underruns. The worst frame was 9424 in each run. These results do not
isolate its cost to a specific subsystem. A temporary narrow timing probe
reproduced a 212941-cycle frame at the same position, with 183599 cycles
already elapsed before display and 29342 after that point. The first
measurement also includes interrupt work. The detailed profile build still
exceeds unbanked memory with the software-stack guard enabled.

The source audit separates several visible symptoms:

- The X16 ramp event updates collision routing, while the reference's mission
  controller also checks mission selection and fuel, dispatches an award, and
  updates the objective. The two timed reference panels have no equivalent in
  the current X16 state-label and control-guide UI.
- The Windows engine-upgrade message comes from a launch-bumper upgrade. The
  wormhole-open message has its own trigger. Either can appear alongside
  unrelated text in the mission panel.
- The X16 lamp path runs from rule state through packed graphics to
  budget-limited VERA writes. Shared blink phase, missing lamp coverage, and
  delayed writes are separate questions. The UI smoke test checks observable
  gate lamp changes.
- Outlane gates, wormhole sinks, and the hyperspace drain blocker are different
  devices. The blocker is absent from the current hyperspace rules. The exact
  full-table light sequence in the recording has not been identified.
