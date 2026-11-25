# Space CmdrX16 Christmas preview

This 2 MB 65C02 target uses the Space CmdrX16 1.0 Beta RAM-and-Quit
runtime as its input. The packer pins the base archive by SHA-256.
The current holiday build uses seven banks for its native Shchedryk arrangement
and bank 64 for the holiday lamp renderer. The game stream includes private
lamp cues and a 204.78-second loop at 92 Hz. SHCHEDRYK.ZSM contains the same
music writes and timing in standard ZSM v1 without the lamp extension.
The YM2151 and PSG play music while the existing VERA PCM mixer plays
table sounds. No commercial recording or sampled music is in this build.

The Encore opening reaches its first guitar chord at 10.43 seconds. At
20.87 seconds the next chord sends color from the center across the rank ring,
out to the left and right lamp banks and up to the upper rollovers. The
choreography addresses 27 ring positions and four playfield inserts. The
renderer processes eight sprites per display frame. Gameplay owns the lamps
during startup, tilt and rank flashes. Active missions reserve the outer ring,
and individual lane, hazard and gravity-well indicators keep priority through
both halves of a gameplay blink. F2 and re-enabling music restart the score.
Ball drains and attract transitions keep the current musical position.

Build on the beta toolchain with its matching generated runtime headers
in cadet/play-build, including the original model and dynamic headers:

```sh
python3 packaging/build_christmas_preview.py headers /opt/spacecadet-x16-analysis/evidence/inventory.json
python3 cadet/game/christmas_music.py cadet/play-build
python3 cadet/game/test_christmas_music.py
CADET_CHRISTMAS=1 CADET_BUILD_PLAYER_ONLY=1 python3 cadet/game/build_native.py
python3 packaging/build_christmas_preview.py package /tmp/SpaceCmdrX16-Christmas-1.0-Beta-2MB-Preview.zip
```

The base edition retains its existing build path. The runtime archive
contains only the playable files, launcher, documentation and notices.
The preview uses the original table assets and is a private playtest.

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
