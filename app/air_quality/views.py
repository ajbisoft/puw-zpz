import json

from django.shortcuts import render, get_object_or_404
from django.utils import timezone

from datetime import timedelta

from air_quality.models import Sensor, Station, Measurement
from air_quality.services.geocoding import search_locations
from air_quality.services.gios_client import (
    get_all_stations,
    get_station_sensors,
    get_sensor_data,
)
from air_quality.services.distance import find_nearest_station, find_stations_by_city
from air_quality.services.measurements import get_latest_measurement
from air_quality.services.aqi import calculate_station_aqi, calculate_aqi_status
from air_quality.services.analytics import (
    get_dashboard_tiles,
    get_city_summary,
    get_station_summary,
    get_city_history,
    get_station_history,
    get_current_city_measurements,
    get_current_station_measurements,
    get_city_station_tiles,
)
from air_quality.services.map_data import get_stations_map_data

def get_air_quality_context(city_name, latitude, longitude, selected_location=None):
    stations = get_all_stations()

    nearest_station, distance = find_nearest_station(
        latitude,
        longitude,
        stations
    )

    if nearest_station is None:
        return {
            "city_name": city_name,
            "error": "Nie znaleziono najbliższej stacji pomiarowej."
        }

    sensors = get_station_sensors(
        nearest_station["Identyfikator stacji"]
    )

    sensor_results = []

    for sensor in sensors:
        sensor_id = sensor.get("Identyfikator stanowiska")

        if not sensor_id:
            continue

        sensor_data = get_sensor_data(sensor_id)

        if sensor_data is None:
            continue

        measurement = get_latest_measurement(sensor, sensor_data)

        if measurement is None:
            continue

        sensor_results.append(measurement)

    return {
        "city_name": city_name,
        "selected_location": selected_location,
        "nearest_station": {
            "id": nearest_station.get("Identyfikator stacji"),
            "code": nearest_station.get("Kod stacji"),
            "name": nearest_station.get("Nazwa stacji"),
            "city": nearest_station.get("Nazwa miasta"),
            "commune": nearest_station.get("Gmina"),
            "district": nearest_station.get("Powiat"),
            "province": nearest_station.get("Województwo"),
            "street": nearest_station.get("Ulica"),
            "latitude": nearest_station.get("WGS84 φ N"),
            "longitude": nearest_station.get("WGS84 λ E"),
        },
        "distance": distance,
        "sensors": sensor_results,
    }


def get_station_details(station):
    return {
        "id": station.get("Identyfikator stacji"),
        "code": station.get("Kod stacji"),
        "name": station.get("Nazwa stacji"),
        "city": station.get("Nazwa miasta"),
        "commune": station.get("Gmina"),
        "district": station.get("Powiat"),
        "province": station.get("Województwo"),
        "street": station.get("Ulica"),
        "latitude": station.get("WGS84 φ N"),
        "longitude": station.get("WGS84 λ E"),
    }


def get_latest_measurement_from_db(sensor_id):
    """
    Pobiera najnowszy zapisany pomiar z lokalnej bazy danych
    dla konkretnego czujnika GIOŚ.
    Jeśli nie ma realnej wartości, zwraca None.
    """

    sensor = Sensor.objects.filter(gios_id=sensor_id).first()

    if sensor is None:
        return None

    measurement = Measurement.objects.filter(
        sensor=sensor,
        value__isnull=False
    ).order_by("-timestamp").first()

    if measurement is None:
        return None

    return {
        "sensor_id": sensor.gios_id,
        "param_name": sensor.param_name,
        "param_code": sensor.param_code,
        "date": measurement.timestamp.strftime("%Y-%m-%d %H:%M"),
        "value": measurement.value,
        "unit": "µg/m³",
        "source": "Baza danych",
        "is_historical": True,
    }

def deduplicate_measurements_by_param(measurements):
    """
    Usuwa duplikaty parametrów, np. dwa PM10.
    Priorytet:
    1. pomiar z API,
    2. pomiar historyczny z wartością,
    3. pomiar z nowszą datą, jeśli źródło takie samo.
    """

    best_by_param = {}

    for measurement in measurements:
        param_code = measurement.get("param_code")
        value = measurement.get("value")

        if not param_code:
            continue

        if value is None:
            continue

        current = best_by_param.get(param_code)

        if current is None:
            best_by_param[param_code] = measurement
            continue

        current_is_api = not current.get("is_historical", False)
        new_is_api = not measurement.get("is_historical", False)

        # API ma pierwszeństwo przed historycznymi.
        if new_is_api and not current_is_api:
            best_by_param[param_code] = measurement
            continue

        # Jeśli oba są tego samego typu, wybierz nowszy po dacie tekstowej.
        current_date = current.get("date") or ""
        new_date = measurement.get("date") or ""

        if new_date > current_date:
            best_by_param[param_code] = measurement

    return list(best_by_param.values())


