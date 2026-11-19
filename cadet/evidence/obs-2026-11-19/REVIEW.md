# OBS follow-up: slingshots and launch audio

Review of the user-supplied 2026-11-19 00-37-20.mp4 against the prior original-game recording and recovered source. This document records observations from the submitted build, before the follow-up corrections. It is not a claim that the new build has been visually verified.

Input: 55.133333 seconds, 1920×1080, 60 fps, 48 kHz stereo AAC.
SHA-256: 5538741917baddb21fb46ef5736889864cc225ae20be1d21744a5bc5611652d1.
Original comparison: 2026-11-17 22-59-31(1).mp4, SHA-256 732d9350f20403c1d5d173c41cf500d3448d63ca14676a5a42d68ba00ff85405.

## Concrete observations

| Recording/time | Observation | Interpretation |
| --- | --- | --- |
| New port, about 37.72 s | Ball approaches the upper inner face of the left triangular slingshot and reverses toward the right. No bright rubber or triangle-light pose appears through 38.0 s. | Confirmed missing slingshot animation on a visible contact. See slingshot-left37.4.jpg. |
| New port, about 41.95 s | Ball moves down the right triangular slingshot, then kicks sharply left between 41.950 and 41.967 s. Score changes from 78000 to 78500. The triangle remains unchanged through the following 0.1 s. | Confirmed qualifying slingshot event without its visible animation. See slingshot-41.85.jpg. |
| Original, 12.833–12.900 s | Right slingshot shows bright curved striking rubber and stronger white lightning inside the triangle. | Direct visual target for the port. |
| Original, 13.050–13.133 s | Left slingshot shows the corresponding rubber and triangle glow, then returns to the ordinary table image. | About six captured frames, consistent with the source 0.1-second timer. See original-slingshots12.8.jpg. |
| New port, 7.917 / 8.117 / 8.133 s | First visible pulled plunger pose / snap back / ball moves up the launch lane. | Release timing is directly visible. First visible pose is not necessarily the key-press time because there are only eight poses. See plunger-7.8-detail.jpg. |
| New port, approximately 15.3–17.1 s | One capture/return UI interval. | The hold and 10000 award are consistent with the first hyperspace kickout; do not label this a verified wormhole event without event telemetry. |
| New port, 52.6–54.2 s | Next-ball transition, followed by serving until clip end. | No second visible launch occurs before the recording ends. |

Times are video presentation times. Individual contact boundaries are limited by the 60-fps capture. Low-rate UI scans are only accurate to approximately 0.1 s.

## Recovered source requirements

The triangular mechanisms above the flippers are TWall groups 469/470, not the round TBumper components.

TWall.cpp hides its extra bitmap at rest (SpriteSet(-1)). A successful DefaultCollision shows bitmap 0 and starts a 0.1-second timer; expiry hides it. A later qualifying collision restarts the timer. Unlike TBumper, TWall does not suppress its boost during the animation interval.

TCollisionComponent.cpp only reports a qualifying control collision when inward/projected speed is greater than the component threshold. Recovered slingshot data has threshold 1, boost 18, elasticity 0.6 and smoothness 0.95. Lower-speed contacts must not automatically fire the slingshot animation or score.

control.cpp FlipperRebounderControl1/2 also turns on the associated triangle lamp (lite84/lite85, bitmap groups 180/181) for 0.1 s and awards 500 points. Both the wall strike bitmap and lamp are needed to match the visible original effect.

TPlunger.cpp plays its HardHit sound once on a new press, SoundIndex3 once on release, and SoundIndex4 for ball-feed timing. It does not retrigger a sound for every charge increment. Recovered DAT parameters are increment 1, maximum 100, 25-ms pullback delay and eight bitmap poses. The first increment is immediate in the original callback; release immediately restores bitmap 0 and enables the impulse for a 25-ms window.

## What this clip does not establish

The submitted clip contains one visible launch, so it cannot by itself prove intermittent plunger-sound loss across repeated launches. The user's flipper/wormhole overlap report likewise needs deliberate simultaneous-event tests. During the sampled capture interval, the flippers mostly remain at rest. Audio dispatch/mixing and waveform-rate verification are separate evidence owned by the audio tests.

The visual comparisons support the slingshot correction directly. They do not establish exact shot-angle fidelity, full audio perceptual equivalence, or a stable 60-FPS claim.

## Follow-up functional regression

After the frozen slingshot and input-event corrections, native ROUTES (254 assertions), TIP (10 assertions) and powered/passive contact fixtures pass at both 512 KB and 2 MB. Optimized and exhaustive 40-seed ASan/UBSan host soaks match exactly at hash 689df8e0: 117 drains, zero escapes/stalls, 928 bumper hits, 918 flipper hits, 518 ramp entries, seven collision-guard hits and 293 returns. Runs stop at GameOver or 18000 frames; not every seed completes a game. These are functional/index-equivalence results, not integrated performance or post-fix visual/audio acceptance. Source hashes and counts are in physics-results.json.
