#!/bin/sh
# Experimental mixed-mode build; run with x16emu -c816 and an R47+ ROM.
set -eu
cd "$(dirname "$0")/../../.."
sdk=${MOS_BIN:-/opt/llvm-mos-sdk-23.4.0/llvm-mos/bin}
src=direct/build/integer/src
out=direct/build/integer/cpu816
mkdir -p "$out/preview"
common="$src/geometry.cpp $src/original_math.cpp $src/original_flipper.cpp $src/original_flipper_control.cpp $src/flipper.cpp $src/original_plunger.cpp $src/plunger.cpp $src/world.cpp"
for kind in world mechanisms flipper; do
 "$sdk/mos-cx16-clang++" -std=c++11 -Oz -mcpu=mosw65816 -I"$src" direct/integer/cpu816/fastmul.s $common "$src/${kind}_probe.cpp" -o "$out/$kind.prg"
done
"$sdk/mos-cx16-clang++" -std=c++11 -Os -mcpu=mosw65816 -I"$src" direct/integer/cpu816/fastmul.s direct/integer/arithmetic_probe.cpp -o "$out/arithmetic.prg"
cp direct/build/integer/preview/*.BIN "$out/preview/"
for kind in normal test; do
 flag=""; optimization=-Os
 if [ "$kind" = test ]; then flag=-DPREVIEW_TEST; optimization=-Oz; fi
 "$sdk/mos-cx16-clang++" -std=c++11 "$optimization" -mcpu=mosw65816 -I"$src" $flag direct/integer/cpu816/fastmul.s $common "$src/preview.cpp" -o "$out/preview/$kind.prg"
 address=$("$sdk/llvm-nm" "$out/preview/$kind.prg.elf" | awk '$3=="ui_state" {print $1}')
 test -n "$address"
 printf 'ui_state = $%s\n' "$address" > "$out/preview/ui-address.inc"
 # Source stays in direct/src so the original relative include works.
 sed 's@../build/preview/@../build/integer/cpu816/preview/@g' direct/src/preview_ui.asm > direct/src/cpu816-ui-generated.asm
 cp direct/build/integer/preview/sprites-init.bin direct/build/integer/preview/status.bin "$out/preview/"
 64tass -b -o "$out/preview/$kind-ui.bin" direct/src/cpu816-ui-generated.asm
 rm direct/src/cpu816-ui-generated.asm
 if "$sdk/llvm-nm" "$out/preview/$kind.prg.elf" | grep -E '__.*(sf3|df3|sf2|df2|floatsi|fixsf|fixdf|extendsf|truncdf)'; then exit 1; fi
done
cp "$out/preview/normal.prg" "$out/preview/CMDRX.PRG"
cp "$out/preview/normal-ui.bin" "$out/preview/UI.BIN"
