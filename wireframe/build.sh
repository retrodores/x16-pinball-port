#!/bin/sh
set -eu
cd "$(dirname "$0")/.."
sdk=${MOS_BIN:-/opt/llvm-mos-sdk-23.4.0/llvm-mos/bin}
python3 wireframe/pack.py
python3 wireframe/assets.py
g++ -std=c++11 -O2 -DPIN_TEST -Iwireframe/build wireframe/engine.cpp wireframe/soak.cpp -o wireframe/build/soak
wireframe/build/soak > wireframe/build/soak.log
g++ -std=c++11 -O2 -Iwireframe/build wireframe/engine.cpp wireframe/replay.cpp -o wireframe/build/replay
wireframe/build/replay > wireframe/build/replay.log
g++ -std=c++11 -O2 -DPIN_REFERENCE -Iwireframe/build wireframe/engine.cpp wireframe/replay.cpp -o wireframe/build/reference
wireframe/build/reference > wireframe/build/reference.log
cmp wireframe/build/replay.log wireframe/build/reference.log
for cpu in c02 c816; do
 out=wireframe/build/$cpu;mkdir -p "$out"
 mul=wireframe/widemul.s;narrow=wireframe/narrowmul_shared.s;flag=""
 if [ "$cpu" = c816 ]; then mul=direct/integer/cpu816/fastmul.s;narrow=wireframe/narrowmul.s;flag=-mcpu=mosw65816;fi
 for variant in normal auto; do
  test="";if [ "$variant" = auto ]; then test=-DPIN_AUTOPLAY;fi
  "$sdk/mos-cx16-clang++" -std=c++11 -Os $flag $test -DPIN_AUDIO -Iwireframe/build "$mul" wireframe/sqrt.s "$narrow" wireframe/build/audio.s wireframe/engine.cpp wireframe/main.cpp -o "$out/$variant.prg"
  if "$sdk/llvm-nm" "$out/$variant.prg.elf" | grep -E '__.*(sf3|df3|sf2|df2|floatsi|fixsf|fixdf|extendsf|truncdf)'; then exit 1;fi
 done
 cp "$out/normal.prg" "$out/CADET.PRG"
done
wc -c wireframe/build/c02/CADET.PRG wireframe/build/c816/CADET.PRG
