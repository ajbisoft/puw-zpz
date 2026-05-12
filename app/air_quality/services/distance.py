from math import radians, sin, cos, sqrt, atan2


def parse_coord(value):
    """
    Zamienia współrzędną na float.
    Obsługuje zarówno zapis z kropką, jak i z przecinkiem.
    """
    if value is None:
        raise ValueError("Brak współrzędnej")

    if isinstance(value, str):
        value = value.replace(",", ".")

    return float(value)


def haversine_distance(lat1, lon1, lat2, lon2):
    earth_radius_km = 6371.0

    lat1 = radians(parse_coord(lat1))
    lon1 = radians(parse_coord(lon1))
    lat2 = radians(parse_coord(lat2))
    lon2 = radians(parse_coord(lon2))

    dlat = lat2 - lat1
    dlon = lon2 - lon1

    a = (
        sin(dlat / 2) ** 2
        + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    )

    c = 2 * atan2(sqrt(a), sqrt(1 - a))

    return earth_radius_km * c


def find_nearest_station(user_lat, user_lon, stations):
    nearest_station = None
    nearest_distance = None

    for station in stations:
        if not isinstance(station, dict):
            continue

        station_lat = station.get("WGS84 φ N")
        station_lon = station.get("WGS84 λ E")

        if not station_lat or not station_lon:
            continue

        try:
            distance = haversine_distance(
                user_lat,
                user_lon,
                station_lat,
                station_lon
            )
        except ValueError:
            continue

        if nearest_distance is None or distance < nearest_distance:
            nearest_distance = distance
            nearest_station = station

    return nearest_station, nearest_distance

def normalize_text(value):
    if value is None:
        return ""

    return str(value).strip().lower()


def find_stations_by_city(city_name, stations):
    """
    Zwraca listę stacji GIOŚ znajdujących się w podanym mieście.
    """

    city_name_normalized = normalize_text(city_name)

    matching_stations = []

    for station in stations:
        if not isinstance(station, dict):
            continue

        station_city = normalize_text(station.get("Nazwa miasta"))

        if station_city == city_name_normalized:
            matching_stations.append(station)

    return matching_stations