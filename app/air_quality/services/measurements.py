def get_latest_measurement(sensor, sensor_data):
    """
    Zwraca najnowszy pomiar z danego czujnika w uproszczonej formie.
    """

    if not sensor_data:
        return None

    values = sensor_data.get("Lista danych pomiarowych", [])

    if not values:
        return {
            "param_name": sensor.get("Wskaźnik"),
            "param_code": sensor.get("Wskaźnik - kod"),
            "date": None,
            "value": None,
            "unit": "µg/m³",
        }

    latest_valid_value = None

    for item in values:
        value = item.get("Wartość")

        if value is not None:
            latest_valid_value = item
            break

    if latest_valid_value is None:
        return {
            "param_name": sensor.get("Wskaźnik"),
            "param_code": sensor.get("Wskaźnik - kod"),
            "date": None,
            "value": None,
            "unit": "µg/m³",
        }

    return {
        "param_name": sensor.get("Wskaźnik"),
        "param_code": sensor.get("Wskaźnik - kod"),
        "date": latest_valid_value.get("Data"),
        "value": latest_valid_value.get("Wartość"),
        "unit": "µg/m³",
    }