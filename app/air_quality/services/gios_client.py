import requests


BASE_URL = "https://api.gios.gov.pl/pjp-api/v1/rest"

HEADERS = {
    "accept": "application/ld+json"
}


def get_all_stations(size=500):
    """
    Pobiera listę stacji pomiarowych GIOŚ.
    """

    url = f"{BASE_URL}/station/findAll"

    response = requests.get(
        url,
        headers=HEADERS,
        params={"size": size},
        timeout=20
    )

    response.raise_for_status()

    data = response.json()

    if isinstance(data, list):
        return data

    possible_keys = [
        "Lista stacji pomiarowych",
        "hydra:member",
        "member",
        "items",
        "results",
    ]

    for key in possible_keys:
        value = data.get(key)
        if isinstance(value, list):
            return value

    print("Nie znaleziono listy stacji. Klucze odpowiedzi API:")
    print(data.keys())

    return []


def get_station_sensors(station_id):
    """
    Pobiera listę czujników / stanowisk pomiarowych dla danej stacji GIOŚ.
    """

    url = f"{BASE_URL}/station/sensors/{station_id}"

    response = requests.get(
        url,
        headers=HEADERS,
        timeout=20
    )

    response.raise_for_status()

    data = response.json()

    if isinstance(data, list):
        return data

    possible_keys = [
        "Lista stanowisk pomiarowych dla podanej stacji",
        "Lista stanowisk pomiarowych",
        "hydra:member",
        "member",
        "items",
        "results",
    ]

    for key in possible_keys:
        value = data.get(key)
        if isinstance(value, list):
            return value

    print("Nie znaleziono listy czujników. Klucze odpowiedzi API:")
    print(data.keys())

    return []


def get_sensor_data(sensor_id):
    """
    Pobiera dane pomiarowe z konkretnego czujnika GIOŚ.
    Jeśli API zwróci błąd, funkcja zwraca None zamiast wywalać aplikację.
    """

    url = f"{BASE_URL}/data/getData/{sensor_id}"

    response = requests.get(
        url,
        headers=HEADERS,
        timeout=20
    )

    if response.status_code != 200:
        print(f"Błąd pobierania danych dla czujnika {sensor_id}")
        print("Status:", response.status_code)
        print("Treść odpowiedzi:", response.text)
        return None

    return response.json()