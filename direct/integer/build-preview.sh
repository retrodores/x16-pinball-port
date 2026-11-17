#!/bin/sh
set -eu
cd "$(dirname "$0")/../.."
sdk=${MOS_BIN:-/opt/llvm-mos-sdk-23.4.0/llvm-mos/bin}
python3 direct/integer/generate.py
python3 direct/integer/pack_audio.py
python3 - <<'PY'
from pathlib import Path
p=Path('direct/tools/build_preview_assets.py').resolve()
s=p.read_text().replace("direct/build/preview","direct/build/integer/preview").replace("DIRECT ENGINE","INTEGER ENGINE").replace("SLOW AT STOCK CPU","S  SOUND ON/OFF").replace("UNFINISHED / SILENT","PREVIEW / ORIGINAL FX")
exec(compile(s,str(p),'exec'),{'__file__':str(p),'__name__':'__main__'})
PY
cp direct/build/integer/WORLD.BIN direct/build/integer/preview/WORLD.BIN
cp direct/build/integer/FLIP.BIN direct/build/integer/preview/FLIP.BIN
cp direct/build/integer/SFXA.BIN direct/build/integer/SFXB.BIN direct/build/integer/preview/
src=direct/build/integer/src
common="$src/geometry.cpp $src/original_math.cpp $src/original_flipper.cpp $src/original_flipper_control.cpp $src/flipper.cpp $src/original_plunger.cpp $src/plunger.cpp $src/world.cpp"
for kind in normal test; do
 flag=""
 optimization=-Oz
 if [ "$kind" = test ]; then flag=-DPREVIEW_TEST; optimization=-Oz; fi
 "$sdk/mos-cx16-clang++" -std=c++11 "$optimization" -I"$src" $flag -DCMDRX_AUDIO direct/integer/audio.s direct/integer/fastmul.s $common "$src/preview.cpp" -o direct/build/integer/preview/$kind.prg
 address=$("$sdk/llvm-nm" direct/build/integer/preview/$kind.prg.elf | awk '$3=="ui_state" {print $1}')
 test -n "$address"
 printf 'ui_state = $%s\n' "$address" > direct/build/integer/preview/ui-address.inc
 python3 direct/integer/make_ui.py standard
 64tass -b -o direct/build/integer/preview/$kind-ui.bin direct/src/integer-ui-generated.asm
 rm direct/src/integer-ui-generated.asm
 # These functions would indicate a runtime floating-point operation.
 if "$sdk/llvm-nm" direct/build/integer/preview/$kind.prg.elf | grep -E '__.*(sf3|df3|sf2|df2|floatsi|fixsf|fixdf|extendsf|truncdf)'; then
  echo 'ERROR: floating-point helper in integer runtime' >&2
  exit 1
 fi
done
cp direct/build/integer/preview/normal.prg direct/build/integer/preview/CMDRX.PRG
cp direct/build/integer/preview/normal-ui.bin direct/build/integer/preview/UI.BIN
g++ -std=c++11 -O2 -I"$src" $common direct/t/preview_launch.cpp -o direct/build/integer/release-timing-host
direct/build/integer/release-timing-host > direct/build/integer/release-timing.tap
wc -c direct/build/integer/preview/CMDRX.PRG
