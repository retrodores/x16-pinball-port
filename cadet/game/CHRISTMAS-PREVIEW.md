# Space CmdrX16 Christmas: Carol of the Bells

The playable 1.0 Beta loads the same 209,321-byte CAROL.ZSM as the standalone
rock audition. The score contains eight YM2151 parts, sixteen VERA PSG parts,
and a synthesized stereo drum kit. The game includes its own ZSM reader and
mixes table, flipper and plunger effects into the shared VERA PCM FIFO.
The stock target for the combined game remains the 8 MHz 65C02 with 2 MB
of banked RAM. A standalone music player can use less RAM.

The Christmas-only runtime loads the unmodified ZSM beginning in bank 80;
bank 64 holds the holiday renderer, lighting timeline and drum gain tables.
The ending runs to the end of the 13,960-tick score, then the game repeats.
F2 restarts an enabled score. M turns music off or restarts it. The light
show uses the current song tick, and gameplay signals retain priority.

The finished playfield uses candy-striped flippers, a polished bauble ball,
a brass-and-green plunger and peppermint rims on all seven pop bumpers.
The stripes follow the flipper angle from the hinge to the tip. Each bumper
keeps its original center jewel as it advances through four levels and
flashes on impact. The packer draws into the existing 4bpp patterns before
play. All of the sprite silhouettes, pose origins and tile allocations are
preserved.

## Rebuild the playable ZIP

