from django.shortcuts import render, get_object_or_404

from air_quality.models import Sensor, Measurement
from air_quality.services.geocoding import search_locations
from air_quality.services.gios_client import (
    get_all_stations,
    get_station_sensors,
    get_sensor_data,
)
from air_quality.services.distance import find_nearest_station, find_stations_by_city
from air_quality.services.measurements import get_latest_measurement
from air_quality.services.aqi import calculate_station_aqi

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


def get_measurements_for_station(station):
    sensors = get_station_sensors(
        station["Identyfikator stacji"]
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

    return sensor_results

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
    sensor = get_object_or_404(Sensor, gios_id=sensor_id)

    measurements = Measurement.objects.filter(
        sensor=sensor,
        value__isnull=False
    ).order_by("timestamp")[:100]

    labels = []
    values = []

    for measurement in measurements:
        labels.append(measurement.timestamp.strftime("%Y-%m-%d %H:%M"))
        values.append(measurement.value)

    context = {
        "sensor": sensor,
        "station": sensor.station,
        "measurements": measurements,
        "labels": labels,
        "values": values,
    }

    return render(request, "air_quality/sensor_history.html", context)