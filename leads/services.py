"""
Business discovery using free OpenStreetMap services.

1. Nominatim geocodes "city, country" into an OSM area (or a bounding box).
2. Overpass returns every named place in that area matching the sector tags.
"""

import re

import requests
from django.conf import settings
from django.db import transaction

from .models import Business, Search
from .sectors import SECTORS


class SearchError(Exception):
    """Raised when a location can't be found or a data source fails."""


def _headers():
    return {"User-Agent": settings.LEADATLAS_USER_AGENT, "Accept-Language": "en"}


def geocode(city, country):
    """Return the best Nominatim match for a city in a country."""
    try:
        response = requests.get(
            settings.NOMINATIM_URL,
            params={"city": city, "country": country, "format": "jsonv2", "limit": 5},
            headers=_headers(),
            timeout=20,
        )
        response.raise_for_status()
        results = response.json()
    except (requests.RequestException, ValueError) as exc:
        raise SearchError(f"Could not reach the geocoding service: {exc}") from exc

    if not results:
        raise SearchError(f"Location not found: {city}, {country}.")
    # Prefer an administrative boundary (relation) so we can search the whole city area.
    relations = [r for r in results if r.get("osm_type") == "relation"]
    return relations[0] if relations else results[0]


def _quote(value):
    return value.replace("\\", "\\\\").replace('"', '\\"')


def build_overpass_query(place, sector_key, keyword="", limit=None):
    sector = SECTORS.get(sector_key)
    if sector is None:
        raise SearchError(f"Unknown sector: {sector_key}")
    limit = limit or settings.LEADATLAS_MAX_RESULTS

    if place.get("osm_type") == "relation":
        area_id = 3600000000 + int(place["osm_id"])
        scope_decl = f"area(id:{area_id})->.searchArea;"
        scope = "(area.searchArea)"
    else:
        south, north, west, east = (float(v) for v in place["boundingbox"])
        scope_decl = ""
        scope = f"({south},{west},{north},{east})"

    name_filter = '["name"]'
    if keyword:
        name_filter += f'["name"~"{_quote(re.escape(keyword))}",i]'

    selectors = []
    for key, value in sector["tags"]:
        tag = f'["{key}"]' if value is None else f'["{key}"="{value}"]'
        selectors.append(f"  nwr{tag}{name_filter}{scope};")

    timeout = settings.OVERPASS_TIMEOUT
    return f"[out:json][timeout:{timeout}];\n{scope_decl}\n(\n" + "\n".join(selectors) + f"\n);\nout center tags {limit};"


def fetch_places(query):
    try:
        response = requests.post(
            settings.OVERPASS_URL,
            data={"data": query},
            headers=_headers(),
            timeout=settings.OVERPASS_TIMEOUT + 15,
        )
        response.raise_for_status()
        return response.json().get("elements", [])
    except requests.HTTPError as exc:
        if exc.response is not None and exc.response.status_code in (429, 504):
            raise SearchError("The OpenStreetMap server is busy. Please retry in a minute.") from exc
        raise SearchError(f"Business search failed: {exc}") from exc
    except (requests.RequestException, ValueError) as exc:
        raise SearchError(f"Could not reach the business search service: {exc}") from exc


def _first(tags, *keys):
    for key in keys:
        if tags.get(key):
            return tags[key].split(";")[0].strip()
    return ""


def _normalize_url(url):
    if url and not url.startswith(("http://", "https://")):
        url = "https://" + url
    return url[:500]


def element_to_fields(element, sector_key, city, country):
    tags = element.get("tags", {})
    lat = element.get("lat") or element.get("center", {}).get("lat")
    lon = element.get("lon") or element.get("center", {}).get("lon")
    street = " ".join(filter(None, [tags.get("addr:housenumber"), tags.get("addr:street")]))
    category = next(
        (tags[k] for k in ("amenity", "shop", "office", "tourism", "leisure", "craft", "industrial") if tags.get(k)),
        "",
    )
    return {
        "name": tags.get("name", "")[:255],
        "sector": sector_key,
        "category": category.replace("_", " ")[:100],
        "country": country[:100],
        "city": (tags.get("addr:city") or city)[:100],
        "address": street[:255],
        "postcode": tags.get("addr:postcode", "")[:20],
        "phone": _first(tags, "phone", "contact:phone", "contact:mobile", "mobile")[:100],
        "email": _first(tags, "email", "contact:email")[:255],
        "website": _normalize_url(_first(tags, "website", "contact:website", "url")),
        "opening_hours": tags.get("opening_hours", "")[:255],
        "latitude": lat,
        "longitude": lon,
    }


def run_search(country, city, sector, keyword=""):
    """Run a search, store/refresh the businesses, and return the Search."""
    place = geocode(city, country)
    elements = fetch_places(build_overpass_query(place, sector, keyword))

    with transaction.atomic():
        search = Search.objects.create(country=country, city=city, sector=sector, keyword=keyword)
        seen = set()
        for element in elements:
            external_id = f"{element['type']}/{element['id']}"
            if external_id in seen or not element.get("tags", {}).get("name"):
                continue
            seen.add(external_id)
            business, _ = Business.objects.update_or_create(
                external_id=external_id,
                defaults=element_to_fields(element, sector, city, country),
            )
            business.searches.add(search)
        search.result_count = len(seen)
        search.save(update_fields=["result_count"])
    return search
