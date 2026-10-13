# LeadAtlas

Find businesses by **country**, **city** and **sector (secteur d'activité)**, save them as leads,
track your outreach, and export to CSV.

Business data comes from [OpenStreetMap](https://www.openstreetmap.org) — free, no API key needed:

1. **Nominatim** turns "city, country" into a map area.
2. **Overpass API** returns every named business in that area for the chosen sector
   (name, address, phone, email, website, opening hours, GPS).

## Features

- 40+ sectors: restaurants, hotels, pharmacies, doctors, dentists, lawyers, accountants,
  real estate, IT companies, garages, hairdressers, gyms, banks, schools, craftsmen, factories…
- Optional "name contains" keyword filter
- Results on a map + table; filter by phone / website / email / status
- Lead tracking: status (New → Contacted → Interested → Client) and notes
- CSV export (Excel-friendly, UTF-8)
- Search history, one-click refresh, Django admin

## Run locally

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python manage.py migrate
python manage.py createsuperuser   # optional, for /admin
python manage.py runserver
```

Open http://127.0.0.1:8000.

Run the tests with `python manage.py test`.

## Deploy (Render)

The repo includes `render.yaml` (web service + free PostgreSQL). On [Render](https://render.com):
**New → Blueprint →** pick this repo. It runs `build.sh` (install, collectstatic, migrate) and
starts gunicorn. Any host that supports a `Procfile` (Railway, Heroku…) works too; set
`SECRET_KEY`, `DEBUG=False`, `ALLOWED_HOSTS`, `CSRF_TRUSTED_ORIGINS` and `DATABASE_URL`.

## Adding a sector

Edit `leads/sectors.py` and add an entry with the matching
[OpenStreetMap tags](https://wiki.openstreetmap.org/wiki/Map_features).

## Notes

- OpenStreetMap coverage varies by country; phone/website are only present when mapped.
- The public Overpass/Nominatim servers are rate-limited — be gentle, one search at a time.
- Data © OpenStreetMap contributors, ODbL.
