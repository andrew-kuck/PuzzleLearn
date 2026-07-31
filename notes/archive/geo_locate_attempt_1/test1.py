import random
import geonamescache

def get_random_detailed_city():
    """
    Selects a random world city and returns geographic metadata.
    
    Returns:
        tuple: (continent, country, state, city_name, latitude, longitude, bounding_box)
               Missing text values default to "". Bounding box defaults to "" if coordinates missing.
    """
    gc = geonamescache.GeonamesCache()
    
    cities = gc.get_cities()
    countries = gc.get_countries()
    us_states = gc.get_us_states()

    if not cities:
        return "", "", "", "", "", "", ""

    # 1. Select a random city ID
    random_city_id = random.choice(list(cities.keys()))
    city_data = cities[random_city_id]

    # 2. Extract standard details
    city_name = city_data.get('name', '')
    country_code = city_data.get('countrycode', '')
    
    # 3. Resolve Country and Continent
    country_info = countries.get(country_code, {})
    country_name = country_info.get('name', '')
    continent_name = country_info.get('continentcode', '')

    # 4. Resolve State / Administrative region
    state_code = city_data.get('admin1code', '')
    state_name = ""
    if country_code == 'US' and state_code in us_states:
        state_name = us_states[state_code].get('name', '')
    else:
        # Fallback to the region code identifier if valid text, otherwise empty string
        state_name = state_code if (state_code and str(state_code).isalpha()) else ""

    # 5. Extract Latitude and Longitude
    latitude = city_data.get('latitude', '')
    longitude = city_data.get('longitude', '')

    # 6. Determine Bounding Box
    bounding_box = ""
    if latitude != "" and longitude != "":
        try:
            lat = float(latitude)
            lon = float(longitude)
            
            # Since cities are point data, we estimate a 0.1 degree buffer around the center
            # Format: [min_lat, max_lat, min_lon, max_lon]
            bounding_box = [
                round(lat - 0.1, 4),  # min latitude
                round(lat + 0.1, 4),  # max latitude
                round(lon - 0.1, 4),  # min longitude
                round(lon + 0.1, 4)   # max longitude
            ]
        except (ValueError, TypeError):
            bounding_box = ""

    return (
        continent_name or "", 
        country_name or "", 
        state_name or "", 
        city_name or "", 
        latitude, 
        longitude, 
        bounding_box
    )

# --- Example Execution ---
continent, country, state, city, lat, lon, bbox = get_random_detailed_city()

print(f"City:         {city}")
print(f"State/Region: {state}")
print(f"Country:      {country}")
print(f"Continent:    {continent}")
print(f"Latitude:     {lat}")
print(f"Longitude:    {lon}")
print(f"Bounding Box: {bbox}")
