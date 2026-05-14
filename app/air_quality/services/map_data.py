from air_quality.models import Station, Measurement
from air_quality.services.aqi import calculate_station_aqi


def get_latest_station_measurements(station):
    """
    Pobiera najnowszy pomiar dla każdego czujnika danej stacji.
    Dane pochodzą z lokalnej bazy.
    """

    measurements = []

    for sensor in station.sensors.all():
        latest_measurement = Measurement.objects.filter(
            sensor=sensor,
            value__isnull=False
        ).order_by("-timestamp").first()

        if latest_measurement is None:
            continue

        measurements.append({
            "sensor_id": sensor.gios_id,
            "param_name": sensor.param_name,
            "param_code": sensor.param_code,
            "date": latest_measurement.timestamp.strftime("%Y-%m-%d %H:%M"),
            "value": latest_measurement.value,
            "unit": "µg/m³",
            "source": "Baza danych",
            "is_historical": True,
        })

    return measurements


def get_stations_map_data():
    """
    Przygotowuje dane stacji do wyświetlenia na mapie.
    Każda stacja dostaje ocenę jakości powietrza na podstawie najnowszych pomiarów.
    """

    stations = Station.objects.prefetch_related("sensors").all()

    map_points = []

    for station in stations:
        latest_measurements = get_latest_station_measurements(station)
        station_aqi = calculate_station_aqi(latest_measurements)

        map_points.append({
            "id": station.gios_id,
            "name": station.name,
            "city": station.city_name,
            "province": station.province,
            "latitude": station.latitude,
            "longitude": station.longitude,
            "aqi_level": station_aqi.get("level"),
            "color": station_aqi.get("color"),
            "description": station_aqi.get("description"),
            "worst_param": station_aqi.get("worst_param"),
            "value": station_aqi.get("value"),
        })

    return map_points