# X16 Pinball Quick Reset Preview

F2 clears the old ball and message panes and draws the first lamp changes
on the first update that handles the keypress. The engine gives the display
a frame to present those changes before reading the opening sound bank.
F2 keydown is latched so a brief tap is available to the game even when
a previous frame takes longer to finish.

The opening uses the supplied SOUND1 sample and the same lamp sweep as
the Opening Show Preview. The sound still waits for the bank read.
F2 skips an active opening and F3 enters the demo. The 512 KB edition
uses the standard soundtrack. The 2 MB edition uses Cover Balance.

Each runtime includes RUN-WINDOWS.bat. Put x16emu.exe and the matching
rom.bin in the parent folder. See VALIDATION.json for the measured
emulator response times. Windows, hardware storage latency, and extended
frame timing remain unverified.
