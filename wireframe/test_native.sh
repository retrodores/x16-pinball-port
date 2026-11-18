#!/bin/sh
set -eu
cd "$(dirname "$0")/.."
sdk=${MOS_BIN:-/opt/llvm-mos-sdk-23.4.0/llvm-mos/bin}
g++ -std=c++11 -O2 -DPIN_TEST -Iwireframe/build wireframe/tests.cpp -o wireframe/build/tests
wireframe/build/tests > wireframe/evidence/host-tests.log
for cpu in c02 c816; do
 flag="";mul=wireframe/widemul.s;narrow=wireframe/narrowmul_shared.s
 if [ "$cpu" = c816 ]; then flag=-mcpu=mosw65816;mul=direct/integer/cpu816/fastmul.s;narrow=wireframe/narrowmul.s;fi
 "$sdk/mos-cx16-clang++" -std=c++11 -Os $flag -DPIN_TEST -Iwireframe/build "$mul" wireframe/sqrt.s "$narrow" wireframe/tests.cpp -o wireframe/build/$cpu/tests.prg
 "$sdk/mos-cx16-clang++" -std=c++11 -Os $flag -DCMDRX_AUDIO "$mul" wireframe/sqrt.s "$narrow" wireframe/audio.s wireframe/audio_probe.cpp -o wireframe/build/$cpu/audio.prg
 for ram in 512 2048; do
  X16_CPU=$cpu X16_RAM_KB=$ram perl wireframe/run_native.pl wireframe/build/$cpu/tests.prg wireframe/build > wireframe/evidence/tests-$cpu-$ram.log
  if grep -q '^not ok' wireframe/evidence/tests-$cpu-$ram.log; then cat wireframe/evidence/tests-$cpu-$ram.log;exit 1;fi
 done
done
python3 wireframe/verify_audio.py
