#!/bin/sh
set -eu
cd "$(dirname "$0")/../.."
sdk=${MOS_BIN:-/opt/llvm-mos-sdk-23.4.0/llvm-mos/bin}
src=direct/build/integer/src
python3 - <<'PY'
from pathlib import Path
p=Path('direct/build/integer/src');s=(p/'preview.cpp').read_text()
start=s.index('volatile uint8_t raw_keys');end=s.index('__attribute__((naked)) void restore_screen')
(p/'controls-generated.h').write_text('extern "C" {\n'+s[start:end]+'\n}\n')
PY
common="$src/geometry.cpp $src/original_math.cpp $src/original_flipper.cpp $src/original_flipper_control.cpp $src/flipper.cpp $src/original_plunger.cpp $src/plunger.cpp"
g++ -std=c++11 -O2 -I"$src" $common direct/integer/contacts_probe.cpp -o direct/build/integer/contacts-host
direct/build/integer/contacts-host > direct/build/integer/contacts-host.tap
if grep -q '^not ok' direct/build/integer/contacts-host.tap; then cat direct/build/integer/contacts-host.tap; exit 1; fi
for cpu in c02 c816; do
 out=direct/build/integer; mul=direct/integer/fastmul.s; flag=""
 if [ "$cpu" = c816 ]; then out=$out/cpu816; mul=direct/integer/cpu816/fastmul.s; flag=-mcpu=mosw65816; fi
 "$sdk/mos-cx16-clang++" -std=c++11 -Oz $flag -I"$src" "$mul" $common direct/integer/contacts_probe.cpp -o "$out/contacts.prg"
 "$sdk/mos-cx16-clang++" -std=c++11 -Oz $flag -I"$src" direct/integer/controls_probe.cpp -o "$out/controls.prg"
 "$sdk/mos-cx16-clang++" -std=c++11 -Oz $flag -DCMDRX_AUDIO -I"$src" "$mul" direct/integer/audio.s direct/integer/audio_probe.cpp -o "$out/audio.prg"
done
