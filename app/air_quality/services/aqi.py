from typing import Dict, List, Optional

POLLUTANTS = ["PM10", "PM2.5", "O3", "NO2", "SO2"]

GOOD_LIMITS = {
    "PM10": 50.0,
    "PM2.5": 35.0,
    "O3": 120.0,
    "NO2": 100.0,
    "SO2": 100.0,
}

AQI_THRESHOLDS = {
    "PM10": [
        (20.0, 1, "Bardzo dobry", "#50B748"),
        (50.0, 2, "Dobry", "#B0D235"),
        (80.0, 3, "Umiarkowany", "#F8C300"),
        (110.0, 4, "Dostateczny", "#F27921"),
        (150.0, 5, "Zły", "#E2001A"),
    ],
    "PM2.5": [
        (13.0, 1, "Bardzo dobry", "#50B748"),
        (35.0, 2, "Dobry", "#B0D235"),
        (55.0, 3, "Umiarkowany", "#F8C300"),
        (75.0, 4, "Dostateczny", "#F27921"),
        (110.0, 5, "Zły", "#E2001A"),
    ],
    "O3": [
        (70.0, 1, "Bardzo dobry", "#50B748"),
        (120.0, 2, "Dobry", "#B0D235"),
        (150.0, 3, "Umiarkowany", "#F8C300"),
        (180.0, 4, "Dostateczny", "#F27921"),
        (240.0, 5, "Zły", "#E2001A"),
    ],
    "NO2": [
        (40.0, 1, "Bardzo dobry", "#50B748"),
        (100.0, 2, "Dobry", "#B0D235"),
        (150.0, 3, "Umiarkowany", "#F8C300"),
        (230.0, 4, "Dostateczny", "#F27921"),
        (400.0, 5, "Zły", "#E2001A"),
    ],
    "SO2": [
        (50.0, 1, "Bardzo dobry", "#50B748"),
        (100.0, 2, "Dobry", "#B0D235"),
        (200.0, 3, "Umiarkowany", "#F8C300"),
        (350.0, 4, "Dostateczny", "#F27921"),
        (500.0, 5, "Zły", "#E2001A"),
    ],
}

HEALTH_ADVICE = {
    1: "Bardzo dobry: Spokojnie korzystaj z aktywności na zewnątrz.",
    2: "Dobry: Możesz bezpiecznie przebywać na zewnątrz.",
    3: "Umiarkowany: Osoby wrażliwe powinny ograniczyć dłuższy wysiłek.",
    4: "Dostateczny: Ogranicz aktywność na zewnątrz i śledź stan powietrza.",
    5: "Zły: Zostań w domu i zamknij okna.",
    6: "Bardzo zły: Unikaj wychodzenia i użyj ochrony układu oddechowego.",
}

DEFAULT_AQI = {
    "level": "Brak danych",
    "color_hex": "#6c757d",
    "color": "#6c757d",
    "description": "Brak wystarczających danych do określenia jakości powietrza.",
    "advice": "Brak aktualnych danych.",
    "order": 0,
    "parameters": {},
}


def normalize_param_code(param_code: Optional[str]) -> Optional[str]:
    if not param_code:
        return None

    normalized = str(param_code).strip().upper().replace(" ", "")

    if normalized == "PM25":
        return "PM2.5"

    if normalized in [code.replace(".", "") for code in POLLUTANTS]:
        if normalized == "PM10":
            return "PM10"
        if normalized == "PM25":
            return "PM2.5"
        return normalized

    if normalized in POLLUTANTS:
        return normalized

    return None


def percent_of_norm(value: Optional[float], param_code: str) -> Optional[float]:
    if value is None or param_code not in GOOD_LIMITS:
        return None

    return (value / GOOD_LIMITS[param_code]) * 100.0


def pollutant_aqi_status(param_code: str, value: Optional[float]) -> Optional[Dict]:
    if value is None:
        return None

    param_code = normalize_param_code(param_code)
    if param_code is None or param_code not in AQI_THRESHOLDS:
        return None

    thresholds = AQI_THRESHOLDS[param_code]

    for limit, order, label, color in thresholds:
        if value <= limit:
            return {
                "param_code": param_code,
                "value": value,
                "level": label,
                "order": order,
                "color_hex": color,
                "percent_norm": percent_of_norm(value, param_code),
            }

    return {
        "param_code": param_code,
        "value": value,
        "level": "Bardzo zły",
        "order": 6,
        "color_hex": "#8A0E1A",
        "percent_norm": percent_of_norm(value, param_code),
    }


def calculate_aqi_status(measurements: List[Dict]) -> Dict:
    statuses = []

    for measurement in measurements:
        param_code = measurement.get("param_code")
        value = measurement.get("value")
        result = pollutant_aqi_status(param_code, value)

        if result is not None:
            statuses.append(result)

    if not statuses:
        return DEFAULT_AQI

    worst = max(statuses, key=lambda item: item["order"])

    return {
        "level": worst["level"],
        "color_hex": worst["color_hex"],
        "color": worst["color_hex"],
        "description": f"Główne zanieczyszczenie: {worst['param_code']} ({worst['value']:.1f} µg/m³)",
        "advice": HEALTH_ADVICE.get(worst["order"], HEALTH_ADVICE[6]),
        "order": worst["order"],
        "parameters": {item["param_code"]: item for item in statuses},
    }


def calculate_station_aqi(measurements: List[Dict]) -> Dict:
    return calculate_aqi_status(measurements)
