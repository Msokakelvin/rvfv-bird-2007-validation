from Bio import SeqIO
from collections import Counter, defaultdict
from datetime import date
import csv
import re

INPUT = "rvfv_east_africa_candidates.gb"
OUTPUT = "rvfv_date_audit.csv"

START_YEAR = 2005
END_DATE = date(2026, 10, 21)

def get_value(q, *keys):
    for key in keys:
        values = q.get(key, [])
        if values:
            return "; ".join(values)
    return ""

def parse_date(raw):
    """Extract year information without silently losing raw metadata."""
    raw = (raw or "").strip()

    if not raw:
        return None, None, "MISSING"

    # GenBank dates can contain a single year or a year range.
    years = [
        int(y) for y in re.findall(r"\b(?:19|20)\d{2}\b", raw)
    ]

    if not years:
        return None, None, "UNRECOGNIZED"

    first_year = min(years)
    last_year = max(years)

    # Check for common exact date formats.
    exact_formats = [
        "%Y-%m-%d",
        "%d-%b-%Y",
        "%d-%B-%Y",
        "%Y/%m/%d",
        "%d/%m/%Y",
        "%m/%d/%Y",
    ]

    for fmt in exact_formats:
        try:
            parsed = date.fromisoformat(raw) if fmt == "%Y-%m-%d" else None
            if parsed is None:
                from datetime import datetime
                parsed = datetime.strptime(raw, fmt).date()
            return parsed.year, parsed.year, "EXACT_DATE"
        except ValueError:
            pass

    if first_year != last_year:
        return first_year, last_year, "YEAR_RANGE"

    # Year-only and partial dates are retained but clearly flagged.
    if re.fullmatch(r"\d{4}", raw):
        return first_year, last_year, "YEAR_ONLY"

    return first_year, last_year, "PARTIAL_OR_OTHER"

rows = []

for record in SeqIO.parse(INPUT, "genbank"):
    source = next(
        (f for f in record.features if f.type == "source"),
        None
    )
    q = source.qualifiers if source else {}

    location = get_value(q, "geo_loc_name", "country")
    raw_date = get_value(q, "collection_date")

    start_year, end_year, date_status = parse_date(raw_date)

    country = location.split(":")[0].strip() if location else ""

    if not raw_date:
        eligibility = "REVIEW_MISSING_DATE"
    elif start_year is None:
        eligibility = "REVIEW_UNRECOGNIZED_DATE"
    elif end_year < START_YEAR or start_year > END_DATE.year:
        eligibility = "OUTSIDE_YEAR_RANGE"
    else:
        eligibility = "CANDIDATE_2005_2026"

    rows.append({
        "accession": record.id,
        "description": record.description,
        "length_bp": len(record.seq),
        "geo_loc_name": location,
        "country": country,
        "collection_date_raw": raw_date,
        "year_start": start_year if start_year is not None else "",
        "year_end": end_year if end_year is not None else "",
        "date_status": date_status,
        "host": get_value(q, "host"),
        "segment": get_value(q, "segment"),
        "eligibility": eligibility,
    })

fields = list(rows[0].keys()) if rows else []

with open(OUTPUT, "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=fields)
    writer.writeheader()
    writer.writerows(rows)

print("TOTAL RECORDS:", len(rows))

print("\nDATE ANNOTATION STATUS:")
for key, count in Counter(r["date_status"] for r in rows).most_common():
    print(f"{key}: {count}")

print("\nCOUNTRY COUNTS:")
for key, count in Counter(
    r["country"] or "MISSING" for r in rows
).most_common():
    print(f"{key}: {count}")

print("\nTANZANIA RECORDS — ORIGINAL DATES:")
tz = [r for r in rows if r["country"].lower() == "tanzania"]
if not tz:
    print("No Tanzania records found in geo_loc_name/country.")
else:
    for r in tz:
        print(
            r["accession"],
            "| date:", r["collection_date_raw"] or "MISSING",
            "| parsed:", r["year_start"], "-", r["year_end"],
            "| status:", r["date_status"],
            "| segment:", r["segment"] or "MISSING",
            "| eligibility:", r["eligibility"]
        )

print("\nCANDIDATE COUNTS BY COUNTRY:")
candidate = [
    r for r in rows
    if r["eligibility"] == "CANDIDATE_2005_2026"
]
for key, count in Counter(
    r["country"] or "MISSING" for r in candidate
).most_common():
    print(f"{key}: {count}")

print("\nSaved full audit to:", OUTPUT)
