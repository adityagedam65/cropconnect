"""Deterministic sensor-condition alerts, not crop disease diagnoses."""

from typing import Any

from irrigation_advisory import HIGH_MOISTURE_THRESHOLD, LOW_MOISTURE_THRESHOLD


GENERAL_PH_MIN = 5.5
GENERAL_PH_MAX = 7.5
HEAT_STRESS_THRESHOLD = 38.0
FUNGAL_RISK_HUMIDITY_THRESHOLD = 85.0
FUNGAL_RISK_TEMP_MIN = 20.0
FUNGAL_RISK_TEMP_MAX = 30.0


def evaluate_stress_conditions(
    soil_moisture: float | None, ph: float | None, temperature: float | None, humidity: float | None,
) -> dict[str, Any]:
    """Return only sensor-backed condition flags; missing readings imply no conclusion."""
    conditions: list[dict[str, str]] = []
    if soil_moisture is not None:
        value = float(soil_moisture)
        if value < LOW_MOISTURE_THRESHOLD:
            conditions.append({"type": "water_stress", "severity": "high", "message": f"Soil moisture is {value:g}%, below the {LOW_MOISTURE_THRESHOLD}% dry-stress threshold."})
        elif value >= HIGH_MOISTURE_THRESHOLD:
            conditions.append({"type": "water_stress", "severity": "high", "message": f"Soil moisture is {value:g}%, at or above the {HIGH_MOISTURE_THRESHOLD}% waterlogging-risk threshold."})
    if ph is not None:
        value = float(ph)
        if value < GENERAL_PH_MIN or value > GENERAL_PH_MAX:
            conditions.append({"type": "ph_stress", "severity": "medium", "message": f"Soil pH is {value:g}, outside the general crop tolerance band of {GENERAL_PH_MIN:g}-{GENERAL_PH_MAX:g}."})
    if temperature is not None and float(temperature) > HEAT_STRESS_THRESHOLD:
        conditions.append({"type": "heat_stress", "severity": "high", "message": f"Temperature is {float(temperature):g}°C, above the {HEAT_STRESS_THRESHOLD:g}°C heat-stress threshold."})
    if humidity is not None and temperature is not None:
        humidity_value, temperature_value = float(humidity), float(temperature)
        if humidity_value > FUNGAL_RISK_HUMIDITY_THRESHOLD and FUNGAL_RISK_TEMP_MIN <= temperature_value <= FUNGAL_RISK_TEMP_MAX:
            conditions.append({"type": "fungal_risk_indicator", "severity": "medium", "message": f"Humidity is {humidity_value:g}% with temperature {temperature_value:g}°C; these conditions can favor fungal disease development, so monitor crops closely."})
    return {"conditions": conditions, "missingReadings": [key for key, value in {"soil_moisture": soil_moisture, "ph": ph, "temperature": temperature, "humidity": humidity}.items() if value is None]}
