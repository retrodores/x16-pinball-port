<!-- p8inball-runtime-beta -->
# 1.0 Beta — Space Cadet X16 and Space CmdrX16

Two separate runtime editions, using identical current engine binaries:

- **SpaceCadet-X16-1.0-Beta-Runtime.zip**: original Space Cadet presentation, imported locally.
- **SpaceCmdr2D-1.0-Beta-Runtime.zip**: 2D Pinball — Space CmdrX16 artwork.

Both include human-readable and machine-readable engine specifications under `specs/`. They contain no standalone engine/build source files, nested ZIPs, emulator, ROM, original playfield or audio assets. Requested machine reference documentation includes geometry, lookup tables and policy excerpts.

Extract each edition into a separate folder. Keep `x16emu.exe` and its matching `rom.bin` in the parent folder. Place your unopened `CmdrX_Cadet_0.3.1_Development.zip` in the game folder or its parent. Double-click `RUN-WINDOWS.bat`; missing/damaged assets are imported automatically, and the CmdrX16 edition applies its 2D patch. Once installed, valid assets can be reused without the local ZIP. Keep the ZIP for repair. PowerShell 5.1+ is required.

## Provenance

Engine source: `9534fb8ed127092b0e9580ab75bfaf5d010e9b94`.
Specification: `898276b21c124afddbb242fb4dba0ff933feb049`.
Both editions preserve the beta PRG and both overlays byte-for-byte. Packaging-only launcher changes add full asset hash validation. The immutable tester reference is retained privately and is not a release asset.

Reference SHA-256: `7f2984ab9939b5ec8ffa828cdd2423c16c4faa3e3bf2afb3881fb47acf87b72b`.

## Checksums

```text
ca7345bcb5c4e819a398aaa6654bd72e807d1adacc4a2f702253bb28360bf118  SpaceCadet-X16-1.0-Beta-Runtime.zip
c24e65d4fe87fb8e4ce0ebb129a96dab48b9e4637464a97cefe46279af475271  SpaceCmdr2D-1.0-Beta-Runtime.zip
```

## Actual validation and limits

Both editions passed isolated Linux emulator smoke tests at 512 KB and 2048 KB, stock 65C02 at 8 MHz: static playfield comparison, plunger and flipper animation, new game, music toggle/restart, recorded audio, and normal exit. Both presentation screenshots were inspected. Reference/asset hashes, patch equivalence, allowlists, ZIP CRC and exclusion of nested archives/standalone game source were checked.

Emulator: r49 Pyrite, build `af102408`. ROM identity is recorded by SHA-256 in VALIDATION.json; a separate ROM release number was not established.

**Windows interactive testing is unavailable.** First launch/import and relaunch without the ZIP have not been executed on Windows. Python verification of asset hashes/patch results is not a substitute for testing PowerShell. Complete those checks before approving publication.

The timing budget still fails on some frames: smoke-test maxima were 158465/158261 cycles for original mode and 160847/167700 for CmdrX16 at 512 KB/2048 KB, against the 133333-cycle limit. This beta is not a sustained-60-FPS or full-fidelity certification. Full metrics are in VALIDATION.json.

Keep this release **draft** until Brett approves publication. GitHub draft visibility can be narrower than repository read access; the same ZIPs are also tracked under `releases/1.0-Beta/` on `spacecadet-fidelity`, so repository readers can download them there. No wiki changes.
