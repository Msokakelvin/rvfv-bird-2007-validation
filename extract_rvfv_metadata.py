from Bio import SeqIO
import csv

INPUT = "rvfv_east_africa_candidates.gb"
OUTPUT = "rvfv_all_metadata.csv"

def get_qualifier(feature, name):
    values = feature.qualifiers.get(name, [])
    return "; ".join(values) if values else ""

rows = []

for record in SeqIO.parse(INPUT, "genbank"):
    source = next(
        (f for f in record.features if f.type == "source"),
        None
    )

    q = source.qualifiers if source else {}

    def value(key):
        vals = q.get(key, [])
        return "; ".join(vals) if vals else ""

    rows.append({
        "accession": record.id,
        "description": record.description,
        "length_bp": len(record.seq),
        "country": value("country"),
        "collection_date": value("collection_date"),
        "host": value("host"),
        "isolate": value("isolate"),
        "strain": value("strain"),
        "segment": value("segment"),
        "isolation_source": value("isolation_source"),
        "organism": value("organism"),
    })

fields = [
    "accession", "description", "length_bp", "country",
    "collection_date", "host", "isolate", "strain",
    "segment", "isolation_source", "organism"
]

with open(OUTPUT, "w", newline="", encoding="utf-8") as handle:
    writer = csv.DictWriter(handle, fieldnames=fields)
    writer.writeheader()
    writer.writerows(rows)

print(f"Records parsed: {len(rows)}")
print(f"Metadata saved to: {OUTPUT}")
print("Review missing country and collection-date fields before filtering.")
