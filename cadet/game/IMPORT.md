# CmdrX Cadet local asset import

The code ZIP contains the engine, importer and launch templates. Generate a private
runtime from a supported local installation. The existing CmdrX Cadet checkout
supplies `wireframe/recovered-table.json` and
`direct/vendor/SpaceCadetPinball/control.cpp`. Pass those paths explicitly when
running from the code ZIP. The converter does not derive these two reference
inputs from the installation.

Install Python with Pillow, NumPy, SciPy and mido, Perl with JSON::PP and
Digest::SHA, the LLVM-MOS CX16 SDK, and DejaVu Sans Mono. Use Linux or WSL.

```sh
python3 cadet/game/import_local.py \
  --install "/path/to/Pinball" --output "./CmdrX Cadet" \
  --table "/path/to/checkout/wireframe/recovered-table.json" \
  --rules "/path/to/checkout/direct/vendor/SpaceCadetPinball/control.cpp" \
  --compiler "/path/to/llvm-mos/bin/mos-cx16-clang" \
  --font "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"
```

Choose a new output directory. The importer stages all outputs, checks the RAM/VRAM
layout and publishes the completed folder in one rename. The manifest records
input and output hashes. The importer validates the supported DAT, MIDI and
Windows executable. It reads PBMSG_FT directly from the local executable. Input filenames are case insensitive. The file list includes the
17 required WAVs. Other WAVs are optional for this build.

Put the matching x16emu and rom.bin in the parent folder, then use
`RUN-WINDOWS.bat` or `run-linux.sh`. Either launcher accepts a path to a
different copy of the emulator. Keep the generated PRG, overlays and data together.
