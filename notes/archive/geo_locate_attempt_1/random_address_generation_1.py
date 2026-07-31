"""
build_address_cache.py

Generates random real-world address entries for the world-address guessing game.

Process:
1. Pick a random latitude/longitude uniformly on Earth's surface.
2. Reject the point if it is not inside a country polygon.
3. Find a nearby city/town/village using Overpass.
4. Find a random OSM address near that place using Overpass.
5. Reverse-geocode the address using Nominatim.
6. Search/geocode the city using Nominatim to get city center and bounding box.
7. Save successful addresses in the same shape as the browser game's
   FALLBACK_ADDRESSES array.

Output object format:

{
  "continent": "Europe",
  "country": "France",
  "iso3": "FRA",
  "state": "Île-de-France",
  "city": "Paris",
  "street": "5 Avenue Anatole France",
  "lat": 48.85837,
  "lng": 2.294481,
  "cityLat": 48.8566,
  "cityLng": 2.3522,
  "cityBbox": [48.815575, 48.902156, 2.224122, 2.469761]
}

Install dependencies:

  pip install requests shapely

Usage examples:

  python random_address_generation_1.py --count 25
  python random_address_generation_1.py --count 100 --output fallback_addresses.generated.json
  python random_address_generation_1.py --count 25 --existing fallback_addresses.generated.json

    Generate 100 addresses and also create a JavaScript snippet:
        python build_address_cache.py --count 100 --output fallback_addresses.generated.json --js

Important:
- Please set a real User-Agent contact string if you plan to use this more than
  casually. Nominatim requires identifiable clients.

  python build_address_cache.py \
  --count 50 \
  --user-agent "WorldAddressClassroomGame/1.0 your-email@example.com"
"""

import argparse
import json
import math
import os
import random
import sys
import time
from typing import Any, Dict, List, Optional, Tuple

import requests
from shapely.geometry import Point, shape
from shapely.prepared import prep


COUNTRY_GEOJSON_URL = (
    "https://raw.githubusercontent.com/nvkelso/natural-earth-vector/master/"
    "geojson/ne_110m_admin_0_countries.geojson"
)

OVERPASS_URL = "https://overpass-api.de/api/interpreter"
NOMINATIM_REVERSE_URL = "https://nominatim.openstreetmap.org/reverse"
NOMINATIM_SEARCH_URL = "https://nominatim.openstreetmap.org/search"

DEFAULT_USER_AGENT = (
    "RandomAddressCacheBuilder/1.0 "
    "(educational cache generation; replace-with-your-contact@example.com)"
)


class RateLimiter:
    def __init__(self, min_interval_seconds: float):
        self.min_interval_seconds = min_interval_seconds
        self.last_time = 0.0

    def wait(self):
        now = time.time()
        elapsed = now - self.last_time
        remaining = self.min_interval_seconds - elapsed
        if remaining > 0:
            time.sleep(remaining)
        self.last_time = time.time()


nominatim_limiter = RateLimiter(1.1)
overpass_limiter = RateLimiter(1.5)


def request_json(
    url: str,
    *,
    params: Optional[Dict[str, Any]] = None,
    headers: Optional[Dict[str, str]] = None,
    limiter: Optional[RateLimiter] = None,
    retries: int = 3,
    timeout: int = 45,
) -> Any:
    if limiter:
        limiter.wait()

    last_error = None

    for attempt in range(1, retries + 1):
        try:
            response = requests.get(
                url,
                params=params,
                headers=headers,
                timeout=timeout,
            )

            if response.status_code in (429, 500, 502, 503, 504):
                raise RuntimeError(
                    f"HTTP {response.status_code}: temporary API problem"
                )

            response.raise_for_status()
            return response.json()

        except Exception as exc:
            last_error = exc
            sleep_seconds = 2 ** attempt
            print(
                f"    request failed attempt {attempt}/{retries}: {exc}; "
                f"sleeping {sleep_seconds}s",
                file=sys.stderr,
            )
            time.sleep(sleep_seconds)

    raise RuntimeError(f"Request failed after {retries} attempts: {last_error}")


def normalize_name(value: Optional[str]) -> str:
    if not value:
        return ""
    return "".join(
        ch.lower() if ch.isalnum() else " "
        for ch in value.strip()
    ).split()


def normalized_join(value: Optional[str]) -> str:
    return " ".join(normalize_name(value))


