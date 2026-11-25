# Carol of the Bells – Space CmdrX16 rock audition 1

This standalone 65C02 audition uses the Mannheim Steamroller recording supplied for the Christmas edition as a musical reference. It follows the recording's duration, pulse and changing textures. The pitches of the inner parts are an estimate from a stereo master. The two guitars and newly synthesized stereo drum kit are rock arrangement choices. The song plays once.

## Rebuild the track

Use Python 3.12, NumPy, SciPy, ONNX Runtime, ffmpeg and the ICASSP 2022 ONNX model from Spotify Basic Pitch 0.4.0. The recording and the model are local inputs. The reference input for this take has SHA-256 `e7823ebaf0f6d87474da126d1cba8a36d114490881c4edac7468d5f0f3d82dd6`.

```sh
python3 transcribe.py "$RECORDING" "$NMP_ONNX" score.json
python3 arrange.py score.json CAROL.ZSM
python3 inspect_zsm.py CAROL.ZSM
```

The intermediate score SHA-256 for this take is `202cdcda881c7f8d454c255ec7b06114cb6cf4bd137a4d0d29ec26cd10f8bb41`. The native track SHA-256 is `f4cc99564f3a0a23367c22b0d24d7b04a17b8bf950fe01d6b29508de650c57a9`. To compare the drum contribution, run `python3 arrange.py score.json NODRUM.ZSM --omit pcm` and audition it as CAROL.ZSM in a separate folder. FM and PSG omissions are also available.

## Build the player

```sh
ca65 audition.s -o audition.o
ld65 -t none -S 0x7ff audition.o -o AUDITION.PRG
git clone https://github.com/mooinglemur/zsmkit.git
git -C zsmkit checkout 4c3593d3b09cc228b51516320832f12bd68da50f
mkdir -p zsmkit/lib
make -C zsmkit
cp zsmkit/lib/zsmkit-a000.bin ZSMKIT.BIN
cp zsmkit/LICENSE LICENSE-ZSMKIT.txt
```

Put AUDITION.PRG, CAROL.ZSM, ZSMKIT.BIN, LICENSE-ZSMKIT.txt, README.txt and RUN-WINDOWS.bat together in RUNTIME_DIR. Run `python3 package.py RUNTIME_DIR SpaceCmdrX16-Carol-Rock-Audition-1.zip` to build a repeatable archive. Use a clean extraction, with `x16emu.exe` and its matching `rom.bin` in the parent directory. The supplied launcher selects a stock 8 MHz 65C02 and 512 KB. The music engine occupies RAM banks 1–2, and the track begins in bank 3. A low-RAM VSYNC handler selects the library's primary bank and chains to the previous IRQ vector. Quit and normal completion restore that vector and the original RAM bank.

The inspector reads all 13,960 ticks, compares the header masks to actual key-on and PSG register writes, and checks each stereo sample extent and trigger. The encoded file has 8 active YM2151 channels, 16 active VERA PSG channels and 563 PCM triggers using 11 table entries. These include preblended combinations for the single PCM FIFO.

## Credits

Shchedryk by Mykola Leontovych. Reference interpretation by Mannheim Steamroller. Basic Pitch by Spotify and contributors supplied the note activation model. ZSMKit by mooinglemur is MIT-licensed. The percussion samples were synthesized for this take. The reference master is not embedded.

This audition has its own PRG and does not build or install a pinball soundtrack. A game mix needs a separate test of gameplay effects sharing the PCM FIFO, and the lamp timing must be checked against that integration.
