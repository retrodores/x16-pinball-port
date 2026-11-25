CAROL OF THE BELLS | SPACE CMDRX16 | ROCK AUDITION 1
Standalone Christmas music for the Commander X16

Windows: place x16emu.exe and its matching rom.bin together. Create an audition
folder directly underneath them, extract the entire ZIP into that folder, and
double-click RUN-WINDOWS.bat. All music and playback files are included.

Commander X16: copy AUDITION.PRG, CAROL.ZSM and ZSMKIT.BIN into one directory,
then from BASIC in that directory enter LOAD"AUDITION.PRG",8,1 and RUN.
The audition is designed for the stock 65C02 at 8 MHz with 512 KB or more.
Q or Esc stops the music. It also returns to BASIC at the end.
Any compatible ZSM v1 player with stereo PCM instrument support can use CAROL.ZSM.

Listen in stereo. The opening repeated bells gradually assemble into the main
figure. The first full-band entrance is around 0:39, the breakdown around 2:08,
and the band returns around 2:30. Let the final E-major chord ring.
The YM2151 plays the bells, left and right rhythm guitars, picked bass, lead,
keys and strings. The VERA PSG supplies bass, bell echoes, string and guitar
layers. The VERA PCM track uses a newly synthesized stereo drum kit.

Credits
Based on Shchedryk by Mykola Leontovych. Musical reference for this instrumental
arrangement: Mannheim Steamroller's recording of Carol of the Bells supplied by
the project owner. The ZSM uses new chip patches and newly synthesized drum
samples. The master recording is not included. Pitch analysis used Spotify's
Basic Pitch. The standalone player uses ZSMKit by mooinglemur:
https://github.com/mooinglemur/zsmkit
The enclosed ZSMKit MIT notice applies to that playback library.

This is a music audition independent of the pinball releases. Game effects,
playfield lamp synchronization, and physical X16 playback are outside its tests.
