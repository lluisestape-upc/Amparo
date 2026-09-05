"""Find the real food bank closest to the applicant.

Deliberately NOT asked of the language model. Sending a vulnerable person to an
address that a model invented is worse than telling them nothing, so every place
here comes from OpenStreetMap, and when nothing is found we say nothing.
"""

from math import asin, cos, radians, sin, sqrt

import requests

AGENT = {"User-Agent": "Amparo/1.0 (aid application assistant)"}
NOMINATIM = "https://nominatim.openstreetmap.org/search"
OVERPASS = "https://overpass-api.de/api/interpreter"
RADIUS_M = 8000

_cache: dict[str, dict | None] = {}


def _km(lat1, lon1, lat2, lon2) -> float:
    dlat, dlon = radians(lat2 - lat1), radians(lon2 - lon1)
    a = sin(dlat / 2) ** 2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon / 2) ** 2
    return 2 * 6371 * asin(sqrt(a))


def _geocode(address: str):
    r = requests.get(
        NOMINATIM,
        params={"q": address, "format": "json", "limit": 1},
        headers=AGENT, timeout=15,
    )
    hits = r.json()
    return (float(hits[0]["lat"]), float(hits[0]["lon"])) if hits else None


def _food_banks(lat: float, lon: float) -> list[dict]:
    query = f"""[out:json][timeout:25];
    (node[social_facility=food_bank](around:{RADIUS_M},{lat},{lon});
     way[social_facility=food_bank](around:{RADIUS_M},{lat},{lon});
     node[amenity=social_facility][social_facility~"food"](around:{RADIUS_M},{lat},{lon});
     way[amenity=social_facility][social_facility~"food"](around:{RADIUS_M},{lat},{lon}););
    out center 25;"""
    r = requests.post(OVERPASS, data={"data": query}, headers=AGENT, timeout=45)

    places = []
    for el in r.json().get("elements", []):
        tags = el.get("tags", {})
        name = tags.get("name")
        if not name:
            continue                     # an unnamed pin helps nobody
        centre = el.get("center") or el
        plat, plon = centre.get("lat"), centre.get("lon")
        if plat is None:
            continue
        street = " ".join(
            p for p in (tags.get("addr:street"), tags.get("addr:housenumber")) if p
        )
        places.append({
            "name": name,
            "address": street,
            "km": round(_km(lat, lon, plat, plon), 1),
        })
    return sorted(places, key=lambda p: p["km"])


def nearest(address: str) -> dict | None:
    """The closest named food bank to `address`, or None if we cannot be sure."""
    key = address.strip().lower()
    if not key:
        return None
    if key in _cache:
        return _cache[key]

    place = None
    try:
        point = _geocode(address)
        if point:
            found = _food_banks(*point)
            place = found[0] if found else None
    except Exception:
        place = None                     # offline, rate-limited, malformed — stay quiet

    _cache[key] = place
    return place
