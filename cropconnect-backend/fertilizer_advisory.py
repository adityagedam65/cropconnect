"""Fixed, unit-explicit soil nutrient status advice; never fertilizer dosages."""

from typing import Any


NUTRIENT_BANDS = {
    "nitrogen": (280.0, 560.0),
    "phosphorus": (10.0, 25.0),
    "potassium": (110.0, 280.0),
}
NUTRIENT_UNIT = "kg/ha equivalent"

ACTION_BY_STATUS = {
    "low": "{name} is low; consider a {name_lower}-rich fertilizer, following local agricultural extension guidance.",
    "medium": "{name} is in the medium status band; maintain nutrient management with local agricultural extension guidance.",
    "high": "{name} is high; additional {name_lower} fertilizer is not recommended right now.",
    "unavailable": "{name} is unavailable, so its nutrient status cannot be assessed.",
}


def nutrient_status(value: float | None, low_max: float, medium_max: float) -> str:
    """Return a status band without treating an absent sensor value as zero."""
    if value is None:
        return "unavailable"
    numeric_value = float(value)
    if numeric_value < low_max:
        return "low"
    if numeric_value <= medium_max:
        return "medium"
    return "high"


def evaluate_fertilizer_advice(
    nitrogen: float | None, phosphorus: float | None, potassium: float | None,
) -> dict[str, Any]:
    """Evaluate supplied values as verified kg/ha-equivalent measurements only."""
    values = {"nitrogen": nitrogen, "phosphorus": phosphorus, "potassium": potassium}
    nutrients: dict[str, dict[str, Any]] = {}
    missing: list[str] = []
    for key, value in values.items():
        low_max, medium_max = NUTRIENT_BANDS[key]
        status = nutrient_status(value, low_max, medium_max)
        name = key.capitalize()
        if status == "unavailable":
            missing.append(key)
        nutrients[key] = {
            "value": value,
            "status": status,
            "action": ACTION_BY_STATUS[status].format(name=name, name_lower=key),
            "bands": {"low_below": low_max, "medium_through": medium_max, "unit": NUTRIENT_UNIT},
        }
    return {"nutrients": nutrients, "missingReadings": missing, "unit": NUTRIENT_UNIT}
