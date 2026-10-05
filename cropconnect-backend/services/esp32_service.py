# ESP32 device-key and API-key validation helpers.
import hashlib
import hmac
import secrets
from datetime import datetime, timezone
from typing import Any

from fastapi import HTTPException

from config import settings
from db.repositories import active_device_key, ensure_device, insert_device_key, revoke_device_keys
from logging_config import configure_logging
from security_crypto import decrypt_text, encrypt_text
from services.auth_service import decimal_to_float

logger = configure_logging()


def raise_public_error(status_code: int, detail: str, context: str, exc: Exception) -> None:
    logger.exception("%s: %s", context, exc)
    raise HTTPException(status_code=status_code, detail=detail) from exc


def generate_esp32_api_key() -> str:
    return f"cc_esp32_{secrets.token_urlsafe(32)}"


def esp32_key_hash(api_key: str) -> str:
    return hashlib.sha256(api_key.encode("utf-8")).hexdigest()


def active_esp32_device_key(device_id: str, create_if_missing: bool = False) -> str:
    device = str(device_id or "").strip()
    if not device:
        return ""

    try:
        row = active_device_key(device)
        if row:
            return decrypt_text(row["encrypted_key"]) or ""
        if not create_if_missing:
            return ""
        api_key = generate_esp32_api_key()
        ensure_device(device)
        insert_device_key({"device_id": device, "key_hash": esp32_key_hash(api_key), "encrypted_key": encrypt_text(api_key), "status": "active"})
        return api_key
    except HTTPException:
        raise
    except Exception as exc:
        raise_public_error(503, "Could not load ESP32 device key", "ESP32 device key lookup failed", exc)


def esp32_device_key_summary(device_id: str) -> dict[str, Any]:
    device = str(device_id or "").strip()
    if not device:
        return {"has_active_key": False}

    try:
        row = active_device_key(device)
    except Exception as exc:
        raise_public_error(503, "Could not load ESP32 device key metadata", "ESP32 device key metadata lookup failed", exc)

    if not row:
        return {"has_active_key": False}
    return {
        "has_active_key": True,
        "created_at": decimal_to_float(row.get("created_at")),
        "last_used_at": decimal_to_float(row.get("last_used_at")),
    }


def rotate_esp32_device_key(device_id: str) -> str:
    device = str(device_id or "").strip()
    if not device:
        return ""

    api_key = generate_esp32_api_key()
    try:
        ensure_device(device)
        revoke_device_keys(device)
        insert_device_key({"device_id": device, "key_hash": esp32_key_hash(api_key), "encrypted_key": encrypt_text(api_key), "status": "active"})
        return api_key
    except Exception as exc:
        raise_public_error(503, "Could not rotate ESP32 device key", "ESP32 device key rotation failed", exc)


def stored_esp32_key_matches(supplied_key: str, device_id: str) -> bool:
    device = str(device_id or "").strip()
    if not supplied_key or not device:
        return False

    supplied_hash = esp32_key_hash(supplied_key)
    try:
        from db.mongodb import get_database

        rows = get_database().esp32_device_keys.find(
            {"device_id": device, "status": "active"}, {"id": 1, "key_hash": 1}
        ).sort("id", -1).limit(5)
        for row in rows:
            if hmac.compare_digest(str(row.get("key_hash") or ""), supplied_hash):
                get_database().esp32_device_keys.update_one({"id": row["id"]}, {"$set": {"last_used_at": datetime.now(timezone.utc)}})
                return True
        return False
    except Exception as exc:
        raise_public_error(503, "Could not validate ESP32 device key", "ESP32 device key validation failed", exc)


def supplied_esp32_key(x_api_key: str | None, api_key: str | None = None) -> str:
    return str(x_api_key or api_key or "").strip()


def require_esp32_get_write_enabled() -> None:
    if not settings.esp32_get_write_enabled:
        raise HTTPException(status_code=405, detail="ESP32 GET write endpoints are disabled; use POST")


def check_api_key(x_api_key: str | None, api_key: str | None = None, device_id: str | None = None) -> None:
    if api_key and not settings.query_api_key_enabled:
        raise HTTPException(status_code=401, detail="Query-string ESP32 API keys are disabled")
    supplied_key = supplied_esp32_key(x_api_key, api_key)
    if not supplied_key:
        raise HTTPException(status_code=401, detail="ESP32 API key is required")

    device = str(device_id or "").strip()
    if device:
        if stored_esp32_key_matches(supplied_key, device):
            return
        if (
            settings.allow_global_esp32_api_key
            and settings.esp32_api_key
            and hmac.compare_digest(supplied_key, settings.esp32_api_key)
        ):
            return
        raise HTTPException(status_code=401, detail="Invalid ESP32 API key for this device")

    if not settings.esp32_api_key:
        raise HTTPException(status_code=503, detail="ESP32_API_KEY is not configured")
    if not hmac.compare_digest(supplied_key, settings.esp32_api_key):
        raise HTTPException(status_code=401, detail="Invalid ESP32 API key")


def api_key_matches(x_api_key: str | None = None, api_key: str | None = None, device_id: str | None = None) -> bool:
    supplied_key = supplied_esp32_key(x_api_key, api_key)
    if not supplied_key:
        return False
    device = str(device_id or "").strip()
    if device:
        db_key_ok = stored_esp32_key_matches(supplied_key, device)
        return bool(
            db_key_ok
            or (
                settings.allow_global_esp32_api_key
                and settings.esp32_api_key
                and hmac.compare_digest(supplied_key, settings.esp32_api_key)
            )
        )
    return bool(settings.esp32_api_key and hmac.compare_digest(supplied_key, settings.esp32_api_key))
