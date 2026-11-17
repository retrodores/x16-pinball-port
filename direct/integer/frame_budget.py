#!/usr/bin/env python3
from pathlib import Path
import re,sys
root=Path(__file__).resolve().parents[2];failed=False
for test,ram in enumerate((512,2048),1):
 text=(root/f'evidence/integer-preview/instrumented-{ram}.log').read_text(errors='replace')
 match=re.search(r'# CYCLES (\w+) (\w+) (\w+)',text)
 assert match,'missing timing evidence'
 maximum,average,missed=(int(x,16) for x in match.groups())
 ok=maximum<=133333;failed|=not ok
 print(f'{"ok" if ok else "not ok"} {test} - integer preview fits 133333 cycles, {ram} KB')
 print(f'# maximum={maximum} average={average} over_budget_frames={missed}/760')
print('1..2');sys.exit(1 if failed else 0)
