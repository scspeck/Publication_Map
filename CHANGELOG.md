# Changelog

## [0.9.3-development] - 2026-08-20

### Changed
- Restored the dual-handle collection-year slider.
- Distinguished total source parasite records from host-linked parasite records.
- Added transparent accounting for parasite-of relationships lacking resolvable Arctos host GUIDs.
- Added `data/unresolved_host_relationships.csv` for audit instead of inventing host identifiers.

### Record accounting
- Source parasite records: 53,870
- Records containing `parasite of`: 51,505
- Host-linked parasite records: 51,376
- `parasite of` records without resolvable host GUID: 129
- Unique hosts: 30,906
- Host–parasite associations: 51,864

## [0.9.2-development] - 2026-08-20

### Changed
- Replaced verbose geography JSON objects with the compact shared-string relational architecture.
- Country, state/province, locality, taxonomy, and GUID strings are stored once and referenced by integer IDs.
- Preserved Country → State/Province filtering.
- Preserved host-centered map behavior and filtered CSV downloads.
- Preserved parasite-record geographic provenance and future authoritative-host integration plan.

### Result
- `atlas.json`: approximately 8.22 MB uncompressed.

## [0.9.1-development] - 2026-08-20
### Added
- Country filter derived from parasite-record geography.
- Cascading State/Province filter.
- Country, state/province, locality, coordinates, and coordinate uncertainty in filtered CSV exports.
- Explicit documentation of geographic provenance and planned authoritative-host integration.
- Reproducible processor for the newly exported Arctos CSV.

### Data model note
Geography in this release is derived from linked parasite records. Authoritative
host-record integration remains planned for a future release.

## [0.9.0-development] - 2026-08-18

### Added
- Host-centered relational atlas architecture.
- Cascading parasite taxonomy filters from kingdom through species.
- Host group and collection filters.
- Dual-handle collection-year filter with explicit handling of unknown years.
- GUID and taxon search.
- Marker clustering and multiple basemaps.
- Filtered host–parasite association CSV download.
- Dynamic summary counts for parasite records, host records, associations, and host taxa.
- Scholarly documentation, methods, data dictionary, citation metadata, and data-use guidance.

### Known limitation
- Development host coordinates are inferred from linked parasite records rather than authoritative host records.
