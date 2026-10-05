"""Authenticated, unit-safe fertilizer status endpoint."""

from fastapi import APIRouter, Cookie, Header, HTTPException, Request

from fertilizer_advisory import evaluate_fertilizer_advice
from services.auth_service import owner_profile_context, require_auth_owner
from services.rate_limit import rate_limit_authenticated_request
from services.sensor_service import latest_sensor_context


AUTH_COOKIE_NAME = "cropconnect_auth"
STORED_NUTRIENT_UNIT = "mg/kg"
EXPECTED_NUTRIENT_UNIT = "kg/ha equivalent"
router = APIRouter()


@router.post("/api/fertilizer/advice")
def fertilizer_advice(
    request: Request,
    authorization: str | None = Header(default=None),
    auth_cookie: str | None = Cookie(default=None, alias=AUTH_COOKIE_NAME),
):
    """Return an explicit unit warning instead of guessing an NPK unit conversion."""
    owner_id, _owner_email = require_auth_owner(authorization, auth_cookie)
    rate_limit_authenticated_request(owner_id, "fertilizer-advice", limit=20, window_seconds=60)
    profile = owner_profile_context(owner_id)
    device_id = str(profile.get("sensorDeviceId") or "").strip()
    if not device_id:
        raise HTTPException(status_code=400, detail="No sensor device is configured for this account")

    sensor_context = latest_sensor_context(device_id)
    # Telemetry records nutrient values in mg/kg. The supplied status bands are
    # kg/ha equivalents, and no validated conversion is available in this repo.
    return {
        "ok": True,
        "source": "unit_guard",
        "unit_status": "unsupported",
        "message": (
            f"Live ESP32 N/P/K readings are stored as {STORED_NUTRIENT_UNIT}, but this advisory's "
            f"Low/Medium/High bands require {EXPECTED_NUTRIENT_UNIT}. No conversion was applied."
        ),
        "advice": evaluate_fertilizer_advice(None, None, None),
        "missingReadings": ["nitrogen", "phosphorus", "potassium"],
        "sensor_context": sensor_context,
    }
