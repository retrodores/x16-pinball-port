#!/bin/sh
set -eu
cd "$(dirname "$0")/.."
compiler=${MOS_CXX:-/opt/llvm-mos-sdk-23.4.0/llvm-mos/bin/mos-cx16-clang++}
mkdir -p direct/build
python3 direct/tools/extract_math.py
cp direct/data/table.json direct/build/table.json
python3 direct/tools/pack_world.py
for probe in math world; do
    extra=""
    if [ "$probe" = world ]; then extra=direct/src/world.cpp; fi
    g++ -std=c++11 -O2 -ffp-contract=off -Idirect/src direct/src/original_math.cpp $extra direct/t/${probe}_probe.cpp -o direct/build/${probe}-host
    direct/build/${probe}-host > direct/build/${probe}-host.tap
    "$compiler" -std=c++11 -Os -ffp-contract=off -Idirect/src direct/src/original_math.cpp $extra direct/t/${probe}_probe.cpp -o direct/build/${probe}.prg
done
