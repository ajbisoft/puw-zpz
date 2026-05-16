from datetime import timedelta
from django.db.models import Avg, F, Max, OuterRef, Subquery
from django.db.models.functions import TruncDay
from django.utils import timezone

from air_quality.models import Measurement, Sensor, Station
from air_quality.services.aqi import (
    POLLUTANTS,
    calculate_aqi_status,
    normalize_param_code,
    percent_of_norm,
    pollutant_aqi_status,
)


HISTORY_WINDOW = timedelta(days=7)
CURRENT_WINDOW = timedelta(hours=3)


def _recent_measurement_query():
    return Measurement.objects.filter(
        sensor=OuterRef("pk"),
        timestamp__gte=timezone.now() - CURRENT_WINDOW,
        value__isnull=False,
    ).order_by("-timestamp")


def _historical_measurements():
    # Return all measurements from the last 7 days window.
    # This works with any available data inside that interval,
    # even if there are only 1-2 days of measurements.
    return Measurement.objects.filter(
        timestamp__gte=timezone.now() - HISTORY_WINDOW,
        value__isnull=False,
        sensor__param_code__in=POLLUTANTS,
    ).select_related("sensor__station")


def _clean_param(param_code):
    return normalize_param_code(param_code) if param_code else None


def get_dashboard_tiles():
    city_names = Sensor.objects.filter(param_code__in=POLLUTANTS).values_list(
        "station__city_name", flat=True
    ).distinct()

    tiles = []

    for city_name in city_names:
        measurements = get_current_city_measurements(city_name)

        if not measurements:
            continue

        pollutants = {item["param_code"]: item["value"] for item in measurements}
        status = calculate_aqi_status(
            [{"param_code": item["param_code"], "value": item["value"]} for item in measurements]
        )

        tiles.append(
            {
                "city_name": city_name,
                "status_label": status["level"],
                "status_color": status["color_hex"],
                "advice": status["advice"],
                "order": status["order"],
                "pollutants": pollutants,
                "detail_url": f"/air_quality/analytics/city/{city_name}/",
            }
        )

    return sorted(tiles, key=lambda item: (-item["order"], item["city_name"]))


def get_city_summary(city_name):
    records = (
        _historical_measurements()
        .filter(sensor__station__city_name__iexact=city_name)
        .values(pollutant=F("sensor__param_code"))
        .annotate(avg_value=Avg("value"), max_value=Max("value"))
    )

    pollutants = {}

    for record in records:
        pollutant = _clean_param(record["pollutant"])
        if pollutant is None:
            continue

        avg_status = pollutant_aqi_status(pollutant, record["avg_value"])
        max_status = pollutant_aqi_status(pollutant, record["max_value"])

        pollutants[pollutant] = {
            "avg_value": record["avg_value"],
            "avg_percent_norm": percent_of_norm(record["avg_value"], pollutant),
            "avg_color": avg_status["color_hex"] if avg_status else "#6c757d",
            "avg_text_color": "#000" if avg_status and avg_status["order"] == 3 else "#fff",
            "max_value": record["max_value"],
            "max_percent_norm": percent_of_norm(record["max_value"], pollutant),
            "max_color": max_status["color_hex"] if max_status else "#6c757d",
            "max_text_color": "#000" if max_status and max_status["order"] == 3 else "#fff",
        }

    if not pollutants:
        return None

    status = calculate_aqi_status(
        [{"param_code": key, "value": value["avg_value"]} for key, value in pollutants.items()]
    )

    return {
        "city_name": city_name,
        "pollutants": pollutants,
        "status": status,
        "updated_at": timezone.now(),
    }


def get_station_summary(station_id):
    records = (
        _historical_measurements()
        .filter(sensor__station__gios_id=station_id)
        .values(pollutant=F("sensor__param_code"))
        .annotate(avg_value=Avg("value"), max_value=Max("value"))
    )

    pollutants = {}

    for record in records:
        pollutant = _clean_param(record["pollutant"])
        if pollutant is None:
            continue

        avg_status = pollutant_aqi_status(pollutant, record["avg_value"])
        max_status = pollutant_aqi_status(pollutant, record["max_value"])

        pollutants[pollutant] = {
            "avg_value": record["avg_value"],
            "avg_percent_norm": percent_of_norm(record["avg_value"], pollutant),
            "avg_color": avg_status["color_hex"] if avg_status else "#6c757d",
            "avg_text_color": "#000" if avg_status and avg_status["order"] == 3 else "#fff",
            "max_value": record["max_value"],
            "max_percent_norm": percent_of_norm(record["max_value"], pollutant),
            "max_color": max_status["color_hex"] if max_status else "#6c757d",
            "max_text_color": "#000" if max_status and max_status["order"] == 3 else "#fff",
        }

    if not pollutants:
        return None

    status = calculate_aqi_status(
        [{"param_code": key, "value": value["avg_value"]} for key, value in pollutants.items()]
    )

    return {
        "station_id": station_id,
        "pollutants": pollutants,
        "status": status,
        "updated_at": timezone.now(),
    }


