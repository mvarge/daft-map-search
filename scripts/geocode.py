#!/usr/bin/env python3
"""
Geocode Dublin Daft location slugs via OpenStreetMap Nominatim.

Reads the `name` fields from locations.js, queries Nominatim for
"<name>, Dublin, Ireland", and writes results to geocoded.json.

Respects Nominatim usage policy: 1 request/second, descriptive User-Agent.
Run once, offline. Output is reviewed by hand before patching locations.js.
"""
import json
import re
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path

HERE = Path(__file__).resolve().parent
LOCATIONS_JS = HERE.parent / "locations.js"
OUT = HERE / "geocoded.json"

NOMINATIM = "https://nominatim.openstreetmap.org/search"
UA = "daft-map-search/1.0 (https://github.com/mvarge/daft-map-search; geocoding one-time)"


def parse_locations(js_text: str):
    """Extract slug + name + existing lat/lng from the JS array."""
    entries = []
    pat = re.compile(
        r'\{\s*slug:\s*"([^"]+)"\s*,\s*name:\s*"([^"]+)"\s*,\s*lat:\s*([\d.]+)\s*,\s*lng:\s*(-?[\d.]+)'
    )
    for m in pat.finditer(js_text):
        slug, name, lat, lng = m.groups()
        entries.append({
            "slug": slug,
            "name": name,
            "old_lat": float(lat),
            "old_lng": float(lng),
        })
    return entries


def geocode(query: str):
    params = urllib.parse.urlencode({
        "q": query,
        "format": "jsonv2",
        "limit": 1,
        "countrycodes": "ie",
        "addressdetails": 0,
    })
    req = urllib.request.Request(f"{NOMINATIM}?{params}", headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=30) as resp:
        data = json.load(resp)
    if not data:
        return None
    top = data[0]
    return {"lat": float(top["lat"]), "lng": float(top["lon"]), "display": top.get("display_name", "")}


def haversine_km(a_lat, a_lng, b_lat, b_lng):
    from math import radians, sin, cos, asin, sqrt
    R = 6371
    dlat = radians(b_lat - a_lat)
    dlng = radians(b_lng - a_lng)
    x = sin(dlat/2)**2 + cos(radians(a_lat))*cos(radians(b_lat))*sin(dlng/2)**2
    return 2 * R * asin(sqrt(x))


def main():
    js_text = LOCATIONS_JS.read_text()
    entries = parse_locations(js_text)
    print(f"Parsed {len(entries)} locations from locations.js", file=sys.stderr)

    results = []
    for i, e in enumerate(entries, 1):
        # Dublin coastal + city suburbs — bias query to Dublin, Ireland
        query = f"{e['name']}, Dublin, Ireland"
        try:
            hit = geocode(query)
        except Exception as ex:
            hit = None
            print(f"[{i}/{len(entries)}] {e['slug']}: ERROR {ex}", file=sys.stderr)

        rec = dict(e)
        if hit:
            drift = haversine_km(e["old_lat"], e["old_lng"], hit["lat"], hit["lng"])
            rec.update({
                "new_lat": round(hit["lat"], 5),
                "new_lng": round(hit["lng"], 5),
                "display": hit["display"],
                "drift_km": round(drift, 2),
                "status": "ok",
            })
            flag = "  <-- LARGE DRIFT" if drift > 3 else ""
            print(f"[{i}/{len(entries)}] {e['slug']}: {hit['lat']:.4f},{hit['lng']:.4f} drift={drift:.2f}km{flag}", file=sys.stderr)
        else:
            rec.update({"status": "not_found"})
            print(f"[{i}/{len(entries)}] {e['slug']}: NOT FOUND", file=sys.stderr)

        results.append(rec)
        time.sleep(1.1)  # Nominatim policy: max 1 req/sec

    OUT.write_text(json.dumps(results, indent=2))
    print(f"\nWrote {OUT}", file=sys.stderr)

    # Summary
    ok = [r for r in results if r["status"] == "ok"]
    nf = [r for r in results if r["status"] != "ok"]
    big = [r for r in ok if r.get("drift_km", 0) > 3]
    print(f"OK: {len(ok)}  Not found: {len(nf)}  Large drift (>3km): {len(big)}", file=sys.stderr)


if __name__ == "__main__":
    main()
