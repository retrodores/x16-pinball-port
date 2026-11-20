# Attract Fidelity Preview recovery

Worktree /opt/cadet-panel-package on the authorized VM. Branch
x16-attract-fidelity, split from 76799b6 on spacecadet-fidelity. The source
commits are 85b911a and d8160f2. Read root and cadet AGENTS.md first.

The controller uses swept approach edges and independent delay/hold timers.
Its launch begins in Serving; the recovered standalone shooter edge is
still pending. The three balls and missions use the production simulation.
The center rings run a 72-frame opening sparkle, show rank progress and
animate first-rank Target Practice and Launch Training. The rest of the
original mission and jackpot ladder is pending. Both panes use PBMSG_FT
read from the user's PINBALL.EXE. The score and BALL keep their own sprites.

## Regenerate and build on the VM

```sh
cd /opt/cadet-panel-package
python3 cadet/game/prepare_runtime.py
python3 cadet/game/pack_dynamic.py
python3 cadet/game/pack_music_cover.py /opt/cadet-gtr3qq-input/Pinball_R6.zsm
CADET_BUILD_PLAYER_ONLY=1 python3 cadet/game/build_native.py
CADET_COVER_AUDIO=1 CADET_BUILD_PLAYER_ONLY=1 python3 cadet/game/build_native.py
python3 cadet/game/test_build_native.py CADET COVER
python3 cadet/game/test_mechanisms.py
python3 cadet/game/test_package_development.py
cc -O2 -Icadet/play-build cadet/game/test_attract.c cadet/game/engine.c -o /tmp/cadet-test-attract
/tmp/cadet-test-attract
python3 packaging/build_center_preview.py --attract-fidelity releases/Attract-Preview-3 cadet/play-build /opt/cadet-attract-zips d8160f2
```

The font importer uses the executable at
/opt/spacecadet-x16-analysis/input/game/pinball.exe by default. See
game/IMPORT.md for the supported local inputs. The 6,360-byte packed font
starts at bank 57 A400, after PCM2. The two editions keep distinct theme
patch prefixes in DYN2.BIN. Keep each PRG, PHY and RUL together.

For a stock-emulator attract trace, set CADET_ATTRACT_TEST=1 and
CADET_TEST_FRAMES=60000 for each build. Copy the corresponding ATTEST or
CATTEST PRG/PHY/RUL into a fresh extracted runtime. Invoke Linux r49 with
the matching ROM, -c02 -mhz 8 -ram 512 or 2048, -warp -echo raw -fsroot .
-prg ATTEST.PRG or CATTEST.PRG, and -run. The fixture stops at ball three
or frame limit. Use CADET_PROFILE_ATTRACT=1 for phase timing in a 512 KB
fixture. It adds the pre-display cycle count to each new worst-frame line.

The 133,333-cycle target remains open. Profiling put 460,807 of 495,466
cycles before display in the worst sampled 512 KB frame. Keep development
labeling. Linux extraction, runtime and WAV evidence are on the VM in
/opt/cadet-attract-extracted and /tmp/cadet-attract-*.log. See the release
validation JSON for actual coverage and limitations. Windows is untested.
