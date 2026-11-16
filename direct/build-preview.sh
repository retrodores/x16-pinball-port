#!/bin/sh
set -eu
cd "$(dirname "$0")/.."
sdk=${MOS_BIN:-/opt/llvm-mos-sdk-23.4.0/llvm-mos/bin}
mkdir -p direct/build/preview
python3 direct/tools/build_preview_assets.py
common="direct/src/original_math.cpp direct/src/original_flipper.cpp direct/src/original_flipper_control.cpp direct/src/flipper.cpp direct/src/original_plunger.cpp direct/src/plunger.cpp direct/src/world.cpp direct/src/preview.cpp"
for kind in normal test; do
 flag=""
 if [ "$kind" = test ]; then flag=-DPREVIEW_TEST; fi
 "$sdk/mos-cx16-clang++" -std=c++11 -Oz -ffp-contract=off -Idirect/src $flag $common -o direct/build/preview/$kind.prg
 address=$("$sdk/llvm-nm" direct/build/preview/$kind.prg.elf | awk '$3=="ui_state" {print $1}')
 test -n "$address"
 printf 'ui_state = $%s\n' "$address" > direct/build/preview/ui-address.inc
 64tass -b -o direct/build/preview/$kind-ui.bin direct/src/preview_ui.asm
done
cp direct/build/preview/normal.prg direct/build/preview/CMDRX.PRG
cp direct/build/preview/normal-ui.bin direct/build/preview/UI.BIN
wc -c direct/build/preview/CMDRX.PRG direct/build/preview/UI.BIN
