import random
import time
from geonamescache import GeonamesCache
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut, GeocoderServiceError
import json


def select_major_city_candidates(cities, max_count=250, min_population=100000):
    """Return a bounded pool of major world cities from the provided city list."""
    if not cities:
        return []

    filtered = [city for city in cities if (city.get('population') or 0) >= min_population]

    if not filtered:
        fallback_population = max(1000, min_population // 10)
        filtered = [city for city in cities if (city.get('population') or 0) >= fallback_population]

    ranked = sorted(
        filtered,
        key=lambda city: (
            city.get('population') or 0,
            city.get('name') or '',
        ),
        reverse=True,
    )

    return ranked[:max_count]


def get_random_city_with_address():
    """
    Selects a random world city, generates a nearby random coordinate,
    and reverses it to find a valid local street address and its exact location.
    
    Returns:
        tuple: (continent, country, state, city_name, street_address, lat, lon, bounding_box)
               Returns "" for any fields that cannot be resolved.
    """
    # 1. Initialize data sources
    gc = GeonamesCache()
    cities = gc.get_cities()
    countries = gc.get_countries()
    us_states = gc.get_us_states()

    if not cities:
        return "", "", "", "", "", "", "", ""

    # OpenStreetMap requires a unique, descriptive User-Agent header
    geolocator = Nominatim(user_agent="random_address_generator_2026")

    # Try up to 5 random cities/offsets to guarantee we find a valid street address
    for _ in range(5):
        random_city_id = random.choice(list(cities.keys()))
        city_data = cities[random_city_id]

        # Extract base city coordinates
        base_lat = city_data.get('latitude')
        base_lon = city_data.get('longitude')
        
        if base_lat is None or base_lon is None:
            continue

        # 2. Add a tiny random offset (~1–2 km) to move away from the exact city center point
        # This increases the chances of hitting a residential/commercial street address
        offset_lat = float(base_lat) + random.uniform(-0.015, 0.015)
        offset_lon = float(base_lon) + random.uniform(-0.015, 0.015)

        try:
            # Respect OpenStreetMap's usage policy by introducing a tiny delay if looping
            time.sleep(1.0) 
            
            # 3. Query OpenStreetMap for the closest street address
            location = geolocator.reverse((offset_lat, offset_lon), timeout=5)
            
            if location and location.raw.get('address'):
                address_data = location.raw['address']
                
                # Verify if we hit a usable street or building feature
                street = address_data.get('road') or address_data.get('pedestrian') or address_data.get('suburb')
                if not street:
                    continue  # Skip if it returned empty wilderness or open ocean
                
                # 4. Construct the street address string (e.g., "123 Main St")
                house_number = address_data.get('house_number', '')
                street_address = f"{house_number} {street}".strip()

                # 5. Resolve city metadata
                city_name = city_data.get('name', '')
                country_code = city_data.get('countrycode', '')
                country_info = countries.get(country_code, {})
                country_name = country_info.get('name', '')
                continent_name = country_info.get('continentcode', '')

                # Resolve state/region text
                state_code = city_data.get('admin1code', '')
                state_name = ""
                if country_code == 'US' and state_code in us_states:
                    state_name = us_states[state_code].get('name', '')
                else:
                    state_name = state_code if (state_code and str(state_code).isalpha()) else ""

                # 6. Extract the exact coordinate and bounding box of the specific address found
                exact_lat = location.latitude
                exact_lon = location.longitude
                raw_bbox = location.raw.get('boundingbox', '') # Format: [min_lat, max_lat, min_lon, max_lon]
                
                # Ensure bounding box values are converted to numeric floats if present
                bounding_box = [round(float(coord), 4) for coord in raw_bbox] if raw_bbox else ""

                return {
                    'continent': continent_name or '',
                    'country': country_name or '',
                    'state': state_name or '',
                    'city': city_name or '',
                    'address': street_address or '',
                    'addressLat': exact_lat,
                    'addressLon': exact_lon,
                    'cityBbox': bounding_box
                }
                
        except (GeocoderTimedOut, GeocoderServiceError):
            continue # Try a different city if the network request fails

    with open('puzzle/view_functions/geo_cache.json', 'r', encoding='utf-8') as f:
        cached_data = json.load(f)
    return random.choice(cached_data)


def get_random_city_with_address_major_cities():
    """Return a random city/address from a major-city pool spanning the world."""
    try:
        gc = GeonamesCache()
        cities = list(gc.get_cities().values())
        major_candidates = select_major_city_candidates(cities)

        if not major_candidates:
            return get_random_city_with_address()

        return get_random_city_with_address_from_candidates(major_candidates)
    except Exception:
        return get_random_city_with_address()


def get_random_city_with_address_from_candidates(candidates):
    """Reverse geocode a random city from the supplied candidate list."""
    gc = GeonamesCache()
    countries = gc.get_countries()
    us_states = gc.get_us_states()
    geolocator = Nominatim(user_agent="random_address_generator_2026")

    for _ in range(6):
        chosen = random.choice(candidates)
        base_lat = chosen.get('latitude')
        base_lon = chosen.get('longitude')
        if base_lat is None or base_lon is None:
            continue

        offset_lat = float(base_lat) + random.uniform(-0.015, 0.015)
        offset_lon = float(base_lon) + random.uniform(-0.015, 0.015)

        try:
            time.sleep(1.0)
            location = geolocator.reverse((offset_lat, offset_lon), timeout=5)
            if location and location.raw.get('address'):
                address_data = location.raw['address']
                street = address_data.get('road') or address_data.get('pedestrian') or address_data.get('suburb')
                if not street:
                    continue

                house_number = address_data.get('house_number', '')
                street_address = f"{house_number} {street}".strip()

                country_code = chosen.get('countrycode', '')
                country_info = countries.get(country_code, {})
                country_name = country_info.get('name', '')
                continent_name = country_info.get('continentcode', '')

                state_name = ''
                if country_code == 'US' and chosen.get('admin1code') in us_states:
                    state_name = us_states[chosen.get('admin1code')].get('name', '')
                else:
                    state_name = chosen.get('admin1code', '')

                exact_lat = location.latitude
                exact_lon = location.longitude
                raw_bbox = location.raw.get('boundingbox', '')
                bounding_box = [round(float(coord), 4) for coord in raw_bbox] if raw_bbox else ''

                return {
                    'continent': continent_name or '',
                    'country': country_name or '',
                    'state': state_name or '',
                    'city': chosen.get('name', '') or '',
                    'address': street_address or '',
                    'addressLat': exact_lat,
                    'addressLon': exact_lon,
                    'cityBbox': bounding_box
                }
        except (GeocoderTimedOut, GeocoderServiceError):
            continue

    return get_random_city_with_address()


def get_random_city_with_address_filtered(filters: dict):
    """
    Select a random city/address constrained by filters dict which may contain
    keys: continent (code or name), country (name or ISO), state (name or code), city (name substring).

    If filters is empty or no match found, falls back to get_random_city_with_address().
    """
    try:
        if not filters:
            return get_random_city_with_address()

        gc = GeonamesCache()
        countries = gc.get_countries()
        cities = gc.get_cities()
        us_states = gc.get_us_states()

        # Normalize filter values
        cont = (filters.get('continent') or '').strip()
        country_in = (filters.get('country') or '').strip()
        state_in = (filters.get('state') or '').strip()
        city_in = (filters.get('city') or '').strip()

        # Build initial candidate list
        candidates = list(cities.values())

        # Filter by continent: accept either continent code (e.g. 'NA') or name
        if cont:
            cont_norm = cont.upper()
            # If given a full name, try to find matching continent code
            continent_codes = set()
            for ccode, cdata in gc.get_continents().items():
                if ccode.upper() == cont_norm or cdata.get('name','').lower() == cont.lower() or cdata.get('aliases','').lower() == cont.lower():
                    continent_codes.add(ccode)

            # Also accept codes provided directly
            if not continent_codes and len(cont_norm) <= 3:
                continent_codes.add(cont_norm)

            if continent_codes:
                country_codes = {k for k, v in countries.items() if v.get('continentcode') in continent_codes}
                candidates = [c for c in candidates if c.get('countrycode') in country_codes]

        # Filter by country name or ISO
        if country_in:
            country_iso = None
            for iso, cdata in countries.items():
                if country_in.lower() == cdata.get('name','').lower() or country_in.lower() == iso.lower() or country_in.lower() == cdata.get('iso3','').lower():
                    country_iso = iso
                    break

            if country_iso:
                candidates = [c for c in candidates if c.get('countrycode') == country_iso]

        # Filter by state (best-effort): for US use us_states mapping; otherwise match admin1code or name substring
        if state_in:
            state_norm = state_in.strip()
            # Try US states mapping first
            state_code = None
            for code, sdata in us_states.items():
                if state_norm.lower() == code.lower() or state_norm.lower() == sdata.get('name','').lower():
                    state_code = code
                    break

            if state_code:
                candidates = [c for c in candidates if str(c.get('admin1code','')).upper() == state_code.upper()]
            else:
                # Fallback: match admin1code directly or admin1 name substring in alternatenames
                candidates = [c for c in candidates if state_norm.lower() in str(c.get('admin1code','')).lower() or state_norm.lower() in c.get('name','').lower()]

        # Filter by city name substring
        if city_in:
            city_norm = city_in.lower()
            candidates = [c for c in candidates if city_norm in c.get('name','').lower()]

        if not candidates:
            return get_random_city_with_address()

        return get_random_city_with_address_from_candidates(candidates)

        # Fallback to cache if reverse geocoding failed
        with open('puzzle/view_functions/geo_cache.json', 'r', encoding='utf-8') as f:
            cached_data = json.load(f)

        # Try to return a cached item that matches filters if possible
        for item in random.sample(cached_data, min(len(cached_data), 30)):
            ok = True
            if cont and item.get('continent','') and cont.lower() not in str(item.get('continent','')).lower():
                ok = False
            if country_in and item.get('country','') and country_in.lower() not in item.get('country','').lower():
                ok = False
            if state_in and item.get('state','') and state_in.lower() not in item.get('state','').lower():
                ok = False
            if city_in and item.get('city','') and city_in.lower() not in item.get('city','').lower():
                ok = False
            if ok:
                return item

        return get_random_city_with_address()
    except Exception:
        return get_random_city_with_address()

    # Return empty strings if all attempts fail
    # return {
    #     'continent': '',
    #     'country': '',
    #     'state': '',
    #     'city': '',
    #     'address': '',
    #     'addressLat': '',
    #     'addressLon': '',
    #     'cityBbox': ''
    # }


def append_to_geo_cache(append_count):
    with open('puzzleplayapp/puzzle/view_functions/geo_cache.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    for i in range(append_count):
        data.append(get_random_city_with_address())
    with open('puzzleplayapp/puzzle/view_functions/geo_cache.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4)


if __name__ == '__main__':
    append_to_geo_cache(100)