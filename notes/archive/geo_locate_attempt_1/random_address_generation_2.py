import json
import random
import time
from faker import Faker
from geopy.geocoders import Nominatim

# Number of addresses to generate
NUM_ADDRESSES = 20

# Supported locales
LOCALES = {
    "United States": {
        "faker": "en_US",
        "continent": "North America",
        "iso3": "USA",
    },
    "Canada": {
        "faker": "en_CA",
        "continent": "North America",
        "iso3": "CAN",
    },
    "France": {
        "faker": "fr_FR",
        "continent": "Europe",
        "iso3": "FRA",
    },
    "Germany": {
        "faker": "de_DE",
        "continent": "Europe",
        "iso3": "DEU",
    },
    "United Kingdom": {
        "faker": "en_GB",
        "continent": "Europe",
        "iso3": "GBR",
    },
    "Italy": {
        "faker": "it_IT",
        "continent": "Europe",
        "iso3": "ITA",
    },
    "Spain": {
        "faker": "es_ES",
        "continent": "Europe",
        "iso3": "ESP",
    },
    "Australia": {
        "faker": "en_AU",
        "continent": "Oceania",
        "iso3": "AUS",
    },
}

geolocator = Nominatim(user_agent="random-address-generator")


def geocode_address(address):
    try:
        location = geolocator.geocode(address, addressdetails=True)
        if location is None:
            return None

        raw = location.raw
        addr = raw.get("address", {})

        bbox = raw.get("boundingbox", [])

        city_bbox = None
        if len(bbox) == 4:
            city_bbox = [
                float(bbox[0]),  # south
                float(bbox[1]),  # north
                float(bbox[2]),  # west
                float(bbox[3]),  # east
            ]

        return {
            "lat": float(location.latitude),
            "lng": float(location.longitude),
            "city": (
                addr.get("city")
                or addr.get("town")
                or addr.get("village")
                or ""
            ),
            "state": addr.get("state", ""),
            "country": addr.get("country", ""),
            "cityLat": float(location.latitude),
            "cityLng": float(location.longitude),
            "cityBbox": city_bbox,
        }

    except Exception:
        return None


results = []

while len(results) < NUM_ADDRESSES:
    country = random.choice(list(LOCALES.keys()))
    info = LOCALES[country]

    fake = Faker(info["faker"])

    street = fake.street_address()
    city = fake.city()

    query = f"{street}, {city}, {country}"

    geo = geocode_address(query)

    # Respect Nominatim usage policy
    time.sleep(1)

    if geo is None:
        continue

    results.append(
        {
            "continent": info["continent"],
            "country": geo["country"],
            "iso3": info["iso3"],
            "state": geo["state"],
            "city": geo["city"],
            "street": street,
            "lat": geo["lat"],
            "lng": geo["lng"],
            "cityLat": geo["cityLat"],
            "cityLng": geo["cityLng"],
            "cityBbox": geo["cityBbox"],
        }
    )

with open("addresses.json", "w", encoding="utf-8") as f:
    json.dump(results, f, indent=2, ensure_ascii=False)

print(f"Generated {len(results)} addresses.")