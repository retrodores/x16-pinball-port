#!/bin/sh
set -eu
cd "$(dirname "$0")/.."
compiler=${MOS_CXX:-/opt/llvm-mos-sdk-23.4.0/llvm-mos/bin/mos-cx16-clang++}
mkdir -p direct/build
python3 direct/tools/extract_math.py
cp direct/data/table.json direct/build/table.json
python3 direct/tools/pack_world.py
python3 direct/tools/pack_flippers.py
common="direct/src/original_math.cpp direct/src/original_flipper.cpp direct/src/original_flipper_control.cpp direct/src/flipper.cpp direct/src/original_plunger.cpp direct/src/plunger.cpp"
for probe in math world reference flipper mechanisms plunger; do
    extra=""
    source_probe=$probe
    if [ "$probe" = world ] || [ "$probe" = mechanisms ]; then extra=direct/src/world.cpp; fi
    if [ "$probe" = reference ]; then extra=direct/reference/world_baseline.cpp; source_probe=world; fi
    g++ -std=c++11 -O2 -ffp-contract=off -Idirect/src $common $extra direct/t/${source_probe}_probe.cpp -o direct/build/${probe}-host
    direct/build/${probe}-host > direct/build/${probe}-host.tap
    "$compiler" -std=c++11 -Oz -ffp-contract=off -Idirect/src $common $extra direct/t/${source_probe}_probe.cpp -o direct/build/${probe}.prg
done
