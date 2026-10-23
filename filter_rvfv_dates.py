import pandas as pd
import re

df = pd.read_csv("rvfv_geographic_metadata.csv").fillna("")

def extract_year(value):
    match = re.search(r"\b(19\d{2}|20\d{2})\b", str(value))
    return int(match.group(1)) if match else None

df["collection_year"] = df["collection_date"].apply(extract_year)

eligible_countries = {
    "Kenya", "Uganda", "Rwanda", "Burundi",
    "Tanzania", "Somalia", "Sudan"
}

df["date_eligible"] = df["collection_year"].between(2005, 2026)
df["country_eligible"] = df["country"].isin(eligible_countries)

eligible = df[df["date_eligible"] & df["country_eligible"]].copy()

eligible.to_csv("rvfv_east_africa_2005_2026_candidates.csv", index=False)

print("All downloaded records:", len(df))
print("Records with interpretable collection years:",
      df["collection_year"].notna().sum())
print("Records from 2005–2026:", df["date_eligible"].sum())
print("East African records from 2005–2026:", len(eligible))

print("\nEligible records by country:")
print(eligible["country"].value_counts().to_string())

print("\nEligible records by year:")
print(eligible["collection_year"].value_counts().sort_index().to_string())

print("\nSaved: rvfv_east_africa_2005_2026_candidates.csv")