def is_meaningful_region(
    region: Optional[str],
    city: Optional[str],
    country: Optional[str],
) -> bool:
    if not region:
        return False

    r = normalized_join(region)
    c = normalized_join(city)
    co = normalized_join(country)

    if not r:
        return False
    if r == c:
        return False
    if r == co:
        return False

    return True


def random_point_on_earth() -> Tuple[float, float]:
    """
    Returns lat, lng.

    This samples uniformly on the sphere. Do not use a simple random latitude
    from -90 to 90, because that over-samples the poles.
    """
    lng = random.uniform(-180.0, 180.0)
    u = random.uniform(-1.0, 1.0)
    lat = math.degrees(math.asin(u))
    return lat, lng


def load_countries() -> List[Dict[str, Any]]:
    print("Loading Natural Earth country polygons...")
    data = request_json(COUNTRY_GEOJSON_URL)

    countries = []

    for feature in data["features"]:
        props = feature.get("properties", {})
        geom = shape(feature["geometry"])

        iso3 = (
            props.get("ISO_A3")
            or props.get("ADM0_A3")
            or props.get("SOV_A3")
        )

        if not iso3 or iso3 == "-99":
            continue

        countries.append(
            {
                "feature": feature,
                "geometry": geom,
                "prepared": prep(geom),
                "continent": props.get("CONTINENT"),
                "country": props.get("ADMIN") or props.get("NAME"),
                "iso3": iso3,
            }
        )

    print(f"Loaded {len(countries)} countries.")
    return countries


def find_country_containing_point(
    countries: List[Dict[str, Any]],
    lat: float,
    lng: float,
) -> Optional[Dict[str, Any]]:
    pt = Point(lng, lat)

    for country in countries:
        try:
            if country["prepared"].contains(pt) or country["geometry"].touches(pt):
                return country
        except Exception:
            continue

    return None


def overpass_query(query: str) -> Any:
    return request_json(
        OVERPASS_URL,
        params={"data": query},
        limiter=overpass_limiter,
        retries=3,
        timeout=60,
    )


def find_nearby_place(lat: float, lng: float) -> Optional[Dict[str, Any]]:
    """
    Finds a nearby populated place.

    We progressively increase the radius because random land points can fall in
    remote areas.
    """
    radii_meters = [25000, 50000, 100000, 200000, 350000]

    for radius in radii_meters:
        query = f"""
        [out:json][timeout:25];
        (
          node["place"~"city|town|village"](around:{radius},{lat},{lng});
        );
        out body 75;
        """

        data = overpass_query(query)
        elements = data.get("elements", [])

        places = []

        for el in elements:
            if el.get("lat") is None or el.get("lon") is None:
                continue

            tags = el.get("tags") or {}
            name = tags.get("name")

            if not name:
                continue

            place_lat = float(el["lat"])
            place_lng = float(el["lon"])

            distance_km = haversine_km(lat, lng, place_lat, place_lng)

            places.append(
                {
                    "name": name,
                    "lat": place_lat,
                    "lng": place_lng,
                    "type": tags.get("place"),
                    "distanceKm": distance_km,
                }
            )

        if places:
            places.sort(key=lambda p: p["distanceKm"])

            # Choose from the nearest few, rather than always the absolute nearest.
            shortlist = places[: min(8, len(places))]
            return random.choice(shortlist)

    return None


def find_random_address_near(lat: float, lng: float) -> Optional[Dict[str, float]]:
    """
    Finds a random OSM address point or address-bearing way near a city/town/village.
    """
    radii_meters = [3000, 6000, 10000, 20000, 35000]

    for radius in radii_meters:
        query = f"""
        [out:json][timeout:30];
        (
          node["addr:housenumber"]["addr:street"](around:{radius},{lat},{lng});
          way["addr:housenumber"]["addr:street"](around:{radius},{lat},{lng});
        );
        out center 150;
        """

        data = overpass_query(query)
        elements = data.get("elements", [])

        usable = []

        for el in elements:
            point_lat = el.get("lat")
            point_lng = el.get("lon")

            if point_lat is None and "center" in el:
                point_lat = el["center"].get("lat")
                point_lng = el["center"].get("lon")

            if point_lat is None or point_lng is None:
                continue

            usable.append(
                {
                    "lat": float(point_lat),
                    "lng": float(point_lng),
                }
            )

        if usable:
            return random.choice(usable)

    return None


