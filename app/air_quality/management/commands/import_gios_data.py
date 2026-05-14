import time

from django.core.management.base import BaseCommand
from django.utils.dateparse import parse_datetime
from django.utils import timezone

from air_quality.services.email_alerts import send_air_quality_emails_for_favorite_stations
from air_quality.models import Station, Sensor, Measurement, AQINorm
from air_quality.services.gios_client import (
    get_all_stations,
    get_station_sensors,
    get_sensor_data,
)


# ALLOWED_PARAMETERS = {"PM10", "PM2.5", "O3", "NO2", "SO2", "C6H6", "CO"}


AQI_NORMS_DATA = [
    ("PM10", "Bardzo dobry", 0, 20, "#50B748"),
    ("PM10", "Dobry", 20.1, 50, "#B0D235"),
    ("PM10", "Umiarkowany", 50.1, 80, "#F8C300"),
    ("PM10", "Dostateczny", 80.1, 110, "#F27921"),
    ("PM10", "Zły", 110.1, 150, "#E2001A"),
    ("PM10", "Bardzo zły", 150.1, 9999, "#8A0E1A"),

    ("PM2.5", "Bardzo dobry", 0, 13, "#50B748"),
    ("PM2.5", "Dobry", 13.1, 35, "#B0D235"),
    ("PM2.5", "Umiarkowany", 35.1, 55, "#F8C300"),
    ("PM2.5", "Dostateczny", 55.1, 75, "#F27921"),
    ("PM2.5", "Zły", 75.1, 110, "#E2001A"),
    ("PM2.5", "Bardzo zły", 110.1, 9999, "#8A0E1A"),

    ("O3", "Bardzo dobry", 0, 70, "#50B748"),
    ("O3", "Dobry", 70.1, 120, "#B0D235"),
    ("O3", "Umiarkowany", 120.1, 150, "#F8C300"),
    ("O3", "Dostateczny", 150.1, 180, "#F27921"),
    ("O3", "Zły", 180.1, 240, "#E2001A"),
    ("O3", "Bardzo zły", 240.1, 9999, "#8A0E1A"),

    ("NO2", "Bardzo dobry", 0, 40, "#50B748"),
    ("NO2", "Dobry", 40.1, 100, "#B0D235"),
    ("NO2", "Umiarkowany", 100.1, 150, "#F8C300"),
    ("NO2", "Dostateczny", 150.1, 230, "#F27921"),
    ("NO2", "Zły", 230.1, 400, "#E2001A"),
    ("NO2", "Bardzo zły", 400.1, 9999, "#8A0E1A"),

    ("SO2", "Bardzo dobry", 0, 50, "#50B748"),
    ("SO2", "Dobry", 50.1, 100, "#B0D235"),
    ("SO2", "Umiarkowany", 100.1, 200, "#F8C300"),
    ("SO2", "Dostateczny", 200.1, 350, "#F27921"),
    ("SO2", "Zły", 350.1, 500, "#E2001A"),
    ("SO2", "Bardzo zły", 500.1, 9999, "#8A0E1A"),
]


