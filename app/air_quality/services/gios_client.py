import requests
import time

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


def get_station_sensors(station_id, retries=3, sleep_time=2):
    """
    Pobiera listę czujników / stanowisk pomiarowych dla danej stacji GIOŚ.
    """

    url = f"{BASE_URL}/station/sensors/{station_id}"

    for attempt in range(1, retries + 1):
        try:
            response = requests.get(
                url,
                headers=HEADERS,
                timeout=30
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

        except requests.exceptions.RequestException as error:
            print(f"Błąd pobierania czujników dla stacji {station_id}, próba {attempt}/{retries}")
            print(error)

            if attempt < retries:
                time.sleep(sleep_time)

    print(f"Nie udało się pobrać czujników dla stacji {station_id}.")
    return []


def get_sensor_data(sensor_id, retries=3, sleep_time=2):
    """
    Pobiera dane pomiarowe z konkretnego czujnika GIOŚ.
    Jeśli API zwróci błąd albo zerwie połączenie, funkcja zwraca None.
    """

    url = f"{BASE_URL}/data/getData/{sensor_id}"

    for attempt in range(1, retries + 1):
        try:
            response = requests.get(
                url,
                headers=HEADERS,
                timeout=30
            )

            if response.status_code != 200:
                print(f"Błąd pobierania danych dla czujnika {sensor_id}")
                print("Status:", response.status_code)
                print("Treść odpowiedzi:", response.text)
                return None

            return response.json()

        except requests.exceptions.RequestException as error:
            print(f"Błąd połączenia dla czujnika {sensor_id}, próba {attempt}/{retries}")
            print(error)

            if attempt < retries:
                time.sleep(sleep_time)

    print(f"Nie udało się pobrać danych dla czujnika {sensor_id} po {retries} próbach.")
    return None