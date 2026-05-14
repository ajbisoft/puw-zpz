from django.conf import settings
from django.core.mail import send_mail

from air_quality.models import Station, Measurement
from air_quality.services.aqi import calculate_station_aqi
from locations.models import FavoriteLocation


def get_latest_station_measurements(station):
    """
    Pobiera najnowszy pomiar dla każdego parametru danej stacji z lokalnej bazy.
    """

    measurements = []

    sensors = station.sensors.all()

    for sensor in sensors:
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


def get_message_for_air_quality(aqi_level, station_name, city_name, worst_param, value):
    """
    Zwraca temat i treść maila zależnie od jakości powietrza.
    """

    if aqi_level == "Bardzo dobry":
        subject = f"Jakość powietrza bardzo dobra — {station_name}"
        body = (
            f"Cześć!\n\n"
            f"Jakość powietrza dla stacji {station_name} ({city_name}) jest bardzo dobra.\n"
            f"Możesz spokojnie aktywnie spędzać czas na świeżym powietrzu.\n\n"
            f"Najgorszy parametr: {worst_param or 'brak'}"
            f"{f' = {value}' if value is not None else ''}\n\n"
            f"To automatyczne powiadomienie z aplikacji jakości powietrza."
        )

    elif aqi_level == "Dobry":
        subject = f"Jakość powietrza dobra — {station_name}"
        body = (
            f"Cześć!\n\n"
            f"Jakość powietrza dla stacji {station_name} ({city_name}) jest dobra.\n"
            f"Warunki są korzystne — można wyjść na spacer, rower lub inną aktywność na zewnątrz.\n\n"
            f"Najgorszy parametr: {worst_param or 'brak'}"
            f"{f' = {value}' if value is not None else ''}\n\n"
            f"To automatyczne powiadomienie z aplikacji jakości powietrza."
        )

    elif aqi_level == "Umiarkowany":
        subject = f"Jakość powietrza umiarkowana — {station_name}"
        body = (
            f"Cześć!\n\n"
            f"Jakość powietrza dla stacji {station_name} ({city_name}) jest umiarkowana.\n"
            f"Większość osób może normalnie przebywać na zewnątrz, ale osoby wrażliwe "
            f"powinny rozważyć ograniczenie dłuższej aktywności na dworze.\n\n"
            f"Najgorszy parametr: {worst_param or 'brak'}"
            f"{f' = {value}' if value is not None else ''}\n\n"
            f"To automatyczne powiadomienie z aplikacji jakości powietrza."
        )

    elif aqi_level == "Dostateczny":
        subject = f"Jakość powietrza dostateczna — {station_name}"
        body = (
            f"Cześć!\n\n"
            f"Jakość powietrza dla stacji {station_name} ({city_name}) jest dostateczna.\n"
            f"Jeśli planujesz intensywny trening na zewnątrz, warto rozważyć krótszą aktywność "
            f"albo wybrać spokojniejszą formę ruchu.\n\n"
            f"Najgorszy parametr: {worst_param or 'brak'}"
            f"{f' = {value}' if value is not None else ''}\n\n"
            f"To automatyczne powiadomienie z aplikacji jakości powietrza."
        )

    elif aqi_level == "Zły":
        subject = f"Uwaga: zła jakość powietrza — {station_name}"
        body = (
            f"Cześć!\n\n"
            f"Jakość powietrza dla stacji {station_name} ({city_name}) jest zła.\n"
            f"Zalecane jest ograniczenie aktywności na zewnątrz, szczególnie dla dzieci, seniorów "
            f"i osób z problemami oddechowymi lub krążeniowymi.\n\n"
            f"Najgorszy parametr: {worst_param or 'brak'}"
            f"{f' = {value}' if value is not None else ''}\n\n"
            f"To automatyczne powiadomienie z aplikacji jakości powietrza."
        )

    elif aqi_level == "Bardzo zły":
        subject = f"Alarm: bardzo zła jakość powietrza — {station_name}"
        body = (
            f"Cześć!\n\n"
            f"Jakość powietrza dla stacji {station_name} ({city_name}) jest bardzo zła.\n"
            f"Lepiej unikać aktywności na zewnątrz i ograniczyć przebywanie na dworze do minimum.\n\n"
            f"Najgorszy parametr: {worst_param or 'brak'}"
            f"{f' = {value}' if value is not None else ''}\n\n"
            f"To automatyczne powiadomienie z aplikacji jakości powietrza."
        )

    else:
        subject = f"Brak pełnej oceny jakości powietrza — {station_name}"
        body = (
            f"Cześć!\n\n"
            f"Nie udało się jednoznacznie określić jakości powietrza dla stacji "
            f"{station_name} ({city_name}).\n"
            f"Brakuje wystarczających danych albo nie ma progów AQI dla dostępnych parametrów.\n\n"
            f"To automatyczne powiadomienie z aplikacji jakości powietrza."
        )

    return subject, body


def send_air_quality_emails_for_favorite_stations():
    """
    Wysyła użytkownikom e-maile o jakości powietrza dla ich ulubionych stacji.
    Wysyła wiadomość zawsze, niezależnie od tego, czy jakość jest dobra czy zła.
    """

    favorite_stations = FavoriteLocation.objects.select_related("user").all()

    sent_count = 0

    for favorite in favorite_stations:
        user = favorite.user

        if not user.email:
            continue

        if not favorite.nearest_station_id:
            continue

        station = Station.objects.filter(
            gios_id=favorite.nearest_station_id
        ).first()

        if station is None:
            continue

        latest_measurements = get_latest_station_measurements(station)
        station_aqi = calculate_station_aqi(latest_measurements)

        aqi_level = station_aqi.get("level")
        worst_param = station_aqi.get("worst_param")
        value = station_aqi.get("value")

        subject, body = get_message_for_air_quality(
            aqi_level=aqi_level,
            station_name=station.name,
            city_name=station.city_name,
            worst_param=worst_param,
            value=value,
        )

        send_mail(
            subject=subject,
            message=body,
            from_email=getattr(settings, "DEFAULT_FROM_EMAIL", None),
            recipient_list=[user.email],
            fail_silently=False,
        )

        sent_count += 1

    return sent_count