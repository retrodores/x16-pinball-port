# Engine handover

Start with [ENGINE-SPEC.md](ENGINE-SPEC.md). It documents the actual engine at commit `9534fb8ed127092b0e9580ab75bfaf5d010e9b94`, including limits and incomplete work.

- [engine-contract.json](engine-contract.json): typed constants, memory ownership, enums, file/source hashes and symbol locations.
- [engine-contract.schema.json](engine-contract.schema.json): JSON Schema 2020-12.
- [reference-data.json](reference-data.json): decoded collision records, spatial index, generated tables/headers, rules source and historical reports.
- `export_contract.py`: regenerate from an existing prepared VM checkout.
- `verify_contract.py`: validate schema, hashes, table layouts and binary round trips. Requires Python 3 and `jsonschema`.

The generated `cadet/play-build` directory is ignored by Git. The JSON snapshot preserves the data needed to inspect the engine without those files; it does not bundle artwork, audio, PRGs or a full runtime. To rebuild or run full snapshot verification on a fresh clone, prepare the local assets using [IMPORT.md](../../cadet/game/IMPORT.md) and the appropriate source inputs. Regenerated presentation assets can differ from the customized release; runtime hashes identify this particular VM snapshot.

Run on the prepared checkout:

```sh
python3 docs/engine/verify_contract.py
```

For a source-only clone, validate the embedded snapshot without requiring ignored runtime files:

```sh
python3 docs/engine/verify_contract.py --snapshot-only
```

Regeneration intentionally updates provenance to the current commit. Review the prose manually after engine changes. Historical timing JSON is not a certification of the current commit. No Prog8 implementation was attempted.
