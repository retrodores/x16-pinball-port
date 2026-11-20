# CmdrX Cadet development checkpoint

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
