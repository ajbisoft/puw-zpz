from django.utils import timezone
from django.utils.dateparse import parse_datetime

from air_quality.models import Station, Sensor, Measurement
from air_quality.services.gios_client import get_station_sensors, get_sensor_data


def parse_float(value):
    if value is None or value == "":
        return None

    if isinstance(value, str):
        value = value.replace(",", ".")

    try:
        return float(value)
    except ValueError:
        return None


def get_first_existing_value(dictionary, keys):
    if not isinstance(dictionary, dict):
        return None

    for key in keys:
        if key in dictionary:
            return dictionary[key]

    return None


def extract_measurement_values(sensor_measurements):
    if isinstance(sensor_measurements, list):
        return sensor_measurements

    if isinstance(sensor_measurements, dict):
        possible_keys = [
            "Lista danych pomiarowych",
            "values",
            "items",
            "results",
            "hydra:member",
            "member",
        ]

        for key in possible_keys:
            value = sensor_measurements.get(key)
            if isinstance(value, list):
                return value

        for value in sensor_measurements.values():
            if isinstance(value, list):
                return value

    return []


def save_sensor(sensor_data, station):
    sensor_id = (
        sensor_data.get("Identyfikator stanowiska")
        or sensor_data.get("id")
        or sensor_data.get("sensorId")
    )

    param_code = (
        sensor_data.get("Wskaźnik - kod")
        or sensor_data.get("param_code")
        or sensor_data.get("paramCode")
        or sensor_data.get("param", {}).get("paramCode", None)
    )

    param_name = (
        sensor_data.get("Wskaźnik")
        or sensor_data.get("param_name")
        or sensor_data.get("paramName")
        or sensor_data.get("param", {}).get("paramName", "")
    )

    param_formula = (
        sensor_data.get("Wskaźnik - wzór")
        or sensor_data.get("param_formula")
        or sensor_data.get("paramFormula")
        or sensor_data.get("param", {}).get("paramFormula", "")
    )

    if not sensor_id:
        return None

    if not param_code:
        param_code = "UNKNOWN"

    sensor, created = Sensor.objects.update_or_create(
        gios_id=sensor_id,
        defaults={
            "station": station,
            "param_name": param_name or param_code,
            "param_code": param_code,
            "param_formula": param_formula or "",
        }
    )

    return sensor


def save_measurements(sensor, sensor_measurements):
    values = extract_measurement_values(sensor_measurements)

    saved_count = 0

    for item in values:
        timestamp_raw = get_first_existing_value(
            item,
            ["Data", "data", "date", "timestamp", "czas"]
        )

        value_raw = get_first_existing_value(
            item,
            ["Wartość", "wartosc", "value", "val"]
        )

        if timestamp_raw is None:
            continue

        timestamp = parse_datetime(str(timestamp_raw))

        if timestamp is None:
            continue

        if timezone.is_naive(timestamp):
            timestamp = timezone.make_aware(
                timestamp,
                timezone.get_current_timezone()
            )

        value = parse_float(value_raw) if value_raw is not None else None

        measurement, created = Measurement.objects.get_or_create(
            sensor=sensor,
            timestamp=timestamp,
            defaults={
                "value": value
            }
        )

        if created:
            saved_count += 1
        else:
            if measurement.value != value:
                measurement.value = value
                measurement.save(update_fields=["value"])

    return saved_count


def sync_station_measurements(station):
    """
    Pobiera czujniki i pomiary dla jednej stacji.
    Zwraca liczbę nowych pomiarów.
    """

    sensors_data = get_station_sensors(station.gios_id)

    total_saved = 0

    for sensor_data in sensors_data:
        sensor = save_sensor(sensor_data, station)

        if sensor is None:
            continue

        sensor_measurements = get_sensor_data(sensor.gios_id)

        if sensor_measurements is None:
            continue

        saved_count = save_measurements(sensor, sensor_measurements)
        total_saved += saved_count

    return total_saved