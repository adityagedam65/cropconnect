"""ML crop ranking with a post-model live-soil-moisture adjustment."""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

import joblib
import pandas as pd

from crop_knowledge import CROP_DATABASE


logger = logging.getLogger(__name__)
FEATURES = ["N", "P", "K", "temperature", "humidity", "ph"]
SENSOR_FEATURES = {
    "N": "nitrogen", "P": "phosphorus", "K": "potassium",
    "temperature": "temperature", "humidity": "humidity", "ph": "ph",
}
MODEL_PATH = Path(__file__).resolve().parent / "data" / "models" / "crop_random_forest.joblib"
_model: Any | None = None


def _load_model() -> Any | None:
    global _model
    if _model is not None:
        return _model
    try:
        _model = joblib.load(MODEL_PATH)
        return _model
    except Exception as exc:  # Model absence or a corrupt artifact must not break requests.
        logger.warning("Crop ML model is unavailable: %s", exc)
        return None


def is_model_available() -> bool:
    """Return whether the model artifact can be loaded, without raising."""
    return _load_model() is not None


def _crop_by_name(name: str) -> dict[str, Any] | None:
    normalized = name.casefold()
    return next((crop for crop in CROP_DATABASE if crop["name"].casefold() == normalized), None)


def _moisture_adjustment(moisture: Any, moisture_range: list[float] | None) -> float:
    if moisture is None or not moisture_range:
        return 1.0
    lower, upper = map(float, moisture_range)
    value = float(moisture)
    if lower <= value <= upper:
        return 1.0
    width = max(upper - lower, 1.0)
    distance = lower - value if value < lower else value - upper
    # Cap the post-model effect at 35%, preserving the learned ranking signal.
    return 1.0 - (0.35 * min(distance / width, 1.0))


# Season, like moisture, was never a training feature for the ML model
# (the public dataset has no season column), so it is fused in the same
# way: as a small post-model bonus rather than silently ignored or fed
# into the model under a false premise. Capped well below the moisture
# adjustment since season is a much softer signal than measured soil
# conditions.
SEASON_MATCH_BONUS = 0.10


def _season_adjustment(requested_season, crop_season):
    if not requested_season or not crop_season:
        return 1.0
    if requested_season.strip().casefold() == crop_season.strip().casefold():
        return 1.0 + SEASON_MATCH_BONUS
    return 1.0


def rank_crops_ml(sensor_data: dict[str, Any], top_n: int = 8, season: str | None = None) -> list[dict[str, Any]]:
    """Rank crops from the trained model, then fuse in live soil moisture."""
    model = _load_model()
    if model is None:
        raise RuntimeError("Crop ML model is unavailable")

    missing = [sensor_key for column, sensor_key in SENSOR_FEATURES.items() if sensor_data.get(sensor_key) is None]
    if missing:
        raise ValueError(f"Missing required ML features: {', '.join(missing)}")

    values = {column: sensor_data[SENSOR_FEATURES[column]] for column in FEATURES}
    probabilities = model.predict_proba(pd.DataFrame([values], columns=FEATURES))[0]
    soil_moisture = sensor_data.get("soil_moisture")
    ranked: list[dict[str, Any]] = []
    for label, probability in zip(model.classes_, probabilities):
        knowledge = _crop_by_name(str(label))
        moisture_range = knowledge.get("moisture_range") if knowledge else None
        adjustment = _moisture_adjustment(soil_moisture, moisture_range)
        season_adjustment = _season_adjustment(season, knowledge.get("season") if knowledge else None)
        adjusted_probability = float(probability) * adjustment * season_adjustment
        fit = int(round(min(adjusted_probability, 1.0) * 100))
        missing_readings = ["soil_moisture"] if soil_moisture is None else []
        status = (
            "Model ranking; soil moisture is unavailable, so no moisture adjustment was applied."
            if soil_moisture is None else
            "Model ranking adjusted for soil moisture." if adjustment < 1 else
            "Model ranking; soil moisture is within this crop's ideal range."
        )
        if season_adjustment > 1.0:
            status += " It matches the requested growing season."
        ranked.append({
            "name": knowledge["name"] if knowledge else str(label).title(),
            "category": knowledge.get("category", "Unknown") if knowledge else "Unknown",
            "season": knowledge.get("season", "Unknown") if knowledge else "Unknown",
            "cropType": knowledge.get("crop_type", "Unknown") if knowledge else "Unknown",
            "fit": f"{fit}%",
            "suitability": "Excellent" if fit >= 85 else "Good" if fit >= 70 else "Fair" if fit >= 50 else "Poor",
            "model_probability": float(probability),
            "moisture_adjustment": adjustment,
            "moisture_range": moisture_range,
            "temp_range": knowledge.get("temp_range") if knowledge else None,
            "humidity_range": knowledge.get("humidity_range") if knowledge else None,
            "ph_range": knowledge.get("ph_range") if knowledge else None,
            "rainfall_range": knowledge.get("rainfall_range") if knowledge else None,
            "description": knowledge.get("description_template", "No local crop profile is available.") if knowledge else "No local crop profile is available.",
            "status_message": status,
            "missingReadings": missing_readings,
            "source": "ml_model",
            "_adjusted_probability": adjusted_probability,
        })
    ranked.sort(key=lambda crop: (-crop["_adjusted_probability"], crop["name"]))
    for crop in ranked:
        crop.pop("_adjusted_probability")
    return ranked[:max(0, top_n)]
