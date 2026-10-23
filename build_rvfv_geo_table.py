from Bio import SeqIO
import csv

INPUT = "rvfv_east_africa_candidates.gb"
OUTPUT = "rvfv_geographic_metadata.csv"

rows = []

for record in SeqIO.parse(INPUT, "genbank"):
    source = next(
        (f for f in record.features if f.type == "source"),
        None
    )
    q = source.qualifiers if source else {}

    def first(*keys):
        for key in keys:
            values = q.get(key, [])
            if values:
                return "; ".join(values)
        return ""

    geo = first("geo_loc_name", "country")

    rows.append({
        "accession": record.id,
        "length_bp": len(record.seq),
        "geo_loc_name": geo,
        "country": geo.split(":")[0].strip() if geo else "",
        "collection_date": first("collection_date"),
        "host": first("host"),
        "isolate": first("isolate"),
        "strain": first("strain"),
        "segment": first("segment"),
    })

fields = list(rows[0].keys()) if rows else []

with open(OUTPUT, "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=fields)
    writer.writeheader()
    writer.writerows(rows)

print(f"Saved {len(rows)} records to {OUTPUT}")