class Command(BaseCommand):
    help = "Importuje stacje, czujniki, normy AQI i pomiary z API GIOŚ do bazy Django."

    def add_arguments(self, parser):
        parser.add_argument(
            "--limit",
            type=int,
            default=None,
            help="Ogranicza liczbę importowanych stacji, np. --limit 5"
        )

        parser.add_argument(
            "--sleep",
            type=float,
            default=0.1,
            help="Pauza między zapytaniami do API, domyślnie 0.1 sekundy"
        )

        parser.add_argument(
            "--skip-measurements",
            action="store_true",
            help="Importuje tylko stacje i czujniki, bez pomiarów"
        )

    def handle(self, *args, **options):
        limit = options["limit"]
        sleep_time = options["sleep"]
        skip_measurements = options["skip_measurements"]

        self.stdout.write("Start importu danych GIOŚ...")

        self.import_aqi_norms()

        stations_data = get_all_stations(size=500)

        if limit:
            stations_data = stations_data[:limit]

        self.stdout.write(f"Liczba stacji do przetworzenia: {len(stations_data)}")

        total_stations = 0
        total_sensors = 0
        total_measurements = 0

        for index, station_data in enumerate(stations_data, start=1):
            station = self.save_station(station_data)
            total_stations += 1

            self.stdout.write(
                f"[{index}/{len(stations_data)}] Stacja: {station.name} ({station.city_name})"
            )

            try:
                sensors_data = get_station_sensors(station.gios_id)
            except Exception as error:
                self.stdout.write(
                    self.style.WARNING(
                        f"  Nie udało się pobrać czujników dla stacji {station.gios_id}: {error}"
                    )
                )
                continue

            for sensor_data in sensors_data:
                sensor = self.save_sensor(sensor_data, station)

                if sensor is None:
                    continue

                total_sensors += 1

                self.stdout.write(f"  Czujnik: {sensor.param_code}")

                if skip_measurements:
                    continue

                sensor_measurements = get_sensor_data(sensor.gios_id)

                if sensor_measurements is None:
                    continue

                saved_count = self.save_measurements(sensor, sensor_measurements)
                total_measurements += saved_count

                if saved_count:
                    self.stdout.write(f"    Zapisano nowych pomiarów: {saved_count}")

                time.sleep(sleep_time)

        self.stdout.write("")
        self.stdout.write(self.style.SUCCESS("Import zakończony."))
        self.stdout.write(f"Stacje przetworzone: {total_stations}")
        self.stdout.write(f"Czujniki przetworzone: {total_sensors}")
        self.stdout.write(f"Nowe pomiary zapisane: {total_measurements}")

        if total_measurements > 0:
            self.stdout.write("")
            self.stdout.write("Wysyłam powiadomienia e-mail dla ulubionych stacji...")

            sent_count = send_air_quality_emails_for_favorite_stations()

            self.stdout.write(
                self.style.SUCCESS(f"Wysłano powiadomień e-mail: {sent_count}")
            )
        else:
            self.stdout.write("")
            self.stdout.write("Brak nowych pomiarów — pomijam wysyłanie powiadomień.")

    def import_aqi_norms(self):
        self.stdout.write("Importuję normy AQI...")

        for param_code, index_level, min_value, max_value, color_hex in AQI_NORMS_DATA:
            AQINorm.objects.update_or_create(
                param_code=param_code,
                index_level=index_level,
                defaults={
                    "min_value": min_value,
                    "max_value": max_value,
                    "color_hex": color_hex,
                }
            )

    def save_station(self, station_data):
        station, created = Station.objects.update_or_create(
            gios_id=station_data.get("Identyfikator stacji"),
            defaults={
                "station_code": station_data.get("Kod stacji", ""),
                "name": station_data.get("Nazwa stacji", ""),
                "latitude": self.parse_float(station_data.get("WGS84 φ N")) or 0.0,
                "longitude": self.parse_float(station_data.get("WGS84 λ E")) or 0.0,
                "city_name": station_data.get("Nazwa miasta", ""),
                "commune": station_data.get("Gmina", ""),
                "district": station_data.get("Powiat", ""),
                "province": station_data.get("Województwo", ""),
                "street": station_data.get("Ulica", ""),
            }
        )

        return station

    def save_sensor(self, sensor_data, station):
        sensor_id = sensor_data.get("Identyfikator stanowiska")
        param_code = sensor_data.get("Wskaźnik - kod")

        if not sensor_id:
            return None

        if not param_code:
            param_code = "UNKNOWN"

        sensor, created = Sensor.objects.update_or_create(
            gios_id=sensor_id,
            defaults={
                "station": station,
                "param_name": sensor_data.get("Wskaźnik", ""),
                "param_code": param_code,
                "param_formula": sensor_data.get("Wskaźnik - wzór", ""),
            }
        )

        return sensor

    def save_measurements(self, sensor, sensor_measurements):
        values = self.extract_measurement_values(sensor_measurements)

        saved_count = 0

        for item in values:
            timestamp_raw = self.get_first_existing_value(
                item,
                ["Data", "data", "date", "timestamp", "czas"]
            )

            value_raw = self.get_first_existing_value(
                item,
                ["Wartość", "wartosc", "value", "val"]
            )

            if timestamp_raw is None:
                continue

            timestamp = parse_datetime(str(timestamp_raw))

            if timestamp is None:
                continue

            if timezone.is_naive(timestamp):
                timestamp = timezone.make_aware(timestamp, timezone.get_current_timezone())

            value = self.parse_float(value_raw) if value_raw is not None else None

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

    def extract_measurement_values(self, sensor_measurements):
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

    def get_first_existing_value(self, dictionary, keys):
        if not isinstance(dictionary, dict):
            return None

        for key in keys:
            if key in dictionary:
                return dictionary[key]

        return None

    def parse_float(self, value):
        if value is None or value == "":
            return None

        if isinstance(value, str):
            value = value.replace(",", ".")

        try:
            return float(value)
        except ValueError:
            return None