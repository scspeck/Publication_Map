# Publication Release Checklist

Use this checklist before creating the version cited by a manuscript.

- [ ] Replace the development dataset with the intended publication dataset.
- [ ] Resolve host coordinates from authoritative host records, or document the retained inference method explicitly.
- [ ] Record the Arctos query/export date, collections, fields, and inclusion/exclusion criteria in `METHODS.md`.
- [ ] Verify taxonomic provenance for host names and parasite ranks.
- [ ] Validate a random sample of host–parasite relationships against Arctos.
- [ ] Check duplicate GUIDs and duplicate associations.
- [ ] Check coordinate ranges and obvious geographic outliers.
- [ ] Confirm handling of missing/ambiguous collection dates.
- [ ] Confirm map-filter results equal filtered-download results for several test cases.
- [ ] Confirm all external basemap/library attributions display correctly.
- [ ] Add project authors, affiliations, ORCIDs, and corresponding-author email to `CITATION.cff`.
- [ ] Decide and document the data license/terms separately from the software license.
- [ ] Update the release version and date in `index.html`, `CITATION.cff`, and `CHANGELOG.md`.
- [ ] Create a tagged GitHub release.
- [ ] Archive the release in a DOI-issuing repository and add the DOI to `CITATION.cff` and `README.md`.
- [ ] Cite the frozen DOI-backed release in the manuscript rather than only the live website.
