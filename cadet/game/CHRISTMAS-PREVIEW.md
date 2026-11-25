# Space CmdrX16 Christmas preview

This 2 MB 65C02 target uses the Space CmdrX16 1.0 Beta RAM-and-Quit
runtime as its input. The packer pins the base archive by SHA-256.
The current holiday build uses six banks for its native Shchedryk arrangement
and bank 64 for the holiday lamp renderer. The game stream includes private
lamp cues and a 204.78-second loop at 92 Hz. SHCHEDRYK.ZSM contains the same
music writes and timing in standard ZSM v1 without the lamp extension.
The YM2151 and PSG play music while the existing VERA PCM mixer plays
table sounds. No commercial recording or sampled music is in this build.

Holiday sprites draw over inactive center inserts only. Normal startup,
rank progress, rank flash, and tilt retain priority. Active missions
reserve the outer ring for their chase. Unclaimed inner inserts can still
follow the song during a mission. The holiday
display updates seven sprites per normal display frame. F2 and re-enabling
music restart the score. Ball drains and attract transitions keep the
current musical position.

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

## Preview validation

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
