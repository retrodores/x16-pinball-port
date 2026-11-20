<!-- p8inball-runtime-beta -->
# 1.0 Beta — complete game runtimes

**All required game assets are already included in both ZIPs.** Extract into separate folders and double-click `RUN-WINDOWS.bat`. Only `x16emu.exe` and its matching `rom.bin` are needed in the parent folder. No other ZIP, asset import, patching, PowerShell, or compilation is required.

- **SpaceCadet-X16-1.0-Beta-Runtime.zip** — original Space Cadet presentation.
- **SpaceCmdr2D-1.0-Beta-Runtime.zip** — 2D Pinball — Space CmdrX16 artwork, already applied.

Each archive includes all 30 game files: PRG, matched overlays, table graphics, palettes, sprites, geometry, depth data, dynamic patches, music and PCM effects. Both include human-readable and machine-readable engine specifications under `specs/`, plus license notices. No nested archives or standalone game/build source are included. The machine reference documentation includes geometry and policy excerpts. Emulator and ROM are not bundled.

This refresh puts the **music about 5.6 dB above sound effects** in the measured test scene. Live status messages and the music indicator now render in purple in both editions. Re-download the ZIP and extract it into a fresh folder.

## Provenance

Engine and music converter: `116ee4cc6d7b85c55313c54f404c4ce3f676c3fe`.
Specification snapshot: `898276b21c124afddbb242fb4dba0ff933feb049`.
PACKAGE-MANIFEST.json records the current runtime hashes, including the matched PRG and overlays.

## SHA-256

```text
12318ec032bb95ba2f3bc0cd068596114ecb63e7aa19e4cc3e1742e3bc118cf6  SpaceCadet-X16-1.0-Beta-Runtime.zip
be3395340ff9f6ea9ddeee9a7c7cfb29d7df4ead3785f6127448608f34c6ec9a  SpaceCmdr2D-1.0-Beta-Runtime.zip
```

## Validation

Both editions passed Linux emulator smoke tests at 512 KB and 2048 KB from fresh extractions. Checks covered purple live text, all four new-ball gate lamp regions, playfield rendering, controls, music toggle and restart, new game, and normal exit. The audio fixture completed a full soundtrack loop with concurrent effects at both RAM sizes. The deliberate 12000-frame test had 70 frames over budget at each RAM size. See VALIDATION.json for results.

Emulator: r49 Pyrite `af102408`, stock 65C02 at 8 MHz. Exact ROM SHA-256 is in VALIDATION.json; separate ROM version not independently identified. Windows interactive launcher testing remains unverified. The engine still exceeds the 133333-cycle budget on some frames and has incomplete rules; this is not a sustained-60-FPS certification.

Keep the release **draft** until Brett approves publishing. Repository readers can download both ZIPs from `releases/1.0-Beta/` on `spacecadet-fidelity`. Original game resources retain their existing attribution and are not relicensed under the engine's MIT license. Wiki unchanged.
