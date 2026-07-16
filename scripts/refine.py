#!/usr/bin/env python3
"""
Refine the geocodes that resolved to a business/road instead of the place.

Re-queries a fixed list of slugs using Nominatim's featureType=settlement,
which prefers town/village/suburb records over POIs and streets. Writes the
corrections back into geocoded.json (status -> "ok_refined").
"""
import json
import time
import urllib.parse
import urllib.request
from pathlib import Path

HERE = Path(__file__).resolve().parent
GEO = HERE / "geocoded.json"
NOMINATIM = "https://nominatim.openstreetmap.org/search"
UA = "daft-map-search/1.0 (https://github.com/mvarge/daft-map-search; geocoding one-time)"

# slugs to redo -> the query string to use
REDO = {
    "rush-dublin": "Rush, County Dublin, Ireland",
    "naul-dublin": "Naul, County Dublin, Ireland",
    "oldtown-dublin": "Oldtown, County Dublin, Ireland",
    "citywest-dublin": "Citywest, County Dublin, Ireland",
    "swords-dublin": "Swords, County Dublin, Ireland",
    "cloghran-dublin": "Cloghran, County Dublin, Ireland",
    "malahide-dublin": "Malahide, County Dublin, Ireland",
    "dublin-city-centre-dublin": "Dublin City Centre, Dublin, Ireland",
    "huntstown-dublin": "Huntstown, Dublin, Ireland",
    "damastown-dublin": "Damastown, County Dublin, Ireland",
    "tyrrelstown-dublin": "Tyrrelstown, County Dublin, Ireland",
    "cherry-orchard-dublin": "Cherry Orchard, Dublin, Ireland",
    "strawberry-beds-dublin": "Strawberry Beds, County Dublin, Ireland",  # was not_found
}


def geocode(query, feature_type="settlement"):
    params = {
        "q": query,
        "format": "jsonv2",
        "limit": 1,
        "countrycodes": "ie",
    }
    if feature_type:
        params["featureType"] = feature_type
    req = urllib.request.Request(
        f"{NOMINATIM}?{urllib.parse.urlencode(params)}", headers={"User-Agent": UA}
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        data = json.load(resp)
    if not data:
        return None
    t = data[0]
    return {"lat": float(t["lat"]), "lng": float(t["lon"]), "display": t.get("display_name", "")}


def main():
    recs = json.load(open(GEO))
    by_slug = {r["slug"]: r for r in recs}

    for slug, query in REDO.items():
        rec = by_slug.get(slug)
        if not rec:
            print(f"?? {slug} not in geocoded.json")
            continue
        hit = geocode(query, "settlement")
        if not hit:
            # fall back to no featureType
            time.sleep(1.1)
            hit = geocode(query, None)
        if hit:
            rec["new_lat"] = round(hit["lat"], 5)
            rec["new_lng"] = round(hit["lng"], 5)
            rec["display"] = hit["display"]
            rec["status"] = "ok_refined"
            print(f"{slug:28} -> {hit['lat']:.4f},{hit['lng']:.4f}  {hit['display'][:60]}")
        else:
            print(f"{slug:28} -> STILL NOT FOUND")
        time.sleep(1.1)

    json.dump(recs, open(GEO, "w"), indent=2)
    print("\nUpdated geocoded.json")


if __name__ == "__main__":
    main()
