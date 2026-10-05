"""Pure, deterministic crop suitability scoring."""

from typing import Any

from crop_knowledge import CROP_DATABASE


FACTOR_CONFIG = (
    ("ph", "ph_range", 0.18, "Soil pH"),
    ("soil_moisture", "moisture_range", 0.18, "Soil moisture"),
    ("temperature", "temp_range", 0.12, "Temperature"),
    ("humidity", "humidity_range", 0.12, "Humidity"),
    ("nitrogen", "nitrogen_range", 0.09, "Nitrogen"),
    ("phosphorus", "phosphorus_range", 0.09, "Phosphorus"),
    ("potassium", "potassium_range", 0.09, "Potassium"),
    ("rainfall", "rainfall_range", 0.13, "Rainfall (7-day forecast)"),
)


def score_factor(value: float | None, range_min: float, range_max: float) -> float | None:
    """Return 100 in range, decaying linearly to zero one range-width outside it."""
    if value is None:
        return None
    value = float(value)
    range_min, range_max = float(range_min), float(range_max)
    if range_min > range_max:
        raise ValueError("range_min must not be greater than range_max")
    if range_min <= value <= range_max:
        return 100.0
    width = max(range_max - range_min, 1.0)
    distance = range_min - value if value < range_min else value - range_max
    return max(0.0, 100.0 * (1.0 - distance / width))


def score_crop(sensor_data: dict[str, Any], crop: dict[str, Any]) -> dict[str, Any]:
    """Score one crop using only present sensor readings and explicit crop ranges."""
    factor_scores: list[tuple[float, float, str]] = []
    missing_readings: list[str] = []
    for sensor_key, range_key, weight, display_name in FACTOR_CONFIG:
        value = sensor_data.get(sensor_key)
        if value is None:
            missing_readings.append(sensor_key)
            continue
        ideal_range = crop.get(range_key)
        if ideal_range is None:
            continue
        score = score_factor(value, ideal_range[0], ideal_range[1])
        if score is not None:
            factor_scores.append((score, weight, display_name))

    if factor_scores:
        weight_total = sum(weight for _score, weight, _name in factor_scores)
        numeric_fit = sum(score * weight for score, weight, _name in factor_scores) / weight_total
        lowest_score, _weight, lowest_name = min(factor_scores, key=lambda item: item[0])
        status_message = (
            "All available readings are within the ideal ranges."
            if lowest_score >= 100 else f"{lowest_name} is outside the ideal range."
        )
    else:
        numeric_fit = 0.0
        status_message = "No comparable sensor readings are available."

    fit = int(round(numeric_fit))
    suitability = "Excellent" if fit >= 85 else "Good" if fit >= 70 else "Fair" if fit >= 50 else "Poor"
    return {
        "name": crop["name"], "category": crop["category"], "season": crop["season"],
        "cropType": crop["crop_type"], "fit": f"{fit}%", "suitability": suitability,
        "moisture_range": crop["moisture_range"], "temp_range": crop["temp_range"],
        "humidity_range": crop["humidity_range"], "ph_range": crop["ph_range"],
        "rainfall_range": crop.get("rainfall_range"),
        "description": crop["description_template"], "status_message": status_message,
        "missingReadings": missing_readings,
    }


def rank_crops(sensor_data: dict[str, Any], season: str | None = None, top_n: int = 8) -> list[dict[str, Any]]:
    """Rank crops, adding a small deterministic preference for the requested season."""
    requested_season = (season or "").strip().casefold()
    ranked: list[tuple[int, float, str, dict[str, Any]]] = []
    for crop in CROP_DATABASE:
        scored = score_crop(sensor_data, crop)
        fit = int(scored["fit"].removesuffix("%"))
        season_bonus = 3.0 if requested_season and crop["season"].casefold() == requested_season else 0.0
        # Preserve descending output by the actual displayed fit. The seasonal
        # bonus is a deterministic tie-breaker, never a hidden score change.
        ranked.append((fit, season_bonus, crop["name"], scored))
    ranked.sort(key=lambda item: (-item[0], -item[1], item[2]))
    return [crop for _fit, _season_bonus, _name, crop in ranked[:max(0, top_n)]]
