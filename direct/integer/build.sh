#!/bin/sh
set -eu
cd "$(dirname "$0")/../.."
sdk=${MOS_BIN:-/opt/llvm-mos-sdk-23.4.0/llvm-mos/bin}
python3 direct/integer/generate.py
src=direct/build/integer/src
common="$src/geometry.cpp $src/original_math.cpp $src/original_flipper.cpp $src/original_flipper_control.cpp $src/flipper.cpp $src/original_plunger.cpp $src/plunger.cpp $src/world.cpp"
for kind in world mechanisms flipper; do
 g++ -std=c++11 -O2 -I"$src" $common "$src/${kind}_probe.cpp" -o "direct/build/integer/$kind-host"
 "direct/build/integer/$kind-host" > "direct/build/integer/$kind-host.tap"
 "$sdk/mos-cx16-clang++" -std=c++11 -Oz -I"$src" direct/integer/fastmul.s $common "$src/${kind}_probe.cpp" -o "direct/build/integer/$kind.prg"
done

"$sdk/mos-cx16-clang++" -std=c++11 -Os -I"$src" direct/integer/fastmul.s direct/integer/arithmetic_probe.cpp -o direct/build/integer/arithmetic.prg
