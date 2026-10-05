# Lightweight weather-context helper used by the predictive agronomy layer.
#
# This intentionally duplicates the small geocode-then-forecast call already
# used by routers/weather.py rather than importing from it, because that
# router function is wired to a Request object and a public rate limiter.
# This helper has no HTTP-route concerns: it is called internally, once per
# crop-recommendation request, and must degrade to None on any failure
# rather than raising, so a weather outage never blocks a crop score.
import urllib.parse
from typing import Any

from http_client import request_json
from logging_config import configure_logging

logger = configure_logging()


def log_backend_error(context: str, exc: Exception) -> None:
    logger.exception("%s: %s", context, exc)


def geocode_location(location: str) -> dict[str, Any] | None:
    """Resolve a free-text farm location to lat/lon using Open-Meteo's geocoder."""
    if not location:
        return None
    try:
        geo_url = "https://geocoding-api.open-meteo.com/v1/search?" + urllib.parse.urlencode(
            {"name": location, "count": 1, "language": "en", "format": "json"}
        )
        geo = request_json(geo_url)
        result = (geo.get("results") or [None])[0]
        if not result and "," in location:
            city_name = location.split(",", 1)[0].strip()
            geo_url = "https://geocoding-api.open-meteo.com/v1/search?" + urllib.parse.urlencode(
                {"name": city_name, "count": 1, "language": "en", "format": "json"}
            )
            geo = request_json(geo_url)
            result = (geo.get("results") or [None])[0]
        return result
    except Exception as exc:
        log_backend_error("Geocoding failed for crop weather context", exc)
        return None


def get_weather_context(location: str) -> dict[str, Any]:
    """Return a small weather summary for crop scoring: 7-day rainfall total (mm)
    and today's rain probability. Never raises; returns an empty/None-valued
    dict on any failure so callers can treat weather as just another
    possibly-missing reading, the same way sensor gaps are handled.
    """
    empty = {
        "rainfall_7day_mm": None,
        "rain_probability_today": None,
        "resolved_location": None,
        "source": "unavailable",
    }
    if not location:
        return empty

    result = geocode_location(location)
    if not result:
        return empty

    try:
        params = {
            "latitude": result["latitude"],
            "longitude": result["longitude"],
            "daily": "precipitation_sum,precipitation_probability_max",
            "forecast_days": 7,
            "timezone": "auto",
        }
        forecast_url = "https://api.open-meteo.com/v1/forecast?" + urllib.parse.urlencode(params)
        data = request_json(forecast_url)
        daily = data.get("daily", {})
        precipitation_sums = [value for value in daily.get("precipitation_sum", []) if value is not None]
        rain_probabilities = daily.get("precipitation_probability_max", [])
        rainfall_7day_mm = round(sum(precipitation_sums), 1) if precipitation_sums else None
        rain_probability_today = rain_probabilities[0] if rain_probabilities else None
        return {
            "rainfall_7day_mm": rainfall_7day_mm,
            "rain_probability_today": rain_probability_today,
            "resolved_location": result.get("name"),
            "source": "open-meteo",
        }
    except Exception as exc:
        log_backend_error("Weather forecast lookup failed for crop weather context", exc)
        return empty
