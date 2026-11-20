# X16 Pinball Backbox Preview

The Space CmdrX16 artwork now fills the cabinet opening. Both themes
share the same red BALL lettering, counter box and cabinet trim. The
update uses the existing artwork and score display.

The 2048 KB packages use the GTR3QQ native soundtrack, measured about
3.9 dB below the previous preview in matched emulator captures. The
isolated flipper effect level was essentially unchanged. The 512 KB
music banks are byte-identical to those in the previous preview.

Extract the chosen ZIP and put x16emu.exe and its matching rom.bin in
the parent folder. Double-click RUN-WINDOWS.bat. All game assets,
licenses and engine specifications are included.

Both themes passed fresh-extraction tests on the Linux r49 emulator
at 8 MHz. Windows launcher execution remains unverified. This is a
development preview. See VALIDATION.json for the scope of testing.

## Rebuild

From the packaging source tree, first prepare the cover banks from the
local Pinball_R6.zsm. Then build the ZIPs from the pinned prior preview.

```sh
python3 cadet/game/pack_music_cover.py /path/to/Pinball_R6.zsm /tmp/cover-banks --extra-db 4
python3 packaging/build_backbox_preview.py releases/Attract-Fidelity-Preview /tmp/cover-banks /tmp/backbox-preview c13635c99d3f29e2652a5b1aa9f7c9eb5b720d71
```