def reverse_geocode(
    lat: float,
    lng: float,
    user_agent: str,
) -> Optional[Dict[str, Any]]:
    data = request_json(
        NOMINATIM_REVERSE_URL,
        params={
            "format": "jsonv2",
            "addressdetails": 1,
            "lat": lat,
            "lon": lng,
        },
        headers={"User-Agent": user_agent},
        limiter=nominatim_limiter,
        retries=3,
        timeout=45,
    )

    return data


def geocode_city(
    city: str,
    state: Optional[str],
    country: str,
    user_agent: str,
) -> Optional[Dict[str, Any]]:
    params = {
        "format": "jsonv2",
        "limit": 1,
        "city": city,
        "country": country,
        "polygon_geojson": 1,
    }

    if state:
        params["state"] = state

    data = request_json(
        NOMINATIM_SEARCH_URL,
        params=params,
        headers={"User-Agent": user_agent},
        limiter=nominatim_limiter,
        retries=3,
        timeout=45,
    )

    if not isinstance(data, list) or not data:
        return None

    item = data[0]

    bbox = None
    if item.get("boundingbox") and len(item["boundingbox"]) == 4:
        # Nominatim order is [south, north, west, east].
        bbox = [float(x) for x in item["boundingbox"]]

    return {
        "lat": float(item["lat"]),
        "lng": float(item["lon"]),
        "bbox": bbox,
    }


def build_one_address(
    countries: List[Dict[str, Any]],
    user_agent: str,
    attempt_number: int,
) -> Optional[Dict[str, Any]]:
    lat, lng = random_point_on_earth()

    initial_country = find_country_containing_point(countries, lat, lng)
    if not initial_country:
        print(f"  attempt {attempt_number}: ocean/no country")
        return None

    print(
        f"  attempt {attempt_number}: land point in "
        f"{initial_country['country']} ({initial_country['continent']})"
    )

    nearby_place = find_nearby_place(lat, lng)
    if not nearby_place:
        print("    no nearby city/town/village found")
        return None

    print(
        f"    nearby place: {nearby_place['name']} "
        f"({nearby_place['type']}, {nearby_place['distanceKm']:.1f} km away)"
    )

    address_point = find_random_address_near(
        nearby_place["lat"],
        nearby_place["lng"],
    )

    if not address_point:
        print("    no address found near nearby place")
        return None

    print(
        f"    address point: {address_point['lat']:.5f}, "
        f"{address_point['lng']:.5f}"
    )

    actual_country = find_country_containing_point(
        countries,
        address_point["lat"],
        address_point["lng"],
    )

    if not actual_country:
        print("    address point is not inside a known country polygon")
        return None

    reverse = reverse_geocode(
        address_point["lat"],
        address_point["lng"],
        user_agent,
    )

    if not reverse:
        print("    reverse geocode failed")
        return None

    addr = reverse.get("address") or {}

    country_name = addr.get("country") or actual_country["country"]
    continent = actual_country["continent"]
    iso3 = actual_country["iso3"]

    city = (
        addr.get("city")
        or addr.get("town")
        or addr.get("village")
        or addr.get("municipality")
        or addr.get("suburb")
        or nearby_place["name"]
    )

    state = (
        addr.get("state")
        or addr.get("province")
        or addr.get("region")
        or addr.get("state_district")
    )

    if not is_meaningful_region(state, city, country_name):
        state = None

    road = (
        addr.get("road")
        or addr.get("pedestrian")
        or addr.get("footway")
        or addr.get("path")
        or addr.get("residential")
    )

    if not city:
        print("    no usable city name")
        return None

    if not road:
        print("    no usable street/road name")
        return None

    house = addr.get("house_number")
    street = f"{house} {road}" if house else road

    city_info = geocode_city(
        city,
        state,
        country_name,
        user_agent,
    )

    city_lat = city_info["lat"] if city_info else nearby_place["lat"]
    city_lng = city_info["lng"] if city_info else nearby_place["lng"]
    city_bbox = city_info["bbox"] if city_info else None

    result = {
        "continent": continent,
        "country": country_name,
        "iso3": iso3,
        "state": state,
        "city": city,
        "street": street,
        "lat": round(float(address_point["lat"]), 7),
        "lng": round(float(address_point["lng"]), 7),
        "cityLat": round(float(city_lat), 7),
        "cityLng": round(float(city_lng), 7),
        "cityBbox": city_bbox,
    }

    # Remove region/state from the cached address if it duplicates city/country.
    if not is_meaningful_region(result.get("state"), result["city"], result["country"]):
        result["state"] = None

    print(
        "    SUCCESS:",
        f"{result['continent']} › {result['country']} › "
        f"{result['state'] + ' › ' if result['state'] else ''}"
        f"{result['city']} › {result['street']}",
    )

    return result