def get_city_history(city_name):
    records = (
        _historical_measurements()
        .filter(sensor__station__city_name__iexact=city_name)
        .annotate(day=TruncDay("timestamp"))
        .values("day", pollutant=F("sensor__param_code"))
        .annotate(avg_value=Avg("value"))
        .order_by("day")
    )

    if not records:
        return {"labels": [], "datasets": []}

    timeline = {}
    days = []

    for record in records:
        day = record["day"].date()
        pollutant = _clean_param(record["pollutant"])
        if pollutant is None:
            continue

        timeline.setdefault(day, {})[pollutant] = record["avg_value"]

    sorted_days = sorted(timeline.keys())
    labels = [day.strftime("%d %b") for day in sorted_days]

    datasets = []
    for pollutant in POLLUTANTS:
        data = [timeline[day].get(pollutant) for day in sorted_days]
        datasets.append(
            {
                "label": pollutant,
                "data": [value if value is not None else None for value in data],
            }
        )

    return {"labels": labels, "datasets": datasets}


def get_station_history(station_id):
    records = (
        _historical_measurements()
        .filter(sensor__station__gios_id=station_id)
        .annotate(day=TruncDay("timestamp"))
        .values("day", pollutant=F("sensor__param_code"))
        .annotate(avg_value=Avg("value"))
        .order_by("day")
    )

    if not records:
        return {"labels": [], "datasets": []}

    timeline = {}
    for record in records:
        day = record["day"].date()
        pollutant = _clean_param(record["pollutant"])
        if pollutant is None:
            continue

        timeline.setdefault(day, {})[pollutant] = record["avg_value"]

    sorted_days = sorted(timeline.keys())
    labels = [day.strftime("%d %b") for day in sorted_days]

    datasets = []
    for pollutant in POLLUTANTS:
        data = [timeline[day].get(pollutant) for day in sorted_days]
        datasets.append(
            {
                "label": pollutant,
                "data": [value if value is not None else None for value in data],
            }
        )

    return {"labels": labels, "datasets": datasets}


def _latest_measurements_for_sensors(filter_kwargs):
    recent_subquery = _recent_measurement_query()
    sensors = (
        Sensor.objects.filter(**filter_kwargs, param_code__in=POLLUTANTS)
        .annotate(
            latest_value=Subquery(recent_subquery.values("value")[:1]),
            latest_timestamp=Subquery(recent_subquery.values("timestamp")[:1]),
        )
        .select_related("station")
    )

    current = {}
    for sensor in sensors:
        pollutant = _clean_param(sensor.param_code)
        if pollutant is None or sensor.latest_value is None:
            continue

        existing = current.get(pollutant)
        if existing is None or sensor.latest_timestamp > existing["timestamp"]:
            current[pollutant] = {
                "param_code": pollutant,
                "value": sensor.latest_value,
                "timestamp": sensor.latest_timestamp,
                "percent_norm": percent_of_norm(sensor.latest_value, pollutant),
            }

    return [current[param] for param in POLLUTANTS if param in current]


def get_current_city_measurements(city_name):
    return _latest_measurements_for_sensors({"station__city_name__iexact": city_name})


def get_city_station_tiles(city_name):
    stations = Station.objects.filter(city_name__iexact=city_name).order_by("name")
    station_tiles = []

    for station in stations:
        measurements = get_current_station_measurements(station.gios_id)
        if not measurements:
            continue

        pollutants = {item["param_code"]: item["value"] for item in measurements}
        status = calculate_aqi_status(
            [{"param_code": item["param_code"], "value": item["value"]} for item in measurements]
        )

        station_tiles.append(
            {
                "station_id": station.gios_id,
                "name": station.name,
                "status_label": status["level"],
                "status_color": status["color_hex"],
                "order": status["order"],
                "pollutants": pollutants,
            }
        )

    return sorted(station_tiles, key=lambda item: (-item["order"], item["name"]))


def get_current_station_measurements(station_id):
    return _latest_measurements_for_sensors({"station__gios_id": station_id})