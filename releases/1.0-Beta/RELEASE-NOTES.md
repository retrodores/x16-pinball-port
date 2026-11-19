<!-- p8inball-runtime-beta -->
# 1.0 Beta — complete game runtimes

**All required game assets are already included in both ZIPs.** Extract into separate folders and double-click `RUN-WINDOWS.bat`. Only `x16emu.exe` and its matching `rom.bin` are needed in the parent folder. No other ZIP, asset import, patching, PowerShell, or compilation is required.

- **SpaceCadet-X16-1.0-Beta-Runtime.zip** — original Space Cadet presentation.
- **SpaceCmdr2D-1.0-Beta-Runtime.zip** — 2D Pinball — Space CmdrX16 artwork, already applied.

Each archive includes all 30 game files: PRG, matched overlays, table graphics, palettes, sprites, geometry, depth data, dynamic patches, music and PCM effects. Both include human-readable and machine-readable engine specifications under `specs/`, plus license notices. No nested archives or standalone game/build source are included. The machine reference documentation includes geometry and policy excerpts. Emulator and ROM are not bundled.

These complete packages replace the earlier import-only downloads with the same filenames. Re-download and extract into fresh folders.

## Provenance

Engine source: `9534fb8ed127092b0e9580ab75bfaf5d010e9b94`.
Specification: `898276b21c124afddbb242fb4dba0ff933feb049`.
PRG and overlays remain byte-identical to the accepted beta. The original reference ZIP is unchanged.

## SHA-256

```text
eee9bdb8500e3be61eb7ec19474b9b1f49227e0699c678c0294b7d8949888799  SpaceCadet-X16-1.0-Beta-Runtime.zip
cdbf79a33662ba12feda6b28698fec776d17f3d29706563c77fa66897aece511  SpaceCmdr2D-1.0-Beta-Runtime.zip
```

## Validation

All 30 runtime files in each ZIP were compared byte-for-byte with the tested edition. ZIP CRCs, explicit allowlists, included specs and absence of nested packages/import scripts were checked. Fresh extractions are tested directly in the Linux emulator with no external asset archive. Prior 512 KB and 2048 KB tests of identical game bytes covered playfield rendering, plunger/flipper animation, music toggle/restart, audio output, new game and normal exit. Detailed results are in VALIDATION.json.

Emulator: r49 Pyrite `af102408`, stock 65C02 at 8 MHz. Exact ROM SHA-256 is in VALIDATION.json; separate ROM version not independently identified. Windows interactive launcher testing remains unverified. The engine still exceeds the 133333-cycle budget on some frames and has incomplete rules; this is not a sustained-60-FPS certification.

Keep the release **draft** until Brett approves publishing. Repository readers can download both ZIPs from `releases/1.0-Beta/` on `spacecadet-fidelity`. Original game resources retain their existing attribution and are not relicensed under the engine's MIT license. Wiki unchanged.
