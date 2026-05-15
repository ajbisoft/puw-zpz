import time
import requests


BASE_URL = "https://api.gios.gov.pl/pjp-api/v1/rest"

HEADERS = {
    "accept": "application/ld+json"
}


def extract_list_from_response(data, possible_keys=None):
    """
    Próbuje wyciągnąć listę wyników z odpowiedzi API.
    Obsługuje różne możliwe formaty odpowiedzi.
    """

    if isinstance(data, list):
        return data

    if not isinstance(data, dict):
        return []

    if possible_keys is None:
        possible_keys = []

    default_keys = [
        "Lista stacji pomiarowych",
        "Lista stanowisk pomiarowych dla podanej stacji",
        "Lista stanowisk pomiarowych",
        "Lista danych pomiarowych",
        "Lista archiwalnych wyników pomiarów",
        "Lista wyników pomiarów",
        "hydra:member",
        "member",
        "items",
        "results",
        "values",
        "content",
    ]

    all_keys = possible_keys + default_keys

    for key in all_keys:
        value = data.get(key)

        if isinstance(value, list):
            return value

    for value in data.values():
        if isinstance(value, list):
            return value

    return []


def get_total_pages(data):
    """
    Próbuje odczytać liczbę stron z odpowiedzi API.
    Jeśli API nie zwraca informacji o liczbie stron, zwraca None.
    """

    if not isinstance(data, dict):
        return None

    possible_keys = [
        "totalPages",
        "total_pages",
        "liczbaStron",
        "Liczba stron",
        "pages",
    ]

    for key in possible_keys:
        value = data.get(key)

        if value is not None:
            try:
                return int(value)
            except (TypeError, ValueError):
                pass

    return None


def request_json_with_retries(url, params=None, retries=3, sleep_time=1, timeout=30):
    """
    Wysyła request GET z retry.
    Zwraca JSON albo None.
    """

    for attempt in range(1, retries + 1):
        try:
            response = requests.get(
                url,
                headers=HEADERS,
                params=params,
                timeout=timeout
            )

            if response.status_code != 200:
                print("Błąd pobierania danych")
                print("URL:", url)
                print("Params:", params)
                print("Status:", response.status_code)
                print("Treść odpowiedzi:", response.text)
                return None

            return response.json()

        except requests.exceptions.RequestException as error:
            print(f"Błąd połączenia, próba {attempt}/{retries}")
            print("URL:", url)
            print("Params:", params)
            print(error)

            if attempt < retries:
                time.sleep(sleep_time)

    print("Nie udało się pobrać danych po kilku próbach.")
    print("URL:", url)
    print("Params:", params)
    return None


def get_paginated_data(
    url,
    base_params=None,
    size=500,
    retries=3,
    sleep_time=0.2,
    possible_keys=None,
):
    """
    Pobiera wszystkie strony z endpointu obsługującego parametry page i size.
    Zakładamy, że page liczony jest od 0.
    """

    if base_params is None:
        base_params = {}

    all_items = []
    page = 0
    total_pages = None

    while True:
        params = {
            **base_params,
            "page": page,
            "size": size,
        }

        data = request_json_with_retries(
            url=url,
            params=params,
            retries=retries,
            sleep_time=sleep_time,
            timeout=30,
        )

        if data is None:
            return all_items

        items = extract_list_from_response(
            data,
            possible_keys=possible_keys,
        )

        if not items:
            break

        all_items.extend(items)

        print(
            f"    Strona {page}: pobrano {len(items)} rekordów "
            f"(łącznie: {len(all_items)})"
        )

        if total_pages is None:
            total_pages = get_total_pages(data)

        if total_pages is not None:
            if page >= total_pages - 1:
                break
        else:
            if len(items) < size:
                break

        page += 1
        time.sleep(sleep_time)

    return all_items


def get_all_stations(size=500, retries=3, sleep_time=0.2):
    """
    Pobiera wszystkie stacje pomiarowe GIOŚ ze wszystkich stron.
    """

    url = f"{BASE_URL}/station/findAll"

    stations = get_paginated_data(
        url=url,
        base_params={},
        size=size,
        retries=retries,
        sleep_time=sleep_time,
        possible_keys=[
            "Lista stacji pomiarowych",
        ],
    )

    if not stations:
        print("Nie znaleziono listy stacji albo API zwróciło pustą odpowiedź.")

    return stations


def get_station_sensors(station_id, retries=3, sleep_time=2):
    """
    Pobiera listę czujników / stanowisk pomiarowych dla danej stacji GIOŚ.
    Ten endpoint zwykle nie wymaga paginacji.
    """

    url = f"{BASE_URL}/station/sensors/{station_id}"

    data = request_json_with_retries(
        url=url,
        params=None,
        retries=retries,
        sleep_time=sleep_time,
        timeout=30,
    )

    if data is None:
        print(f"Nie udało się pobrać czujników dla stacji {station_id}.")
        return []

    sensors = extract_list_from_response(
        data,
        possible_keys=[
            "Lista stanowisk pomiarowych dla podanej stacji",
            "Lista stanowisk pomiarowych",
        ],
    )

    if not sensors:
        if isinstance(data, dict):
            print("Nie znaleziono listy czujników. Klucze odpowiedzi API:")
            print(data.keys())

    return sensors


def get_sensor_data(sensor_id, retries=3, sleep_time=2):
    """
    Pobiera bieżące dane pomiarowe z konkretnego czujnika GIOŚ.
    Ten endpoint zwykle zwraca ograniczony zestaw najnowszych danych i nie używa page.
    """

    url = f"{BASE_URL}/data/getData/{sensor_id}"

    data = request_json_with_retries(
        url=url,
        params=None,
        retries=retries,
        sleep_time=sleep_time,
        timeout=30,
    )

    if data is None:
        print(f"Nie udało się pobrać bieżących danych dla czujnika {sensor_id}.")
        return None

    return data


def get_archival_sensor_data(sensor_id, day_number, size=500, retries=3, sleep_time=0.1):
    """
    Pobiera wszystkie strony danych historycznych z konkretnego czujnika GIOŚ.

    Endpoint:
    /archivalData/getDataBySensor/{sensor_id}?page=0&size=500&dayNumber={day_number}

    Zwraca jedną listę pomiarów ze wszystkich stron.
    """

    url = f"{BASE_URL}/archivalData/getDataBySensor/{sensor_id}"

    print(
        f"  Pobieram dane historyczne dla czujnika {sensor_id}, "
        f"dni wstecz: {day_number}, size: {size}"
    )

    all_values = get_paginated_data(
        url=url,
        base_params={
            "dayNumber": day_number,
        },
        size=size,
        retries=retries,
        sleep_time=sleep_time,
        possible_keys=[
            "Lista danych pomiarowych",
            "Lista archiwalnych wyników pomiarów",
            "Lista wyników pomiarów",
        ],
    )

    if not all_values:
        print(f"  Brak danych historycznych dla czujnika {sensor_id}.")
        return None

    return all_values