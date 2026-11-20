# X16 Pinball Attract Preview 1

Includes complete runtimes for Space Cadet X16 and Space CmdrX16. Each has
all 30 game files, a Windows launcher, and the human- and machine-readable
engine specification snapshot. Extract each edition to its own folder. Put
`x16emu.exe` and its matching `rom.bin` in the parent folder, then run
`RUN-WINDOWS.bat`.

- Press **F3** or let a fresh table idle for about **15 seconds** to start the
  demo. Watch it play through the bumper and ramp objectives and restart.
- Press **F2** or a play control to take over. **M** toggles music.
- Effects led music by about **14 dB** in the measured test scene.

Both editions passed Linux emulator UI tests at 512 KB and 2 MB. The
Windows launcher was checked as a packaged file. Its execution on Windows
has yet to be tested.

The 12,000-frame benchmark exceeded the **133,333-cycle** budget on
**70 frames** at each RAM size. The worst frame took **212,845 cycles**.
The preview uses the existing gameplay lamps and its own demo objectives.
See VALIDATION.json for the test results and PACKAGE-MANIFEST.json for file
hashes.
