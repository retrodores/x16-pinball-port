# Space CmdrX16 Christmas preview

This 2 MB 65C02 target uses the Space CmdrX16 1.0 Beta RAM-and-Quit
runtime as its input. The packer pins the base archive by SHA-256.
The holiday build uses three banks for a new native Shchedryk arrangement
and bank 64 for the holiday lamp renderer. The game stream includes private
lamp cues and a 204-second loop at 92 Hz. SHCHEDRYK.ZSM contains the same
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
