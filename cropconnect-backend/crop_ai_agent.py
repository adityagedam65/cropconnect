from typing import Any

CORE_READING_FIELDS = ("soil_moisture", "humidity", "temperature", "ph")
OPTIONAL_READING_FIELDS = ("nitrogen", "phosphorus", "potassium")


def missing_crop_readings(context: dict[str, Any]) -> list[str]:
    missing = []
    for field in (*CORE_READING_FIELDS, *OPTIONAL_READING_FIELDS):
        if context.get(field) is None:
            missing.append(field)
    return missing


def has_core_sensor_context(context: dict[str, Any]) -> bool:
    return all(context.get(field) is not None for field in CORE_READING_FIELDS)
