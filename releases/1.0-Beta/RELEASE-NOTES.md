<!-- p8inball-runtime-beta -->
# 1.0 Beta — complete game runtimes

**All required game assets are already included in both ZIPs.** Extract into separate folders and double-click `RUN-WINDOWS.bat`. Only `x16emu.exe` and its matching `rom.bin` are needed in the parent folder. No other ZIP, asset import, patching, PowerShell, or compilation is required.

- **SpaceCadet-X16-1.0-Beta-Runtime.zip** — original Space Cadet presentation.
- **SpaceCmdr2D-1.0-Beta-Runtime.zip** — 2D Pinball — Space CmdrX16 artwork, already applied.

Each archive includes all 30 game files: PRG, matched overlays, table graphics, palettes, sprites, geometry, depth data, dynamic patches, music and PCM effects. Both include human-readable and machine-readable engine specifications under `specs/`, plus license notices. No nested archives or standalone game/build source are included. The machine reference documentation includes geometry and policy excerpts. Emulator and ROM are not bundled.

This refresh raises the music level by about **6 dB** in both editions. The PCM sound effects are unchanged. Re-download the ZIP and extract it into a fresh folder.

## Provenance

Engine source: `9534fb8ed127092b0e9580ab75bfaf5d010e9b94`.
Music converter: `7f6edd77f3665c0f167fb983b784c242f82cce47`.
Specification: `898276b21c124afddbb242fb4dba0ff933feb049`.
The PRG and overlays match the accepted beta. The specs describe the reference snapshot. PACKAGE-MANIFEST.json records the current runtime hashes.

## SHA-256

```text
6068e17ad559b92e6ffa41e603575834a8149ab2fd5124b3ed2882869ac7251e  SpaceCadet-X16-1.0-Beta-Runtime.zip
9c8c4e80d917ab8a447482cf3cc949001f2dab8ae8922aa89a18d2aabd1b5934  SpaceCmdr2D-1.0-Beta-Runtime.zip
```

## Validation

Both editions passed Linux emulator smoke tests at 512 KB and 2048 KB from fresh extractions. Checks covered playfield rendering, plunger and flipper animation, music toggle and restart, audio output, new game, and normal exit. The separate audio fixture completed a full soundtrack loop with concurrent effects at both RAM sizes. See VALIDATION.json for results.

Emulator: r49 Pyrite `af102408`, stock 65C02 at 8 MHz. Exact ROM SHA-256 is in VALIDATION.json; separate ROM version not independently identified. Windows interactive launcher testing remains unverified. The engine still exceeds the 133333-cycle budget on some frames and has incomplete rules; this is not a sustained-60-FPS certification.

Keep the release **draft** until Brett approves publishing. Repository readers can download both ZIPs from `releases/1.0-Beta/` on `spacecadet-fidelity`. Original game resources retain their existing attribution and are not relicensed under the engine's MIT license. Wiki unchanged.