def haversine_km(
    lat1: float,
    lng1: float,
    lat2: float,
    lng2: float,
) -> float:
    r = 6371.0088

    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)

    d_phi = math.radians(lat2 - lat1)
    d_lambda = math.radians(lng2 - lng1)

    a = (
        math.sin(d_phi / 2) ** 2
        + math.cos(phi1) * math.cos(phi2) * math.sin(d_lambda / 2) ** 2
    )

    return 2 * r * math.atan2(math.sqrt(a), math.sqrt(1 - a))


def address_key(address: Dict[str, Any]) -> str:
    return "|".join(
        [
            normalized_join(address.get("country")),
            normalized_join(address.get("city")),
            normalized_join(address.get("street")),
            str(round(float(address.get("lat", 0)), 5)),
            str(round(float(address.get("lng", 0)), 5)),
        ]
    )


def load_existing_addresses(path: Optional[str]) -> List[Dict[str, Any]]:
    if not path:
        return []

    if not os.path.exists(path):
        return []

    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    if not isinstance(data, list):
        raise ValueError("Existing address file must contain a JSON array.")

    return data


def save_addresses(path: str, addresses: List[Dict[str, Any]]) -> None:
    with open(path, "w", encoding="utf-8") as f:
        json.dump(addresses, f, ensure_ascii=False, indent=2)

    print(f"\nSaved {len(addresses)} addresses to {path}")


def save_js_snippet(path: str, addresses: List[Dict[str, Any]]) -> None:
    js_path = path
    if js_path.endswith(".json"):
        js_path = js_path[:-5] + ".js"

    with open(js_path, "w", encoding="utf-8") as f:
        f.write("const FALLBACK_ADDRESSES = ")
        json.dump(addresses, f, ensure_ascii=False, indent=2)
        f.write(";\n")

    print(f"Saved JavaScript snippet to {js_path}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--count",
        type=int,
        default=25,
        help="Number of new successful addresses to generate.",
    )
    parser.add_argument(
        "--output",
        default="fallback_addresses.generated.json",
        help="Output JSON file.",
    )
    parser.add_argument(
        "--existing",
        default=None,
        help="Optional existing JSON file to load and append to/deduplicate.",
    )
    parser.add_argument(
        "--max-attempts",
        type=int,
        default=500,
        help="Maximum random attempts before giving up.",
    )
    parser.add_argument(
        "--user-agent",
        default=DEFAULT_USER_AGENT,
        help=(
            "User-Agent sent to Nominatim. Replace with a real contact string "
            "for serious use."
        ),
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=None,
        help="Optional random seed for reproducible runs.",
    )
    parser.add_argument(
        "--js",
        action="store_true",
        help="Also write a .js file containing const FALLBACK_ADDRESSES = ...",
    )

    args = parser.parse_args()

    if args.seed is not None:
        random.seed(args.seed)

    existing = load_existing_addresses(args.existing or args.output)
    results = list(existing)

    seen = {address_key(a) for a in results}

    print(f"Starting with {len(results)} existing addresses.")
    print(f"Trying to generate {args.count} new addresses.\n")

    countries = load_countries()

    successes = 0
    attempts = 0

    while successes < args.count and attempts < args.max_attempts:
        attempts += 1

        print(f"\n=== Random attempt {attempts}; successes {successes}/{args.count} ===")

        try:
            address = build_one_address(
                countries,
                args.user_agent,
                attempts,
            )

            if not address:
                continue

            key = address_key(address)
            if key in seen:
                print("    duplicate; skipping")
                continue

            seen.add(key)
            results.append(address)
            successes += 1

            # Save after every success so progress is not lost.
            save_addresses(args.output, results)

        except KeyboardInterrupt:
            print("\nInterrupted by user.")
            break

        except Exception as exc:
            print(f"  attempt failed with error: {exc}", file=sys.stderr)

    print("\nDone.")
    print(f"Attempts: {attempts}")
    print(f"New successes: {successes}")
    print(f"Total saved addresses: {len(results)}")

    save_addresses(args.output, results)

    if args.js:
        save_js_snippet(args.output, results)


if __name__ == "__main__":
    main()