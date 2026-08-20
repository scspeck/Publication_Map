#!/usr/bin/env python3
"""
Build a compact host-centered Kansas Host–Parasite Atlas from an Arctos
parasite-record export.

Release 0.9.2 geography model
-----------------------------
Country, state/province, locality, coordinates, and coordinate uncertainty
are derived from the linked PARASITE record in this interim release.

A future release should retrieve authoritative host records by host GUID
and replace inferred host geography/taxonomy with authoritative host data.

Compact atlas.json structure
----------------------------
s = shared strings
p = parasite metadata
h = host metadata
r = host-parasite relationship rows
summary = release summary

Repeated strings such as country, state/province, locality, taxonomy, and
GUIDs are stored only once in s and referenced by integer ID.
"""
from pathlib import Path
import pandas as pd
import re, json, sys
from collections import Counter

src = Path(sys.argv[1])
out = Path(sys.argv[2]) if len(sys.argv) > 2 else Path("data")
out.mkdir(parents=True, exist_ok=True)

wanted = {
    "GUID","SCIENTIFIC_NAME","COUNTRY","STATE_PROV","SPEC_LOCALITY",
    "VERBATIM_DATE","DEC_LAT","DEC_LONG","COORDINATEUNCERTAINTYINMETERS",
    "ATTRIBUTEDETAIL","KINGDOM","PHYLUM","PHYLCLASS","PHYLORDER","FAMILY",
    "GENUS","SPECIES","RELATEDCATALOGEDITEMS"
}

df = pd.read_csv(
    src,
    usecols=lambda c: c in wanted,
    low_memory=False
)

def clean(x):
    if pd.isna(x):
        return ""
    return str(x).strip()

def explicit_year(x):
    m = re.search(r'(?<!\d)(1[5-9]\d{2}|20\d{2})(?!\d)', clean(x))
    return int(m.group(1)) if m else -1

guid_re = re.compile(r'\b[A-Za-z0-9_.-]+:[A-Za-z0-9_.-]+:\d+\b')

def host_guids(text):
    text = clean(text)
    if not text:
        return []
    found = []
    chunks = re.split(r'[|;\n]+', text)
    for chunk in chunks:
        if re.search(r'parasite\s+of', chunk, re.I):
            found.extend(guid_re.findall(chunk))
    if not found and re.search(r'parasite\s+of', text, re.I):
        found.extend(guid_re.findall(text))
    return list(dict.fromkeys(found))

def safe_attrs(v):
    text = clean(v)
    if not text:
        return []
    try:
        x = json.loads(text)
        return x if isinstance(x, list) else []
    except Exception:
        return []

def first_attr(attrs, name):
    lname = name.lower()
    for a in attrs:
        if str(a.get("attribute_type","")).strip().lower() == lname:
            value = a.get("attribute_value")
            if value not in (None, ""):
                return str(value).strip()
    return ""

# Shared string table.
strings = []
string_to_id = {}

def sid(value):
    value = clean(value)
    if not value:
        return -1
    if value not in string_to_id:
        string_to_id[value] = len(strings)
        strings.append(value)
    return string_to_id[value]

parasites = []
hosts_temp = {}
relationships = []

source_record_count = len(df)
parasite_of_record_count = 0
unresolved_relationship_rows = []

for _, row in df.iterrows():
    pguid = clean(row.get("GUID",""))
    relationship_text = clean(row.get("RELATEDCATALOGEDITEMS",""))

    if re.search(r'parasite\s+of', relationship_text, re.I):
        parasite_of_record_count += 1

    hguids = host_guids(relationship_text)

    # Some Arctos records contain a "parasite of" relationship expressed only
    # as an institutional catalog number, collector number, ARK, or other
    # identifier rather than a resolvable Arctos GUID. We retain an audit list
    # but do not invent a host GUID for those records.
    if pguid and re.search(r'parasite\s+of', relationship_text, re.I) and not hguids:
        unresolved_relationship_rows.append({
            "parasite_guid": pguid,
            "related_cataloged_items": relationship_text
        })

    if not pguid or not hguids:
        continue

    attrs = safe_attrs(row.get("ATTRIBUTEDETAIL",""))

    lat = pd.to_numeric(row.get("DEC_LAT",""), errors="coerce")
    lon = pd.to_numeric(row.get("DEC_LONG",""), errors="coerce")
    unc = pd.to_numeric(row.get("COORDINATEUNCERTAINTYINMETERS",""), errors="coerce")

    lat = None if pd.isna(lat) else round(float(lat), 5)
    lon = None if pd.isna(lon) else round(float(lon), 5)
    unc = None if pd.isna(unc) else round(float(unc), 2)

    # p row positions:
    # 0 guid
    # 1 scientific name
    # 2 kingdom
    # 3 phylum
    # 4 class
    # 5 order
    # 6 family
    # 7 genus
    # 8 species
    # 9 year
    # 10 country
    # 11 state/province
    # 12 locality
    # 13 latitude
    # 14 longitude
    # 15 coordinate uncertainty (m)
    # 16 location in host
    # 17 life stage
    # 18 parasite sex
    # 19 individual count
    pid = len(parasites)
    parasites.append([
        sid(pguid),
        sid(row.get("SCIENTIFIC_NAME","")),
        sid(row.get("KINGDOM","")),
        sid(row.get("PHYLUM","")),
        sid(row.get("PHYLCLASS","")),
        sid(row.get("PHYLORDER","")),
        sid(row.get("FAMILY","")),
        sid(row.get("GENUS","")),
        sid(row.get("SPECIES","")),
        explicit_year(row.get("VERBATIM_DATE","")),
        sid(row.get("COUNTRY","")),
        sid(row.get("STATE_PROV","")),
        sid(row.get("SPEC_LOCALITY","")),
        lat,
        lon,
        unc,
        sid(first_attr(attrs, "location in host")),
        sid(first_attr(attrs, "life stage")),
        sid(first_attr(attrs, "sex")),
        sid(first_attr(attrs, "individual count"))
    ])

    for hg in hguids:
        if hg not in hosts_temp:
            parts = hg.split(":")
            hosts_temp[hg] = {
                "collection": ":".join(parts[:2]) if len(parts) >= 2 else hg,
                "group": parts[1] if len(parts) >= 3 else "",
                "taxa": Counter(),
                "coords": [],
                "countries": Counter(),
                "states": Counter(),
                "localities": Counter()
            }

        ht = hosts_temp[hg]

        host_taxon = first_attr(attrs, "verbatim host ID")
        if host_taxon:
            ht["taxa"][host_taxon] += 1

        if lat is not None and lon is not None:
            ht["coords"].append((lat, lon))

        c = clean(row.get("COUNTRY",""))
        st = clean(row.get("STATE_PROV",""))
        loc = clean(row.get("SPEC_LOCALITY",""))
        if c: ht["countries"][c] += 1
        if st: ht["states"][st] += 1
        if loc: ht["localities"][loc] += 1

        relationships.append([hg, pid])

