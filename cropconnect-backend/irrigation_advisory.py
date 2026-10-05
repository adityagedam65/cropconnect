"""Pure, deterministic irrigation advice from soil moisture and rainfall context."""


LOW_MOISTURE_THRESHOLD = 30
HIGH_MOISTURE_THRESHOLD = 80
RAIN_LIKELY_PROBABILITY = 60


def _number(value: float | None) -> str:
    """Format a supplied measurement without converting missing data to zero."""
    return f"{float(value):g}" if value is not None else "unavailable"


def evaluate_irrigation_advice(
    soil_moisture: float | None,
    rain_probability_today: float | None,
    rainfall_7day_mm: float | None,
) -> dict:
    """Return deterministic irrigation advice without I/O or AI-generated reasoning."""
    advice = {
        "soil_moisture": soil_moisture,
        "rain_probability_today": rain_probability_today,
        "rainfall_7day_mm": rainfall_7day_mm,
    }

    if soil_moisture is None:
        return {
            **advice,
            "action": "insufficient_data",
            "reason": "Soil moisture is unavailable, so irrigation advice cannot be calculated.",
        }

    soil_moisture = float(soil_moisture)
    if soil_moisture >= HIGH_MOISTURE_THRESHOLD:
        return {
            **advice,
            "action": "hold",
            "reason": (
                f"Soil moisture is {_number(soil_moisture)}%, at or above the "
                f"{HIGH_MOISTURE_THRESHOLD}% threshold, so irrigation could increase waterlogging risk."
            ),
        }

    rain_is_likely = (
        rain_probability_today is not None
        and float(rain_probability_today) >= RAIN_LIKELY_PROBABILITY
    )
    if soil_moisture < LOW_MOISTURE_THRESHOLD:
        if rain_is_likely:
            return {
                **advice,
                "action": "delay",
                "reason": (
                    f"Soil moisture is {_number(soil_moisture)}%, below the "
                    f"{LOW_MOISTURE_THRESHOLD}% threshold, but rain is {_number(rain_probability_today)}% likely today; wait and recheck after rain."
                ),
            }
        rain_reason = (
            f"Rain probability is {_number(rain_probability_today)}% today."
            if rain_probability_today is not None
            else "Today's rain probability is unavailable."
        )
        return {
            **advice,
            "action": "irrigate",
            "reason": (
                f"Soil moisture is {_number(soil_moisture)}%, below the "
                f"{LOW_MOISTURE_THRESHOLD}% threshold. {rain_reason}"
            ),
        }

    if rain_is_likely:
        return {
            **advice,
            "action": "delay",
            "reason": (
                f"Soil moisture is {_number(soil_moisture)}%, in the adequate "
                f"{LOW_MOISTURE_THRESHOLD}%–{HIGH_MOISTURE_THRESHOLD}% range, and rain is "
                f"{_number(rain_probability_today)}% likely today; delay irrigation and recheck after rain."
            ),
        }

    rain_reason = (
        f"Rain probability is {_number(rain_probability_today)}% today."
        if rain_probability_today is not None
        else "Today's rain probability is unavailable."
    )
    return {
        **advice,
        "action": "monitor",
        "reason": (
            f"Soil moisture is {_number(soil_moisture)}%, within the adequate "
            f"{LOW_MOISTURE_THRESHOLD}%–{HIGH_MOISTURE_THRESHOLD}% range. {rain_reason}"
        ),
    }


def summarize_advice(advice: dict) -> str:
    """Return a fixed farmer-facing summary for an advisory action."""
    summaries = {
        "irrigate": "Irrigation is recommended now.",
        "delay": "Delay irrigation and recheck after the expected rain.",
        "hold": "Hold off on irrigation — soil is already very wet.",
        "monitor": "No irrigation action needed right now — keep monitoring.",
        "insufficient_data": "Not enough sensor data to give irrigation advice yet.",
    }
    return summaries.get(advice.get("action"), "Not enough sensor data to give irrigation advice yet.")
