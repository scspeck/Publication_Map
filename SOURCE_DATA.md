# Source data for this build

Input file: `catalog_record_summary (14)(1).csv`

The source CSV is intentionally not duplicated inside this distributable package.
Run:

```bash
python scripts/process_compact_atlas.py "catalog_record_summary (14)(1).csv" data
```

after placing the Arctos export alongside the project or changing the path.

Build summary:
- parasite records with host relationships: 51,376
- unique hosts: 30,906
- host–parasite associations: 51,864
- countries represented: 46
- states/provinces represented: 130
