# Methods and Technical Architecture

## Overview

The Kansas State Biorepository Host-Parasite Atlas uses a host-centered relational model to visualize museum-vouchered host–parasite associations. The web application is static and browser-based; preprocessing is performed before deployment, so the user does not need to query the source collection database for every interaction.

## Source records

The development workflow begins with an Arctos export of parasite specimen records containing specimen GUIDs, taxonomic fields, collection dates, coordinates, related-cataloged-item relationships, and selected specimen attributes. The processing script identifies relationships explicitly labeled `parasite of` and uses the related GUID as the host identifier.

Data acquisition. Parasite specimens were downloaded from the Museum of Southwestern Biology Parasite Collection (MSB:Para) through Arctos on 8/20/2026. The Arctos catalog search was restricted to only records within MSB:Para, with no additional taxonomic restrictions. The resulting export contained 53,870 parasite specimen records. Exported fields are listed within "Data_Dictionary.md". Records were not excluded from the source export; during the subsequent processing, only records containing an explicit `parasite of` relationship with a resolvable Arctos host GUID were incorporated into the atlas. Of the 53,870 source records, 51,505 contained a `parasite of` relationship, 51,376 could be resolved to an Arctos host GUID, and 129 contained a `parasite of` relationship without a resolvable host GUID. Records lacking a resolvable host GUID were retained in an audit table but not mapped as host-parasite associations.

## Host-parasite relationships

A host-parasite association is retained when a parasite record contains an Arctos related-cataloged-item relationship identified as `parasite of`. Host and parasite GUIDs are preserved as persistent record identifiers in the derived atlas dataset.

## Taxonomy

Parasite taxonomy is retained at kingdom, phylum, class, order, family, genus, and species where available. The browser interface implements cascading taxonomic filters: selection of a higher rank restricts available lower-rank values to combinations represented in the loaded dataset.

Host taxon labels in the development dataset are obtained from the `verbatim host ID` attribute associated with parasite records. For a production release, authoritative host identifications should be preferred where available and the taxonomic source should be documented explicitly.

## Temporal data

The processing script extracts an explicit four-digit year from the verbatim date field. Records without an explicit four-digit year are assigned an unknown-year state rather than having a century inferred. The interface allows users to include or exclude records with unknown years.

## Spatial data

In the development dataset, host coordinates are inferred from coordinates associated with linked parasite records. When multiple linked parasite coordinates are available for a host, the processing script currently derives a representative host coordinate from those linked values.

## Compact representation

To reduce browser transfer size, repeated strings are stored in a shared string dictionary. Parasite, host, and relationship tables then reference those strings by integer identifier. The resulting `atlas.json` contains:

- `s`: shared strings;
- `m`: parasite metadata;
- `h`: host metadata; and
- `r`: host–parasite relationships.

The JavaScript decoder functions in `index.html` must remain synchronized with the positional field order written by `process_compact_atlas.py`.

## Map behavior

Each mapped marker represents one host record with mappable coordinates. Marker clustering is used to improve rendering and readability at broad map scales. Parasite filters act on the set of linked parasite records; a host is displayed when at least one linked parasite satisfies the active parasite and temporal filters in addition to the host-level filters.

## Filtered export

The browser can generate a CSV from the active filters without requiring a server-side process. Each output row represents one host–parasite association and includes host identifiers, host taxon and collection, coordinates, parasite identifiers and taxonomy, collection year, and selected parasite attributes.

## Interim geographic filtering (release 0.9.1)

For the current development release, geographic metadata used for map display and
geographic filtering were obtained from the parasite record fields `COUNTRY`,
`STATE_PROV`, `SPEC_LOCALITY`, `DEC_LAT`, `DEC_LONG`, and
`COORDINATEUNCERTAINTYINMETERS`. A parasite record was associated with a host
through the cataloged `parasite of` relationship and host GUID. Country and
State/Province filters therefore select associations using geography recorded for
the linked parasite specimen.

This approach is an interim implementation necessitated by the scale of retrieving
tens of thousands of authoritative host records. It should not be interpreted as
independent validation of host locality metadata. Future development will retrieve
authoritative host records by GUID and join host-level taxonomy, locality, date,
and georeferencing metadata directly to the relational dataset.


## Relationship resolution

Only explicit `parasite of` relationships containing a resolvable Arctos-style
host GUID are incorporated into the host-centered relational dataset. Records in
which the relationship is expressed only through another identifier are retained
in an audit table rather than being assigned an inferred or constructed GUID.
This distinction allows the complete source-record accounting to remain
transparent and prevents unverified host identities from entering the map.
