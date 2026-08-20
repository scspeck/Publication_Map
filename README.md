# Kansas State Biorepository Host-Parasite Atlas

The **Kansas State Biorepository Host-Parasite Atlas** is an interactive, specimen-based web resource for exploring associations between museum-vouchered hosts and independently cataloged parasite records. The atlas is designed as a discovery, visualization, and reproducible filtering interface while preserving links to the underlying natural history collection records.

## Scientific purpose

Natural history collections preserve information about organisms across geography and time, but host and parasite records are often cataloged as separate objects. This atlas provides a host-centered interface for exploring those relational data. It is intended to support specimen discovery, visualization of geographic and temporal patterns, exploration of host–parasite associations, and reproducible selection of records for subsequent research.

The atlas is **not** an estimator of host abundance, parasite prevalence, parasite intensity, or biological absence unless the underlying sampling design independently supports those inferences.

## How to interpret the map

Each map point represents **one host record**. Parasite records are linked to hosts through cataloged specimen relationships. Selecting a parasite taxon therefore retains hosts having at least one linked parasite record that satisfies the active filters; parasite records are not plotted as independent occurrence points in this host-centered view.

Parasite taxonomy can be filtered hierarchically from kingdom through species. Additional controls allow filtering by host group, host collection, host taxon, collection year, and GUID/taxon text.

## Data provenance

The atlas is built from specimen metadata exported from **Arctos**. Arctos and the contributing natural history collections remain the authoritative sources for specimen information. The atlas is a derived visualization and discovery product and does not replace the corresponding source records.

Every downloadable association retains host and parasite GUIDs so that records can be traced back to their source specimen records.

## Processing workflow

The reproducible workflow is:

```text
Arctos specimen export
        |
        v
scripts/process_compact_atlas.py
        |
        v
data/atlas.json + data/summary.json
        |
        v
index.html
        |
        v
interactive host-centered atlas
```

`process_compact_atlas.py` parses host–parasite relationships, extracts parasite taxonomy and selected specimen attributes, consolidates linked records by host GUID, and writes a compact relational JSON representation for the browser.

### Compact data architecture

`data/atlas.json` contains four principal arrays:

- `s` — shared string dictionary;
- `m` — parasite metadata;
- `h` — host metadata; and
- `r` — host–parasite relationship records.

Repeated text is stored once in `s` and referenced by integer identifier. This substantially reduces file size relative to a verbose GeoJSON representation while preserving the relational structure required by the atlas.

## Filtered data download

The **Download Filtered Data** button exports the host–parasite associations satisfying the active filters. Each CSV row represents one host–parasite association. Parasites linked to a visible host but failing the active parasite taxonomy or year filters are excluded from the download.

The downloaded table is intended for transparent record selection and downstream analysis. Researchers should consult the linked source records before analyses requiring current identifications, complete locality metadata, coordinate uncertainty, restrictions, or other fields not represented in the atlas export.

See [`DATA_DICTIONARY.md`](DATA_DICTIONARY.md) for field definitions.

## Known limitations

Museum data are shaped by collecting effort, sampling design, geography, time, digitization history, taxonomic practice, and collection-specific workflows. Consequently:

- record density should not be interpreted directly as organismal abundance;
- parasite-record frequency should not be interpreted directly as prevalence or intensity;
- absence of a record should not be interpreted as biological absence;
- taxonomic identifications may change after an atlas release is generated; and
- source records may be corrected or augmented after the atlas snapshot is created.

## Reproducibility and versioning

A publication-associated release should be frozen and versioned rather than allowing the paper to point only to a continuously changing website. Recommended release procedure:

1. generate the final dataset from a documented Arctos export;
2. record the export/retrieval date and query criteria;
3. update `CHANGELOG.md` and the release identifier;
4. create a tagged repository release (for example, `v1.0.0`);
5. archive that release in a DOI-issuing repository such as Zenodo; and
6. cite the archived release in the manuscript.

The live atlas may continue to receive updates after publication, while the archived release preserves the exact software and data snapshot used in the paper.

## Repository structure

```text
.
├── index.html
├── README.md
├── DATA_DICTIONARY.md
├── METHODS.md
├── DATA_USE.md
├── CITATION.cff
├── CHANGELOG.md
├── LICENSE
├── data/
│   ├── atlas.json
│   └── summary.json
└── scripts/
    └── process_compact_atlas.py
```

## Software

The web application uses Leaflet, Leaflet.markercluster, and noUiSlider. Data preprocessing is performed in Python with pandas. The application is designed for static hosting, including GitHub Pages.

## Citation

A machine-readable citation template is provided in `CITATION.cff`. Replace the placeholder publication metadata and DOI when the atlas software/data paper and archived release are available.

When using specimen information, researchers should also cite or acknowledge the contributing collections and source records as appropriate for their analysis.

## Data and software licensing

The source code in this repository is released under the MIT License. This software license does **not** relicense specimen data obtained from Arctos or contributing collections. See `DATA_USE.md` for data-use guidance.

## Contact

Kansas State University Biorepository  
Kansas State University

