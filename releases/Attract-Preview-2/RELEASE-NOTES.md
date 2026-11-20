# X16 Pinball Attract Preview 2

Two complete runtime ZIPs are available, one for Space Cadet X16 and one
for Space CmdrX16. Both include the 30 game files, the Windows launcher,
and the human- and machine-readable engine specification snapshot.
Extract each edition to its own folder. Put the matching x16emu.exe and
rom.bin in the parent folder, then run RUN-WINDOWS.bat.

- Press F3 or let a fresh table idle about 15 seconds to start the demo.
  Press F2 or a play control to take over. M toggles music.
- The music leads effects in the measured audio fixture.
- Large purple dot-matrix text covers live status and the demo objectives.
  The controls guide remains in place.

The runtime includes audio fix 317af0b, message renderer c94bd6a, and the
integration fixes recorded in PACKAGE-MANIFEST.json. The integration
places the font in an unobstructed VERA region and keeps the CPU stack
reservation. The PRG and both overlays come from one build.

Both editions passed from fresh ZIP extractions at 512 KB and 2 MB.
The audio fixture measured the music lead and completed one soundtrack
loop with concurrent effects at each RAM size. The Windows launcher is included as checked package
content. Emulator gameplay tests ran on Linux.

At 512 KB, 71 of 12,000 frames exceeded the 133,333-cycle budget. The worst frame took 212,978 cycles.

At 2048 KB, 70 of 12,000 frames exceeded the 133,333-cycle budget. The worst frame took 213,072 cycles.
