import requests

def geocode_city(city_name: str):
    url = f"https://nominatim.openstreetmap.org/search?q={city_name}&format=json&limit=1"
    response = requests.get(url).json()
    if response:
        location = response[0]
        return float(location["lat"]), float(location["lon"])
    return None