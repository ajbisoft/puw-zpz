from air_quality.models import AQINorm


LEVEL_ORDER = {
    "Bardzo dobry": 1,
    "Dobry": 2,
    "Umiarkowany": 3,
    "Dostateczny": 4,
    "Zły": 5,
    "Bardzo zły": 6,
}


DEFAULT_AQI = {
    "level": "Brak danych",
    "color": "#6c757d",
    "description": "Brak wystarczających danych do określenia jakości powietrza.",
    "worst_param": None,
}


def get_aqi_for_measurement(param_code, value):
    """
    Zwraca ocenę jakości powietrza dla pojedynczego parametru i wartości.
    """

    if param_code is None or value is None:
        return None

    try:
        numeric_value = float(str(value).replace(",", "."))
    except ValueError:
        return None

    norm = AQINorm.objects.filter(
        param_code=param_code,
        min_value__lte=numeric_value,
        max_value__gte=numeric_value,
    ).first()

    if norm is None:
        return None

    return {
        "param_code": param_code,
        "value": numeric_value,
        "level": norm.index_level,
        "color": norm.color_hex,
        "order": LEVEL_ORDER.get(norm.index_level, 999),
    }


def calculate_station_aqi(measurements):
    """
    Wylicza ogólną jakość powietrza dla stacji.
    Bierze najgorszy poziom spośród dostępnych pomiarów.
    """

    results = []

    for measurement in measurements:
        param_code = measurement.get("param_code")
        value = measurement.get("value")

        result = get_aqi_for_measurement(param_code, value)

        if result is not None:
            results.append(result)

    if not results:
        return DEFAULT_AQI

    worst_result = max(results, key=lambda item: item["order"])

    return {
        "level": worst_result["level"],
        "color": worst_result["color"],
        "description": f"Ocena na podstawie najgorszego parametru: {worst_result['param_code']} = {worst_result['value']}.",
        "worst_param": worst_result["param_code"],
        "value": worst_result["value"],
        "all_results": results,
    }