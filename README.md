# daft-map-search

Single-page app to build a [daft.ie](https://www.daft.ie) property search URL by
clicking Dublin districts on a map instead of ticking dozens of boxes.

- Leaflet + CARTO Voyager tiles (free, no API key)
- 169 Dublin districts with Daft slug names and real coordinates (geocoded once
  via OpenStreetMap Nominatim)
- d3-delaunay Voronoi cells for click-to-select district catchment areas
- Filters: price, beds, baths, lease length, furnishing, property type,
  facilities, media, keyword, availability, recency, sort, section
- Copy or open the generated multi-area URL

> Unofficial — not affiliated with or endorsed by daft.ie. District Voronoi
> cells are approximate catchment areas, not official neighbourhood boundaries.

## Local

```bash
open index.html
# or serve it
python3 -m http.server 5173
```

## Deploy

The canonical URL is https://daft.mvarge.com. This app has its own Vercel
project, connected to this repository. Cloudflare has a DNS-only CNAME for
`daft` pointing to the project-specific target shown in Vercel's domain settings.

Pure static site. On Vercel:

```bash
vercel --prod
```

or link the repo in the Vercel dashboard — no build command needed.

## Data sources

- Location slugs from
  [TheJokersThief/daft-scraper](https://github.com/TheJokersThief/daft-scraper/blob/main/daft_scraper/search/options_location.py).
- Coordinates in `locations.js` geocoded once via OpenStreetMap Nominatim
  (`scripts/geocode.py` + `scripts/refine.py`); a handful hand-corrected where
  Nominatim disambiguated to the wrong place.
- Daft URL parameters (`rentalPrice_*`, `numBeds_*`, `numBaths_*`,
  `leaseLength_*`, `furnishing`, etc.) validated against live daft.ie search
  URLs.
- A single selected district goes in the URL path. Multiple districts use
  repeated `location` query parameters. Selecting all districts uses the Dublin
  county path to avoid an oversized search URL.