Use the beta toolchain with the existing matching model, dynamic and runtime
headers in cadet/play-build. Supply the tested standalone CAROL.ZSM with SHA-256
`f4cc99564f3a0a23367c22b0d24d7b04a17b8bf950fe01d6b29508de650c57a9`.
The arrangement generator and player are in the
[christmas-rock-audition branch](https://github.com/retrodores/p8inball/tree/ac6831db564a2c349670118e37350afd3646f80b/tools/music-auditions/carol-rock).
The ZSM is included in the playable ZIP and can be extracted from it for a rebuild.
Use the original 2 MB Space CmdrX16 release pinned by the packaging script.

```sh
python3 packaging/build_christmas_preview.py headers /opt/spacecadet-x16-analysis/evidence/inventory.json --song /path/to/CAROL.ZSM
CADET_CHRISTMAS=1 CADET_BUILD_PLAYER_ONLY=1 python3 cadet/game/build_native.py
python3 packaging/test_christmas_art.py
python3 packaging/test_christmas_playfield.py
python3 cadet/game/test_christmas_carol.py
python3 cadet/game/test_carol_lamps.py --native cadet/play-build/CAROL.ZSM
python3 packaging/build_christmas_preview.py package /tmp/SpaceCmdrX16-Christmas-1.0-Beta-2MB.zip
```

Each archive has the launcher, PINBALL.PRG, overlays, full song, other assets,
engine specifications and credits at their runtime paths. The ZSMKit binaries
from the standalone audition are not required. This is a private playtest.

## Finished Christmas table playtest

Playable source `b080750ca5bcac0324bcb1af34969cd776d5671c`.
ZIP SHA-256 `577e2683e9e6496226077f6d64b22ef38ab6a23545deb0b9601c08dcd42279af`.
A fresh source export, base headers and the ZSM from the playable reproduced
the ZIP byte for byte. The root launcher checks all 35 runtime files.

| Linux r49, 65C02 at 8 MHz and 2 MB | Game frames | Frames over 133,333 cycles | Peak cycles | Song loops | Drum triggers |
| --- | ---: | ---: | ---: | ---: | ---: |
| Demo through the complete song | 13,965 | 1,337 | 630,110 | 1 | 563 |
| Demo takeover, F2, launch, flip, mute, resume and Q | 2,852 | 26 | 640,721 | 0 | 0 |
| Cold start to idle demo | 3,313 | 196 | 644,828 | 0 | 83 |

All runs reported zero music errors and zero PCM underruns. The recorded
opening bell returned at 233.646 seconds in the full-loop run. The actual
Windows r49 batch launcher passed under Wine 11.22, including a missing
score and missing ROM. Native Windows and physical X16 remain untested.

Both RAM configurations passed the native suite and returned to BASIC
for a second program. The Christmas game requires 2 MB. The art checks
covered the original transparent pixels, shapes and anchors of 31 moving
sprite poses and the live centers of 56 bumper poses. Collision, rules,
music and lamp code are byte-identical to the earlier Carol Rock playtest.

## Earlier Carol Rock playtest

Playable source `fbb8e6c5c6330b902c097699e48dec0bb31d88b3`. The 44-entry runtime ZIP contains 35
launcher-checked runtime files. The Windows launcher, specs and licenses are
included. An independent rebuild from the staged ZSM produced the same archive.

| Tested download | SHA-256 |
| --- | --- |
| `SpaceCmdrX16-Christmas-1.0-Beta-2MB-Carol-Rock.zip` | `02a6711248684b01ba168fc81761592dd7bb4fe96c2e4214e9f866e8b0af4490` |
| `SpaceCmdrX16-Christmas-Carol-Rock-Gameplay.mp4` | `66450fa66befd7994974d058a2e7896cd9f5b6a0ad4624c5f9eb8d494947c865` |
| `SpaceCmdrX16-Christmas-Carol-Rock.png` | `3d9ae132435f3f37b637d8b059c00d42acba42ec5dd3356ae0bed79ac559af2c` |

Linux x16emu r49, stock 65C02 at 8 MHz, 2 MB RAM, using fresh extractions.
ROM SHA-256 `b81654cc8c87ed96e3ffc7c8e7c312c9f3b7b870c7bb34de61e61eac931b819a`.

| Run | Frames | Over 133,333 cycles | Peak cycles | Song loops | PCM drum triggers | PCM underruns / music errors |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| F3, takeover, F2, launch, flip, mute and resume | 2,854 | 36 | 430,848 | 0 | 0 | 0 / 0 |
| Unattended startup to scored demo | 3,314 | 199 | 654,889 | 0 | 83 | 0 / 0 |
| F3 gameplay through the complete 3:53 song | 13,965 | 1,315 | 630,158 | 1 | 563 | 0 / 0 |

- The raw full-demo stereo range was -32,767 to 32,766. The independent audio check counted 23 of 23,120,924 sample values with absolute amplitude at or above 32,767.
- The full demo recording uses actual 640×480 X16 scanout sampled at 15 fps against the emulated WAV sample clock. Of 3,532 captured video frames, 7 repeated the previous sample at a missed capture deadline. The MP4 uses the game's stereo WAV at original gain.
- In the manual capture, the two F2 startup waveforms correlated at 0.993 and 0.995 with the source sample. The plunger release correlated at 0.919. Flipper return correlated at 0.655 with music and 0.985 during mute. The stereo music component fell to digital zero during mute. The opening bell returned near 784 Hz on resume.
- Across 18 passages the level of the isolated stereo difference signal was within 0.20 dB of the standalone take. The timing check matched 452 drum strikes from 20.05 to 219.47 seconds, with 95% within 9.3 ms of the fitted score clock. On looping, the recording returned to the opening bell at 233.63 seconds (envelope correlation 0.997). Source sample matches in gameplay included the flipper (SOUND104), bumper (SOUND12), pop-up target (SOUND49) and rollover (SOUND8).
- The opening bells lit up to 2 scanned sites at once. The first full-band entrance near 0:40 reached 15. In the recorded full-game fan near 2:30, the screen scan detected up to 10 active holiday sites. The closing chord reached 8. These are image estimates from the gameplay video. A separate 65C02 VERA readback test drove all 31 sites, including the center and outer ring, and verified that active game signals keep their priority.
- The art converter fixed 2,838 unintended black exterior pixels and 5,412 substitutions in the title's original dark field. Its tests compare board pixels, mechanism tile addresses and display windows. The capture includes the full cabinet and snowy ground under the message pane.
- At 512 KB the complete game displayed its 2 MB requirement and returned to BASIC. At 2 MB Q returned to BASIC. Both configurations successfully loaded and ran a second PRG. The shared native regression suite passed at both RAM sizes.
- The actual batch file launched the Windows r49 executable under Wine 11.22 from an outside working directory with spaces in the parent and game paths. F3 entered a scored demo, F2 started manual play, and Q returned to BASIC, where PRINT 37*7 gave 259. A normal close returned status 0. Missing CAROL.ZSM and missing parent ROM each produced the corresponding message and status 1. Native Windows and physical X16 remain untested.
- The full game exceeds its frame budget on some frames. The cumulative statistics above keep the 133,333-cycle criterion.

## Winter Village artwork and validation

Build source `bf11ab2a2e88fd4adfcaa30a5687aa789a5a9ae5`. The Christmas-only
package adds holly and red/green faces to the existing title. Score places
alternate berry and green, the ball counter is green and each status line
has a consistent ink. The fonts retain the original glyph geometry and
stipple. The red BALL label keeps its original pixels.

The village illustration in `packaging/art/winter-village.png` is an original
generated pixel-art plate. It depicts an alpine chalet and a decorated fir,
a crescent moon, candy canes and snowbanks. The title leaves and foreground
snow crystals use native pixel patterns. The packer fits the scene into the
existing map and tile allocation. Dynamic playfield pattern addresses and
all static pixels between the outer rails compare equal to Encore.

The complete ZIP contains the same 44 filenames as Encore. The score stream,
PCM banks, startup effect, gameplay assets and font source are byte-identical
apart from the themed map, tiles, palette and score digit sprite patterns.
The executable and overlays are rebuilt together. A second build produced the
same ZIP. Reproduction checks include `python3 packaging/test_christmas_art.py`
and `python3 cadet/game/test_christmas_music.py`.

- Runtime SHA-256 `8bc82d6462d59f64a5279a2013eab263efd1048496a82a45a5b81a5226105bb9`.
- Lossless 640×480 emulator capture SHA-256 `2b9c33102fbce14cb954b650d1c6df65e058c74722ae9c31f7171984224dc781`.
- Linux x16emu r49, stock 65C02 at 8 MHz, 2 MB banked RAM, ROM SHA-256
  `b81654cc8c87ed96e3ffc7c8e7c312c9f3b7b870c7bb34de61e61eac931b819a`.

| Fresh ZIP extraction | Frames | Over 133,333 cycles | Peak cycles | Music loops |
| --- | ---: | ---: | ---: | ---: |
| Cold start, F3, Q | 2,022 | 171 | 625,376 | 0 |
| F2, launch, flipper, Q | 2,036 | 43 | 295,256 | 0 |
| Idle demo through a complete soundtrack loop, Q | 12,584 | 1,347 | 623,752 | 1 |

All three runs reported zero music errors and zero PCM underruns. The screenshot
shows the 32,500 score and DEMO panel on the second burst, with the lit ring,
two score inks and both message inks in actual emulator pixels. The original
purple face color is absent from those text regions. The 512 KB guard printed
the 2 MB requirement, returned to BASIC and ran a second PRG. The repository
native suite passed at 512 KB and 2 MB. Windows and hardware remain untested.

## Encore validation

Playable source commit `20d7c4336205f335360b1628b5f2896939b615d2`.
The two guitar parts use independent YM2151 voices. Short palm-muted notes
lead into sustained root/fifth chords with pitched pickups and a PSG cymbal.
The two early accents each follow a half-beat rest. The bell motif, quieter
middle passage, later entrances and ending still run across all 157 bars.
The game stream and standalone ZSM contain matching note and timing events.

The ZIP was packed twice and matched byte for byte. Tests used separate fresh
extractions, stock 65C02 at 8 MHz with 2 MB banked RAM, Linux x16emu r49,
and ROM `b81654cc8c87ed96e3ffc7c8e7c312c9f3b7b870c7bb34de61e61eac931b819a`.

| Run | Frames | Over 133333 cycles | Peak cycles | Score loops | PCM underruns |
| --- | ---: | ---: | ---: | ---: | ---: |
| Cold start and F3 demo | 2015 | 174 | 633815 | 0 | 0 |
| F2, launch and flipper | 2097 | 42 | 305161 | 0 | 0 |
| Launch, flip, mute and resume | 2272 | 57 | 230227 | 0 | 0 |
| Unattended through the score loop | 12581 | 1344 | 623462 | 1 | 0 |

The full-loop emulator WAV peaked at 0.809 full scale, with 0 clipped
samples. Each run reported zero music errors. Fresh 512 KB startup printed
the 2 MB memory requirement and returned to BASIC, which then loaded and
executed a second PRG. Timing still exceeds budget on some frames. Windows
launcher execution and physical hardware remain unverified.

The 30-second cold-start excerpt uses the emulator's stereo WAV at original
gain. The screen was sampled at 24 fps against the emulator audio sample clock.
One sample deadline was missed in each of the 34- and 35-second raw captures.
A scan for newly lit red/green pixels in the cold-start demo found as many as
20 lit sites around the first accent and 29 around the second. Both side lamps
and the upper lane appeared in sequence after the center. The same analysis
after F2 found 21 and 28 sites. These are image estimates and depend on which
indicators gameplay owns. Waveform matching against the extracted PCM banks
found the launch at 6.85 seconds (0.79 correlation), and a flipper at 20.57
seconds (0.82 correlation) in the demo.

In separate diagnostic emulator runs with table effects muted, the half-second
after each chord measured about 3.1 and 4.5 dB louder respectively than the
corresponding passages of the previous Audition. The opening bell level matched.

| File | SHA-256 |
| --- | --- |
| `SpaceCmdrX16-Christmas-1.0-Beta-2MB-Encore.zip` | `8ff3fd52f8f899d1f18b90243fe4bd7e5ca8eb8db661077b5b4c8f6e8c4d8c15` |
| `SpaceCmdrX16-Christmas-Encore-Opening.mp4` | `b490b47ddd9f5131a1fec6c075a698f7127b4b4839da9becbfa0120146a85e61` |
| `SpaceCmdrX16-Christmas-Encore.zsm` | `2e15c92a9523252548ee195ea11edfd739ed5b4e3f0b2bde27679e27d7fe1f89` |

## Earlier preview validation

Runtime source: 9f4b534aa370fad9231576259e5064ad5b215319.
ZIP SHA-256: `d69d7eb0198ab6cf1fbdfdf4097af453ea2717b6e4ec60b87802e3ef09bea4f9`.
The packer reproduced the ZIP byte for byte.

x16emu r49, 65C02, 8 MHz, 2 MB, Linux HostFS, fresh ZIP extraction.
ROM SHA-256: `b81654cc8c87ed96e3ffc7c8e7c312c9f3b7b870c7bb34de61e61eac931b819a`.
The final ZIP reached play, ran F3, accepted a flipper takeover and F2,
launched the ball, toggled music and returned via Q. A separate idle-demo
run reached the first musical lift and captured both the red and green
sprite colors against an in-progress game. The final short smoke test
logged 33 frames over 133,333 cycles in 1125 frames (peak 233,670).
The final longer demo test logged 371 over in 4238 (peak 623,012).
Each recorded zero reported music errors and zero PCM underruns.

The same score and player completed one full loop in an immediately
preceding renderer revision (8b1ed62). The final renderer revision changes
mission-selection lamp priority only. The loop run reached 12,364
game frames with zero reported music errors and zero PCM underruns.
The preview has not been validated on Windows or physical hardware.

### Santa cap edition

Artwork source commit: `11f2d7b`.
ZIP SHA-256: `6614d211c84aef169b471730fa4564be1853ed06d365858b3efd8487cb73035e`.
The executable and score are byte-identical to the previous package.

A fresh extraction ran at 8 MHz with 2 MB on Linux x16emu r49. The capture
showed the cap and red/green center lamps in attract mode. The soundtrack
continued into ball 2 and logged one full loop, zero music errors, and zero
PCM underruns before Q. The demo logged 1,353 of 12,397 frames over
133,333 cycles, with a peak of 630,774. Windows and hardware remain untested.

### Audible soundtrack revision

The opening previously used only the quieter FM bell voices. Voice 5
of VERA PSG now carries the lead from tick zero, with FM retaining its
bell layer. The score length and lamp events are identical.

ZIP SHA-256: `e13946ef83fa1cdf9730e6aa38148a23dc66748aca1ac6a62c3db1ca8caf5f8d`.
Fresh-extraction r49 audio capture verified M mute and restart, the
expected 330/370/392 Hz opening motif, and zero PCM underruns.
The revised score was checked structurally for the full 204 seconds.
The revision's emulator playback test covered startup and the mute/restart
sequence. The preceding Santa-cap build supplied the full-loop playtest.


### Concert arrangement

The supplied MP3 decodes to 205.009 seconds. Its level envelope puts the first
full entrance near 1:04, the quiet bridge near 1:36, the second full entrance
near 2:10, and the final release near 3:12. The original native score follows
these landmarks using fresh instrumental parts on the Shchedryk melody.
It contains six YM2151 voices and five VERA PSG voices. VERA PCM stays
available for table, flipper and plunger samples. The musical accents,
brief breaks and releases carry their own lamp cues in COVER.CMD.

The opening pairs a tuned FM bell with a triangle voice. An answering bowed
part and plucked offbeats build toward a brass line, pitched kick and noise
snare. Two counter-rotating lamp trails approach the inner rank ring. At the
strongest downbeats that ring fills, then drops back on the same score clock.
Targets owned by gameplay take priority. The standalone ZSM contains the
same register writes and loop, with the private lamp extension omitted.

Cold boot, F2, and M restart use the same score. The game reads 64 KiB less
before playing the opening sample. This startup improvement is shared with
the standard Space Cadet X16 and Space CmdrX16 runtimes.

Concert runtime source: `2ffeb28820efd24e1be0ad61ad5e4d9d605e8368`.
Rebuilt ZIP SHA-256: `8309bdf43f4d7dad1de5af3b7265d3c34f23c46bbe3dd540ca24c4d96ad5034e`.
Standalone ZSM SHA-256: `8da340f45628fb91c832876246e6e0b01023083e0b7b9ed564612008b3d1cc38`.
Two independently packed ZIPs compared byte for byte. Console, input and
audio tests used fresh extractions on Linux r49 (af102408), ROM SHA-256
`b81654cc8c87ed96e3ffc7c8e7c312c9f3b7b870c7bb34de61e61eac931b819a`.

| Run | Frames | Over 133333 cycles | Peak cycles | PCM underruns |
| --- | ---: | ---: | ---: | ---: |
| Unattended cold start and idle demo | 3848 | 319 | 623481 | 0 |
| F2, launch, flip, mute, restart, Q | 2636 | 50 | 227566 | 0 |
| Recorded F3 demo through loop and Q | 12577 | 1384 | 630813 | 0 |

The recording covered one full loop with a 0.725 full-scale peak and zero
samples at the rails. Captures showed the tune before keyboard input, after
F2 and after M restart. A two-second music-off window was digitally silent.
The previous beta also produced the opening notes on a cold Linux launch.
The reported silence on the tester's system was not reproduced.

The 12 fps video uses the emulator WAV sample count as its clock. All 2544
capture deadlines were met. Normalized waveform matching against the extracted
effect banks found the release (SOUND22) at 6.79 seconds of play and a flipper
(SOUND104) at 139.46 seconds. Their peak correlations were 0.88 in the mixed
stereo capture folded to mono. A color scan of center-lamp sites in the video
counted up to 4 red/green sites together in seconds 8–20 and up to 17 in seconds
170–182. This is a visual estimate on compressed frames.

A 512 KB launch displayed the 2 MB requirement, returned to BASIC and
successfully loaded and executed another PRG. The Christmas runtime targets
2 MB. Windows and physical hardware were not exercised.

## Final Christmas game

The final game uses the approved 74.2-second melody-first Shchedryk
arrangement with five soft VERA PSG laser accents. The Blended table
art is the reference for this build. The decorative lamps advance on the
same song ticks as the audio. The outer lights catch each short laser
sweep, the crash expands from the center, and the final ring fades before
the opening motif returns.

To build the exact song:

```sh
python3 tools/music-auditions/carol-final/melody.py /tmp/CAROL.ZSM
python3 tools/music-auditions/carol-final/inspect_zsm.py /tmp/CAROL.ZSM
```

Use that file as the song argument for the Christmas header and game build.
The original choral setting is by Mykola Leontovych. The comparison score
is the four-voice Shchedryk setting at https://parafia.org.ua/piece/schedryk-3/.
