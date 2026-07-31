import random
import time
from geonamescache import GeonamesCache
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut, GeocoderServiceError

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
                raw_bbox = location.raw.get('boundingbox', "") # Format: [min_lat, max_lat, min_lon, max_lon]
                
                # Ensure bounding box values are converted to numeric floats if present
                bounding_box = [round(float(coord), 4) for coord in raw_bbox] if raw_bbox else ""

                return (
                    continent_name or "",
                    country_name or "",
                    state_name or "",
                    city_name or "",
                    street_address or "",
                    exact_lat,
                    exact_lon,
                    bounding_box
                )
                
        except (GeocoderTimedOut, GeocoderServiceError):
            continue # Try a different city if the network request fails

    # Return empty strings if all attempts fail
    return "", "", "", "", "", "", "", ""

# --- Example Execution ---
continent, country, state, city, address, lat, lon, bbox = get_random_city_with_address()

printdict = {
    'continent': continent, 
    'country': country,
    'state': state,
    'city': city,
    'address': address,
    'addressLat': lat,
    'addressLon': lon,
    'cityBbox': bbox
}
print(printdict)

# print(f"City:           {city}")
# print(f"Street Address: {address}")
# print(f"State/Region:   {state}")
# print(f"Country:        {country}")
# print(f"Continent:      {continent}")
# print(f"Exact Lat/Lon:  {lat}, {lon}")
# print(f"Address BBox:   {bbox}")
