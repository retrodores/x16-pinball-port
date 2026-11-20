# X16 Pinball Attract Fidelity Preview

Choose Space Cadet X16 or Space CmdrX16. The 512 KB ZIPs use the
standard soundtrack. The 2048 KB ZIPs use GTR3QQ's native stereo cover.
Extract one ZIP into its own folder. Put x16emu.exe and its matching
rom.bin in the parent folder and double-click RUN-WINDOWS.bat.

- Both panes use the proportional PBMSG_FT glyphs from the Windows
  executable. Player 1 is above the status pane. Score and BALL retain
  their separate number sprites.
- The center rings sparkle when a game starts and indicate rank progress,
  Target Practice and Launch Training. Later missions and jackpot effects
  remain incomplete.
- Demo flippers react independently when the ball crosses an approach
  edge. They hold, release, and wait for a new approach. The demo uses the
  same serving and ball-drain states as live play.
- The 2 MB cover measured about 6 dB lower in matched music windows.
  The isolated flipper cue was essentially unchanged. Matched 512 KB
  windows showed no material change in the tested music and feed effect.

Linux r49 tests used stock 65C02 at 8 MHz. Both editions were checked
from fresh extracts. The Windows launcher was reviewed but Windows
execution remains unverified. The frame-cycle budget is still exceeded
during play. See VALIDATION.json for actual test coverage and measurements.
This is a development preview.

The 2 MB ZIPs credit Matt Ridgeway and GTR3QQ. See MUSIC-CREDITS.txt for
the cover's CC BY-SA 4.0 license and modifications. The engine's license
and attribution are in the runtime ZIP alongside the engine specifications.
