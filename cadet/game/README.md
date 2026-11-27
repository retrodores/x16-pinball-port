# CmdrX Cadet development checkpoint

For the public 1.0 editions and the exemplar, use the
[1.0 build and handoff](../../docs/release-status/v1.0/HANDOFF.md). This page records earlier checkpoints.

This source tree is work toward 0.3, not a new accepted release. Read
../STATUS-0.3-WIP.md and ../RESUME.md. The integrated 8 MHz performance gate
still fails on five of 6000 scripted frames at both supported RAM sizes.

The accepted 0.2 instructions are preserved in README-TABLE-0.2.md.
Its original assets remain at /opt/cmdrx-cadet-table02-assets.
Do not label the current play-build binaries as the accepted 0.2 release.


## Spinner preview

Both flag spinners use the directed crossings and their installed eight-pose
data. The integer timer keeps scoring and wormhole rotation independent of
which poses VERA can show at 60 Hz. Spinner steps within the same video frame
share a PCM cue. A spinner tick lets its audible transient play before
retriggering the same sample. The opening red X overlays the upper blue insert (lite77) with its own sprite so a flash can coexist
with an active slingshot.

Keep the executable with its matching PHY, RUL and MEC overlays. The MEC
overlay begins at B608 in bank 10, beyond the depth index. RINGS2.BIN starts
at BA00 in bank 11, beyond the UI and projection data. Both ranges fit the
512 KB configuration. The preview also supports the 2 MB cover soundtrack.

Flag boost, Time Warp, skill-shot rules, the drain blocker and two independent
status queues remain open. See the preview validation for the frame budget.


### Table controls

Up Arrow nudges the table. Three distinct presses within three seconds
trigger tilt, with a half-second pause between accepted nudges. The upper
X flashes, scoring is suspended, and the flippers are inactive until the
next ball. The first three drop targets award a four-second spinner boost
that triples the normal spin award. The upper window reports these events
and wormhole captures. The lower window continues to show an active mission
even while the ball is held.

Press Q or Escape to quit to BASIC. The compact soundtrack needs at least
512 KB of banked RAM. The full cover soundtrack needs 2 MB. The game
checks before loading any assets. The r49 emulator can run the same PRG
with either -c02 or -c816 at 8 MHz.