def get_measurements_for_station(station):
    """
    Pobiera aktualne pomiary z API GIOŚ.
    Jeśli API nie zwróci danych dla czujnika, bierze najnowszy pomiar z bazy.
    Na końcu usuwa duplikaty parametrów, np. dwa PM10.
    """

    sensor_results = []

    station_id = station.get("Identyfikator stacji")

    try:
        sensors = get_station_sensors(station_id)
    except Exception:
        sensors = []

    # Jeśli API nie zwróciło listy czujników, próbujemy wziąć czujniki z bazy.
    if not sensors:
        db_station = Station.objects.filter(gios_id=station_id).first()

        if db_station:
            for sensor in db_station.sensors.all():
                fallback_measurement = get_latest_measurement_from_db(sensor.gios_id)

                if fallback_measurement is not None:
                    sensor_results.append(fallback_measurement)

        return deduplicate_measurements_by_param(sensor_results)

    for sensor in sensors:
        sensor_id = sensor.get("Identyfikator stanowiska")

        if not sensor_id:
            continue

        sensor_data = get_sensor_data(sensor_id)

        # API nie zwróciło danych dla czujnika -> bierzemy najnowszy pomiar z bazy.
        if sensor_data is None:
            fallback_measurement = get_latest_measurement_from_db(sensor_id)

            if fallback_measurement is not None:
                sensor_results.append(fallback_measurement)

            continue

        measurement = get_latest_measurement(sensor, sensor_data)

        if measurement is None or measurement.get("value") is None:
            fallback_measurement = get_latest_measurement_from_db(sensor_id)

            if fallback_measurement is not None:
                sensor_results.append(fallback_measurement)

            continue

        measurement["source"] = "API GIOŚ"
        measurement["is_historical"] = False

        sensor_results.append(measurement)

    return deduplicate_measurements_by_param(sensor_results)

def air_quality_search(request):
    context = {}

    if request.method == "POST":
        action = request.POST.get("action")

        if action == "search_city":
            city_name = request.POST.get("city_name", "").strip()

            if not city_name:
                context["error"] = "Podaj nazwę miejscowości."
                return render(request, "air_quality_search.html", context)

            locations = search_locations(city_name)

            if not locations:
                context["error"] = "Nie znaleziono takiej miejscowości."
                context["city_name"] = city_name
                return render(request, "air_quality_search.html", context)

            location_options = []

            for loc in locations:
                location_options.append({
                    "name": loc.get("name"),
                    "latitude": loc.get("latitude"),
                    "longitude": loc.get("longitude"),
                    "admin1": loc.get("admin1"),
                    "admin2": loc.get("admin2"),
                    "country": loc.get("country"),
                })

            context = {
                "city_name": city_name,
                "location_options": location_options,
            }

        elif action == "select_location":
            city_name = request.POST.get("city_name", "").strip()
            location_name = request.POST.get("location_name", "").strip()
            latitude = request.POST.get("latitude")
            longitude = request.POST.get("longitude")
            admin1 = request.POST.get("admin1", "")
            admin2 = request.POST.get("admin2", "")

            stations = get_all_stations()

            city_stations = find_stations_by_city(
                location_name,
                stations
            )

            selected_location = {
                "name": location_name,
                "latitude": latitude,
                "longitude": longitude,
                "admin1": admin1,
                "admin2": admin2,
            }

            if not city_stations:
                nearest_station, distance = find_nearest_station(
                    latitude,
                    longitude,
                    stations
                )

                if nearest_station is None:
                    context = {
                        "city_name": location_name or city_name,
                        "selected_location": selected_location,
                        "error": "Nie znaleziono stacji pomiarowej dla tej lokalizacji."
                    }
                    return render(request, "air_quality_search.html", context)

                context = {
                    "city_name": location_name or city_name,
                    "selected_location": selected_location,
                    "station_options": [get_station_details(nearest_station)],
                    "info": "Nie znaleziono stacji dokładnie w tej miejscowości. Pokazano najbliższą dostępną stację."
                }

                return render(request, "air_quality_search.html", context)

            station_options = []

            for station in city_stations:
                station_options.append(get_station_details(station))

            context = {
                "city_name": location_name or city_name,
                "selected_location": selected_location,
                "station_options": station_options,
            }

        elif action == "select_station":
            city_name = request.POST.get("city_name", "").strip()

            location_name = request.POST.get("location_name", "").strip()
            latitude = request.POST.get("latitude")
            longitude = request.POST.get("longitude")
            admin1 = request.POST.get("admin1", "")
            admin2 = request.POST.get("admin2", "")

            station_id = request.POST.get("station_id")

            stations = get_all_stations()

            selected_station = None

            for station in stations:
                if str(station.get("Identyfikator stacji")) == str(station_id):
                    selected_station = station
                    break

            if selected_station is None:
                context["error"] = "Nie znaleziono wybranej stacji."
                return render(request, "air_quality_search.html", context)

            sensor_results = get_measurements_for_station(selected_station)
            station_aqi = calculate_station_aqi(sensor_results)

            selected_location = {
                "name": location_name or city_name,
                "latitude": latitude,
                "longitude": longitude,
                "admin1": admin1,
                "admin2": admin2,
            }

            context = {
                "city_name": location_name or city_name,
                "selected_location": selected_location,
                "nearest_station": get_station_details(selected_station),
                "distance": None,
                "sensors": sensor_results,
                "station_aqi": station_aqi,
            }

    return render(request, "air_quality_search.html", context)

