> Historical review of the pre-milestone build. The subsequent 0.3 development
> implementation and current results are in STATUS-0.3-WIP.md and RESUME.md.
> Its original findings remain evidence; the missing-feature status below is
> intentionally retained as a dated record, not the current implementation list.

# CmdrX Cadet: OBS comparison and first flipper correction

Review: Codex, with Brett Estrade. Session date: November 18, 2026 (America/Chicago).
This is a development review and source patch, not a new recommended game release.
Original Table 0.2 remains the accepted playable build.

## Evidence

- Original recording: `2026-11-17 22-59-31(1).mp4`, 83.817 seconds, 1920x1080/60, stereo audio.
- Port recording: `2026-11-18 23-02-35.mp4`, 124.517 seconds, 1920x1080/60, stereo audio.
- Input checksums and supplied timing log are in `input-evidence.json`.
- Sampled overview frames and closer sequences around the wormhole were inspected. This is not a frame-by-frame verification of both entire recordings.
- Original code oracle: the unchanged recovered C++ under `direct/vendor/SpaceCadetPinball`.

## Findings

| Report | Confirmed cause or remaining question | State after this patch |
| --- | --- | --- |
| Silent right-side trap | The mid-right sink is a wormhole. `TSink` uses SoundIndex4 on entry and SoundIndex3 on return; both resolve to SOUND43.WAV. The resident sample list excludes SOUND43, and the generic contact mapper ignores sound3/sound4. The port also suppresses its generic return sound after a capture. | Diagnosed; audio routing and resident sample storage remain to implement. |
| Awkward trap behavior | The port applies a generic capture timer, returns from the same metadata entry and disables all wells/capture contacts for 0.75 seconds afterward. Original WormHoleControl selects an exit according to destination state and awards score; TKickout separately uses a 0.05-second reset. The original mechanisms must be kept distinct. | Not corrected by this patch. No new claim of faithful capture physics. |
| Left-side plunger never catches/fires | This is the left kickback. Original TKickback waits 0.7 seconds, enables its impulse, then uses a 0.1-second reset and closes its gate. The port has no kickback state machine. Its gate is never opened by completing the hazard targets. SOUND17 is also absent from the resident samples. | Missing mechanism and rule confirmed; not implemented. |
| Yellow 1/2/3 lights do not count | The renderer does not read table lamp state. Additionally, generic Sensor handling does not implement original paired rollover entry/exit faces or the three-lane completion/bumper-upgrade rules. | Missing logic and rendering confirmed; not implemented. |
| Bumpers do not animate | Packed sprites cover flippers, main plunger, ball and digits. No bumper animation frames are drawn. Current flash/boost interval is 8/120 sec; the original bumper firing interval is 0.1 sec, with rest/fire poses at four levels. | Missing animation and level state confirmed; not implemented. |
| Ball appears over purple ramp | Accepted 0.2 draws the ball over the artwork. The unreleased 0.3 checkpoint has static original depth-map masking. A visual overlap alone does not prove a collision-layer crossing; layer transitions need explicit route tests. Dynamic sprite depth remains unfinished. | Static masking exists only in WIP; not a new fix from this review. |
| Flipper tips stick or produce odd shots | Reproduced a precise defect: `paddle` passed an active flipper impulse into a wall rebound helper, which immediately returned when inward velocity was zero or negative. Original TFlipperEdge/math code applies a powered impulse in this case. | Corrected this defect, with host and native regression fixtures. Swept-tip geometry and other reported odd shots still need comparison. |
| Main launch plunger animation hard to see | The main plunger already has eight poses, separate from the side kickback. Its code and existing UI check should not be confused with the missing kickback mechanism. | No animation change in this patch. |

## Audio matching

The converted SOUND43 waveform correlates strongly with the original recording near 20.342, 22.316, 56.148 and 58.145 seconds (normalized correlations 0.70–0.74). The latter pair is about two seconds apart and corresponds to the sampled wormhole sequence. No similarly strong match was found in the port recording; source inspection establishes that this sample cannot play because it is absent.

`audio-matches.json` retains the measured candidate peaks. Correlation is supporting evidence, not a generic sound-event classifier: similar short mechanical effects can cross-match, so the weak SOUND17 peaks are not proof that a kickback fired. No acoustic identity or note-perfect soundtrack claim is made.

## Timing

The user's log is hexadecimal. `000263bb` means 156603 cycles, or 19.575 ms at 8 MHz. Its frame number `00001905` is 6405, beyond the existing 6000-frame scripted run; the human inputs also differ. The strict 133333-cycle limit is retained. Longer tests and input replay should supplement the current script. Removing rare overruns alone would not complete the missing table mechanisms.

## Correction scope

Only the powered-flipper contact response is changed. For stationary or outward-moving balls on the powered front face, apply the original-style speed loss and normal impulse. Passive contact still adds no energy. Both sides are tested with stationary, slowly outward-moving, and passive stationary contacts. The test fails on the prior code (eight failed assertions) and passes with the correction. It exercises production `engine.c` directly.

The original accepted release and vendor source are untouched. The prior source checkpoint is commit `2e96b8709ba67785bcd5b8a88d5b7e1c803c7e89`.

## Validation

Host sanitizer regression: all six contact cases pass. Forty three-ball games: 120 drains, zero escapes, zero stalls; 532 bumper hits, 947 flipper hits, 453 ramp entries, 100 returns, nine five-contact guard uses. Optimized and exhaustive 1217-edge searches both produce state hash `768b50ac`. The changed hash versus the previous checkpoint is expected because powered flipper behavior changed. The nine guard uses need continued observation; this is not complete physical-fidelity validation.

Powered/passive contact fixtures pass on native 65C02 with both 512 KB and 2048 KB. Native/host trajectories match at 50 checkpoints in both configurations. Exact arithmetic, depth quantization, pixel compositor, bounds and four full music-stream comparisons pass. The interactive emulator UI test passes (including the main plunger and flippers); captured audio RMS is 3739.49, peak 24624, 879060 samples.

| RAM | Frames | Worst cycles | Mean cycles | Over 133333 | Music errors |
| --- | ---: | ---: | ---: | ---: | ---: |
| 512 KB | 6000 | 158182 | 40526 | 3 | 0 |
| 2048 KB | 6000 | 158318 | 40526 | 3 | 0 |

Both integrated budget checks still FAIL. Worst measured time is 19.790 ms; the changed trajectories reach a worse maximum than the prior checkpoint despite fewer overruns. No new 2 MHz claim. The separate music-start/restart prefill hitch is unchanged and outside this script. This patch is not a release candidate.

## Next implementation order

1. Complete source-derived capture/return and kickback/gate fixtures, including legal exit routes, sounds and reset timing.
2. Implement hazard and lane state machines; connect original yellow indicators, bumper poses and gate/kickback graphics to those states.
3. Validate the ramp underpass and flipper-tip sweeps with controlled placements and original-video landmarks.
4. Resolve timing spikes, including music restart, and rerun longer integrated play tests before promoting a release.

Do not add random decorative lamp flashing: lights must report actual rules, awards and timer states.
