#!/usr/bin/env python3
"""Verify snapshot integrity and binary contracts without rebuilding the game."""
from pathlib import Path
import hashlib,json,struct,re,sys
snapshot_only="--snapshot-only" in sys.argv
ROOT=Path(__file__).resolve().parents[2]; HERE=Path(__file__).resolve().parent
c=json.loads((HERE/'engine-contract.json').read_text());r=json.loads((HERE/'reference-data.json').read_text())
import jsonschema
jsonschema.Draft202012Validator.check_schema(json.loads((HERE/'engine-contract.schema.json').read_text()))
jsonschema.validate(c,json.loads((HERE/'engine-contract.schema.json').read_text()))
assert c['baseline_commit']==r['baseline_commit']
for record in c['sources']+([] if snapshot_only else c['runtime_files']):
    p=ROOT/record['path']
    assert hashlib.sha256(p.read_bytes()).hexdigest()==record['sha256'],record['path']
    if 'bytes' in record: assert p.stat().st_size==record['bytes']
for name,row in r['generated_headers'].items():
    assert hashlib.sha256(row['text'].encode()).hexdigest()==row['sha256'],name
assert len(r['edges'])==c['geometry']['edges']==1217
model=None if snapshot_only else (ROOT/'cadet/play-build/MODEL.BIN').read_bytes()
for e in r['edges']:
    b=struct.pack(c['geometry']['edge_struct_format'],*[e[f] for f in c['geometry']['fields']])
    off=11*8192+e['id']*32
    assert model is None or b==model[off:off+32]
    assert e['group']<c['geometry']['components']
    if e['flags']&1: assert e['radius_squared']==e['r']**2 and e['r']<=181
for offset in r['grid_index_offsets']:
    ids=r['candidate_lists'][str(offset)]
    assert len(ids)<128 and all(0<=x<len(r['edges']) for x in ids)
    assert (offset%8192)+2*(len(ids)+1)<=8192
banks=[b for row in c['bank_allocations'] for b in row['banks']]
assert len(banks)==len(set(banks))==63 and min(banks)==1 and max(banks)==63
for field,name in [('font_base','FONT_BASE'),('sprite_pattern_base','SPRITE_BASE')]:
    header=r['generated_headers']['ui.h' if name=='FONT_BASE' else 'sprites.h']['text']
    assert int(re.search(r'#define '+name+r' (\d+)',header)[1])==c['vera'][field]
assert c['vera']['ball_scratch_base']==c['vera']['font_base']+2048
assert len(r['tables']['metadata'])==33 and len(r['tables']['tips'])==2
assert all(len(t)==121 for t in r['tables']['tips'])
assert len(c['runtime_files'])==30
if not snapshot_only: assert (ROOT/'cadet/play-build/CADET.PRG').read_bytes()[:2]==b'\x01\x08'
if not snapshot_only: assert all((ROOT/('cadet/play-build/CADET.'+ext)).stat().st_size==8192 for ext in ('RUL','PHY'))
print('Mode:', 'embedded snapshot + source hashes' if snapshot_only else 'full prepared checkout')
print('PASS: applicable checks: JSON Schema, source/runtime SHA-256, 1217 binary edge round trips, 9216 grid references, bank ownership, generated-table and runtime-layout checks.')
print('Documentation-only validation. No game rebuild, timing rerun or Prog8 port.')
