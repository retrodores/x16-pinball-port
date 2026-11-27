# Space CmdrX16 2D Pinball 1.0 handoff

The public repository is `retrodores/x16-pinball-port`. Continue development
from `main`. The public downloads are on [v1.0](https://github.com/retrodores/x16-pinball-port/releases/tag/v1.0) and the
[wiki](https://github.com/retrodores/x16-pinball-port/wiki) contains player and build instructions.

## Build any of the three editions

Use a full Git clone, Python 3 with NumPy and Pillow for the Christmas
tools, and LLVM-MOS SDK 23.4.0. The build defaults to
`/opt/llvm-mos-sdk-23.4.0/llvm-mos/bin/mos-cx16-clang`; set `MOS_CC`
to the absolute path if installed elsewhere. Run from the repository root.

```sh
python3 packaging/build_release.py regular --ram 512KB
python3 packaging/build_release.py regular --ram 2MB
python3 packaging/build_release.py christmas --ram 2MB
python3 packaging/build_release.py clone --ram 512KB
python3 packaging/build_release.py clone --ram 2MB
```

Outputs default to `build/releases`. Use `--output` to choose another
directory. The standard and exemplar builds export the pinned, approved
engine commit `e849f19accc583176f5fb9e89e0454cf750996ae` from Git history.
The Christmas build compiles its edition from the checkout and assembles
the approved assets using the archived 2 MB standard package. Generated
headers are in [packaging/release-inputs](../../../packaging/release-inputs/).
The builder stages temporary inputs separately from local play-build files.
The archived standard and exemplar builds share the engine and differ in
their presentation assets.

The v1.0 standard runtime files match the archived beta runtime files.
The Christmas runtime files match approved source
`09bcf4a5e44ac9583a502372d9cbc8a636405fa2`. The ZIP's player README reflects
the 1.0 designation. The [exemplar ZIPs](../../../releases/1.0/exemplar/)
are available in the repository. The v1.0 workflow uploads the three 2D ZIPs.

## Christmas sources and validation

- Approved look: Blended winter artwork at `965f1b4`. Holiday asset
  composition lives in `packaging/christmas_art.py` and
  `packaging/christmas_playfield.py`.
- Score source: `tools/music-auditions/carol-final/melody.py`. The approved
  74.2-second `CAROL.ZSM` has SHA-256
  `443860718e270cb1bdd4a5eca855c0730ee3e531c4ea1a2aa7907d1173cc4988`.
  The lamp timeline derives from score events via `cadet/game/carol_lamps.py`.
  Use the melody-first source for revisions. Earlier concert and rock
  auditions are historical.
- The approved runtime completed two soundtrack loops at 8 MHz and 2 MB
  in Linux x16emu r49, with zero music errors, PCM underruns or samples
  at full scale. Timing exceeded 133,333 cycles on 635 of 9,243 frames.
  The documented frame budget still applies to native timing fixtures.
- Preserve the flat ZIP layout, overlay names, 128-bit scores, and matching
  RAM checks. Keep the emulator and ROM separate from the runtime.
- Both RAM sizes passed `prove t/native.t`. Fresh extractions of all three
  official ZIPs reached play and Q returned to BASIC, which loaded and ran
  a second PRG. The Christmas build exercised its 2 MB guard at 512 KB
  and also returned to a working BASIC prompt. All five packages passed
  ZIP integrity and member comparison against their approved input packages.
- Physical X16 and native Windows were outside the v1.0 verification.

See the [Christmas preview history](../../../cadet/game/CHRISTMAS-PREVIEW.md)
and the [beta validation report](../../../releases/1.0-Beta/Emulator/RAM-and-Quit/VALIDATION.json)
for historical measurements and test details.

## Resume on the DC VM

The working repository is `/opt/cmdrx-cadet`. The Christmas delivery and
validation evidence are under `/opt/spacecmdrx16-christmas-delivery`, including
`final/`. For new work, use a fresh clone or worktree at the current
`main`.