hosts = []
host_id = {}

for hg, ht in hosts_temp.items():
    hid = len(hosts)
    host_id[hg] = hid

    if ht["coords"]:
        # Representative point for the current interim geography model.
        lat = round(sum(x[0] for x in ht["coords"]) / len(ht["coords"]), 5)
        lon = round(sum(x[1] for x in ht["coords"]) / len(ht["coords"]), 5)
    else:
        lat = lon = None

    taxon = ht["taxa"].most_common(1)[0][0] if ht["taxa"] else ""
    country = ht["countries"].most_common(1)[0][0] if ht["countries"] else ""
    state = ht["states"].most_common(1)[0][0] if ht["states"] else ""
    locality = ht["localities"].most_common(1)[0][0] if ht["localities"] else ""

    # h row positions:
    # 0 guid
    # 1 host taxon (interim: verbatim host ID)
    # 2 collection
    # 3 broad group
    # 4 latitude
    # 5 longitude
    # 6 country
    # 7 state/province
    # 8 locality
    hosts.append([
        sid(hg),
        sid(taxon),
        sid(ht["collection"]),
        sid(ht["group"]),
        lat,
        lon,
        sid(country),
        sid(state),
        sid(locality)
    ])

rels = [[host_id[hg], pid] for hg, pid in relationships]

countries = sorted({
    strings[p[10]] for p in parasites if p[10] != -1
})
states = sorted({
    strings[p[11]] for p in parasites if p[11] != -1
})
years = [p[9] for p in parasites if p[9] != -1]

summary = {
    "source_records": source_record_count,
    "records_with_parasite_of_relationship": parasite_of_record_count,
    "host_linked_parasite_records": len(parasites),
    "parasite_of_relationships_without_resolvable_host_guid":
        len(unresolved_relationship_rows),
    "records_without_resolvable_parasite_of_host_guid":
        source_record_count - len(parasites),
    "unique_hosts": len(hosts),
    "host_parasite_associations": len(rels),
    "unique_host_taxa": len({
        strings[h[1]] for h in hosts if h[1] != -1
    }),
    "countries": len(countries),
    "states_provinces": len(states),
    "min_year": min(years) if years else None,
    "max_year": max(years) if years else None,
    "geography_provenance":
        "Country, state/province, locality, coordinates, and coordinate "
        "uncertainty are derived from linked parasite records in this release.",
    "relationship_provenance":
        "Only parasite-of relationships containing resolvable Arctos-style "
        "host GUIDs are incorporated into the host-centered atlas. Relationships "
        "expressed only through other identifiers are reported separately.",
    "future_development":
        "Retrieve authoritative host records by host GUID and use authoritative "
        "host taxonomy, geography, dates, and additional host metadata."
}

# Write an audit file for parasite-of relationships that cannot currently be
# resolved to an Arctos-style host GUID.
pd.DataFrame(unresolved_relationship_rows).to_csv(
    out/"unresolved_host_relationships.csv",
    index=False
)

atlas = {
    "s": strings,
    "p": parasites,
    "h": hosts,
    "r": rels,
    "summary": summary
}

(out/"atlas.json").write_text(
    json.dumps(atlas, separators=(",",":")),
    encoding="utf-8"
)

(out/"summary.json").write_text(
    json.dumps(summary, indent=2),
    encoding="utf-8"
)

print(json.dumps(summary, indent=2))
