#!/usr/bin/env python3
"""
Build the compact Kansas Host–Parasite Atlas from an Arctos parasite export.

CURRENT GEOGRAPHY MODEL
Country/state/locality/coordinates are taken from the PARASITE record.
They provide geographic context for the host–parasite association. They are
not independently retrieved authoritative host metadata. A future release
should join host GUIDs to authoritative host records.
"""
from pathlib import Path
import pandas as pd
import re, json, sys

src = Path(sys.argv[1])
out = Path(sys.argv[2]) if len(sys.argv) > 2 else Path("data")
out.mkdir(parents=True, exist_ok=True)

usecols = [
    "GUID","SCIENTIFIC_NAME","COUNTRY","STATE_PROV","SPEC_LOCALITY",
    "VERBATIM_DATE","DEC_LAT","DEC_LONG","COORDINATEUNCERTAINTYINMETERS",
    "ATTRIBUTEDETAIL","KINGDOM","PHYLUM","PHYLCLASS","PHYLORDER","FAMILY",
    "GENUS","SPECIES","RELATEDCATALOGEDITEMS"
]
df = pd.read_csv(src, usecols=lambda c: c in usecols, low_memory=False).fillna("")

def clean(x):
    return str(x).strip()

def year_from(x):
    m = re.search(r'(?<!\d)(1[5-9]\d{2}|20\d{2})(?!\d)', clean(x))
    return int(m.group(1)) if m else None

# Robustly find host GUID(s) associated with "parasite of".
guid_re = re.compile(r'\b[A-Za-z0-9_.-]+:[A-Za-z0-9_.-]+:\d+\b')
def host_guids(text):
    text = clean(text)
    if not text:
        return []
    found = []
    # Split common Arctos multi-relationship delimiters, but fall back to
    # searching the entire field when needed.
    chunks = re.split(r'[|;\n]+', text)
    for chunk in chunks:
        if re.search(r'parasite\s+of', chunk, re.I):
            found.extend(guid_re.findall(chunk))
    if not found and re.search(r'parasite\s+of', text, re.I):
        found.extend(guid_re.findall(text))
    return list(dict.fromkeys(found))

# Attribute helpers: preserve the complete attribute text while extracting
# commonly used parasite-specific values when their labels are present.
def attr_value(text, labels):
    text = clean(text)
    for lab in labels:
        m = re.search(rf'(?:^|[|;])\s*{re.escape(lab)}\s*[:=]\s*([^|;]+)', text, re.I)
        if m:
            return m.group(1).strip()
    return ""

parasites = []
hosts = {}
relations = []

for _, row in df.iterrows():
    p_guid = clean(row.get("GUID",""))
    hguids = host_guids(row.get("RELATEDCATALOGEDITEMS",""))
    if not p_guid or not hguids:
        continue

    p = {
        "guid": p_guid,
        "name": clean(row.get("SCIENTIFIC_NAME","")),
        "kingdom": clean(row.get("KINGDOM","")),
        "phylum": clean(row.get("PHYLUM","")),
        "class": clean(row.get("PHYLCLASS","")),
        "order": clean(row.get("PHYLORDER","")),
        "family": clean(row.get("FAMILY","")),
        "genus": clean(row.get("GENUS","")),
        "species": clean(row.get("SPECIES","")),
        "year": year_from(row.get("VERBATIM_DATE","")),
        "country": clean(row.get("COUNTRY","")),
        "state_province": clean(row.get("STATE_PROV","")),
        "locality": clean(row.get("SPEC_LOCALITY","")),
        "latitude": pd.to_numeric(row.get("DEC_LAT",""), errors="coerce"),
        "longitude": pd.to_numeric(row.get("DEC_LONG",""), errors="coerce"),
        "coordinate_uncertainty_m": pd.to_numeric(row.get("COORDINATEUNCERTAINTYINMETERS",""), errors="coerce"),
        "location_in_host": attr_value(row.get("ATTRIBUTEDETAIL",""), ["location in host","location"]),
        "life_stage": attr_value(row.get("ATTRIBUTEDETAIL",""), ["life stage"]),
        "sex": attr_value(row.get("ATTRIBUTEDETAIL",""), ["sex"]),
        "individual_count": attr_value(row.get("ATTRIBUTEDETAIL",""), ["individual count","count"]),
        "attribute_detail": clean(row.get("ATTRIBUTEDETAIL",""))
    }
    # JSON cannot contain NaN.
    for k in ("latitude","longitude","coordinate_uncertainty_m"):
        if pd.isna(p[k]): p[k] = None

    pid = len(parasites)
    parasites.append(p)

    for hg in hguids:
        h = hosts.setdefault(hg, {
            "guid": hg,
            "collection": ":".join(hg.split(":")[:2]) if ":" in hg else "",
            "group": hg.split(":")[1] if hg.count(":") >= 2 else "",
            "taxon": "",
            "latitude": None, "longitude": None,
            "country": "", "state_province": "", "locality": ""
        })
        # Interim host display geography is inferred from the linked parasite.
        if h["latitude"] is None and p["latitude"] is not None:
            h["latitude"], h["longitude"] = p["latitude"], p["longitude"]
        if not h["country"]: h["country"] = p["country"]
        if not h["state_province"]: h["state_province"] = p["state_province"]
        if not h["locality"]: h["locality"] = p["locality"]
        relations.append([hg, pid])

host_list = list(hosts.values())
hid = {h["guid"]: i for i,h in enumerate(host_list)}
rel = [[hid[hg], pid] for hg,pid in relations]

atlas = {"hosts":host_list, "parasites":parasites, "relations":rel}
(out/"atlas.json").write_text(json.dumps(atlas, separators=(",",":")), encoding="utf-8")

summary = {
    "source_file": src.name,
    "parasite_records_with_host_relationships": len(parasites),
    "unique_hosts": len(host_list),
    "host_parasite_associations": len(rel),
    "countries": sorted({p["country"] for p in parasites if p["country"]}),
    "states_provinces": sorted({p["state_province"] for p in parasites if p["state_province"]}),
    "geography_provenance": "Country, state/province, locality and coordinates are derived from linked parasite records in this release.",
    "future_development": "Join host GUIDs to authoritative host records and use authoritative host taxonomy and geography."
}
(out/"summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
print(json.dumps(summary, indent=2))
