import requests

def search_locations(city_name):
    url = "https://geocoding-api.open-meteo.com/v1/search"

    params = {
        "name": city_name,
        "count": 10,
        "language": "pl",
        "format": "json",
        "countryCode": "PL",
    }

    response = requests.get(url, params=params, timeout=20)
    response.raise_for_status()

    data = response.json()
    return data.get("results", [])