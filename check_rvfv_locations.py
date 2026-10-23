from Bio import SeqIO
from collections import Counter

gb_file = "rvfv_east_africa_candidates.gb"

location_counts = Counter()
examples = []

for record in SeqIO.parse(gb_file, "genbank"):
    source = next(
        (f for f in record.features if f.type == "source"),
        None
    )

    qualifiers = source.qualifiers if source else {}

    location = (
        qualifiers.get("geo_loc_name", [])
        or qualifiers.get("country", [])
    )

    if location:
        location_counts.update(location)
        if len(examples) < 15:
            examples.append((record.id, location[0]))
    else:
        location_counts["MISSING"] += 1

print("Location annotation counts:")
for location, count in location_counts.most_common():
    print(f"{location}: {count}")

print("\nExample accession-location pairs:")
for accession, location in examples:
    print(accession, "->", location)