def sensor_history(request, sensor_id):
    sensor = Sensor.objects.filter(gios_id=sensor_id).first()

    if sensor is None:
        context = {
            "sensor": None,
            "station": None,
            "measurements": [],
            "table_measurements": [],
            "labels": [],
            "values": [],
            "sensor_id": sensor_id,
            "days": 5,
            "error": "Brak danych historycznych dla tego czujnika. Czujnik nie został jeszcze zapisany w lokalnej bazie danych.",
        }

        return render(request, "air_quality/sensor_history.html", context)

    days = 5
    date_from = timezone.now() - timedelta(days=days)

    measurements = Measurement.objects.filter(
        sensor=sensor,
        value__isnull=False,
        timestamp__gte=date_from
    ).order_by("timestamp")

    table_measurements = Measurement.objects.filter(
        sensor=sensor,
        value__isnull=False,
        timestamp__gte=date_from
    ).order_by("-timestamp")

    labels = []
    values = []

    for measurement in measurements:
        labels.append(measurement.timestamp.strftime("%Y-%m-%d %H:%M"))
        values.append(measurement.value)

    context = {
        "sensor": sensor,
        "station": sensor.station,
        "measurements": measurements,
        "table_measurements": table_measurements,
        "labels": labels,
        "values": values,
        "sensor_id": sensor_id,
        "days": days,
        "error": None,
    }

    return render(request, "air_quality/sensor_history.html", context)

def stations_map(request):
    stations_data = get_stations_map_data()

    context = {
        "stations_data": stations_data
    }

    return render(request, "air_quality/stations_map.html", context)

def station_details(request, station_id):
    db_station = get_object_or_404(Station, gios_id=station_id)

    selected_station = {
        "Identyfikator stacji": db_station.gios_id,
        "Kod stacji": db_station.station_code,
        "Nazwa stacji": db_station.name,
        "Nazwa miasta": db_station.city_name,
        "Gmina": db_station.commune,
        "Powiat": db_station.district,
        "Województwo": db_station.province,
        "Ulica": db_station.street,
        "WGS84 φ N": db_station.latitude,
        "WGS84 λ E": db_station.longitude,
    }

    sensor_results = get_measurements_for_station(selected_station)
    station_aqi = calculate_station_aqi(sensor_results)

    selected_location = {
        "name": db_station.name,
        "latitude": db_station.latitude,
        "longitude": db_station.longitude,
        "admin1": db_station.province,
        "admin2": db_station.district,
    }

    context = {
        "city_name": db_station.city_name,
        "selected_location": selected_location,
        "nearest_station": get_station_details(selected_station),
        "distance": None,
        "sensors": sensor_results,
        "station_aqi": station_aqi,
    }

    return render(request, "air_quality_search.html", context)


def analytics_dashboard(request):
    tiles = get_dashboard_tiles()

    return render(request, "air_quality/analytics_dashboard.html", {
        "tiles": tiles,
        "has_data": bool(tiles),
    })


def analytics_city(request, city_name):
    summary = get_city_summary(city_name)
    history = get_city_history(city_name)
    current_measurements = get_current_city_measurements(city_name)
    stations = get_city_station_tiles(city_name)
    current_values = {item["param_code"]: item["value"] for item in current_measurements}
    current_status = calculate_aqi_status([
        {"param_code": param, "value": value}
        for param, value in current_values.items()
    ]) if current_values else None

    return render(request, "air_quality/analytics_city.html", {
        "city_name": city_name,
        "summary": summary,
        "history": history,
        "history_json": json.dumps(history),
        "current_measurements": current_measurements,
        "current_status": current_status,
        "stations": stations,
        "has_history": bool(history.get("labels")),
    })


def analytics_station(request, station_id):
    station = get_object_or_404(Station, gios_id=station_id)

    summary = get_station_summary(station_id)
    history = get_station_history(station_id)
    current_measurements = get_current_station_measurements(station_id)
    current_values = {item["param_code"]: item["value"] for item in current_measurements}
    current_status = calculate_aqi_status([
        {"param_code": param, "value": value}
        for param, value in current_values.items()
    ]) if current_values else None

    return render(request, "air_quality/analytics_station.html", {
        "station": station,
        "summary": summary,
        "history": history,
        "history_json": json.dumps(history),
        "current_measurements": current_measurements,
        "current_status": current_status,
        "has_history": bool(history.get("labels")),
    })