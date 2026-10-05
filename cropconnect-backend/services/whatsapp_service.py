"""Official WhatsApp Cloud API reporting for the latest ESP32 reading."""
from __future__ import annotations

import asyncio
import os
import socket
from datetime import datetime, timedelta, timezone
from typing import Any

import httpx
from fastapi import HTTPException
from pymongo.errors import DuplicateKeyError

from config import settings
from db.mongodb import get_database
from db.repositories import list_current_pump_states_by_device
from services.sensor_service import latest_sensor_context

LEASE_NAME = "whatsapp-sensor-report"
_WORKER_ID = f"{socket.gethostname()}:{os.getpid()}"


class WhatsAppNotConfigured(RuntimeError):
    pass


def _now() -> datetime:
    return datetime.now(timezone.utc)


def configured() -> bool:
    return bool(settings.whatsapp_enabled and settings.whatsapp_access_token and settings.whatsapp_phone_number_id and settings.whatsapp_template_name)


def configuration_message() -> str:
    if not settings.whatsapp_enabled:
        return "WhatsApp reporting is disabled. Set WHATSAPP_ENABLED=true to enable it."
    missing = [name for name, value in (("WHATSAPP_ACCESS_TOKEN", settings.whatsapp_access_token), ("WHATSAPP_PHONE_NUMBER_ID", settings.whatsapp_phone_number_id), ("WHATSAPP_TEMPLATE_NAME", settings.whatsapp_template_name)) if not value]
    return "WhatsApp is not configured: " + ", ".join(missing) if missing else "WhatsApp is configured."


def _value(value: Any, unit: str = "") -> str:
    return "N/A" if value is None else f"{value}{unit}"


def format_sensor_report(device_id: str) -> str:
    context = latest_sensor_context(device_id)
    if context.get("source") != "esp32":
        raise ValueError(context.get("message") or "No current ESP32 sensor reading is available.")
    data = context["sensor_data"]
    pumps = list_current_pump_states_by_device(device_id)
    irrigation = "N/A" if not pumps else ("ON" if any(bool(item.get("on")) for item in pumps) else "OFF")
    recorded_at = context.get("recorded_at") or "N/A"
    return "\n".join((
        "CropConnect Farm Update", f"Time: {recorded_at}",
        f"Temperature: {_value(data.get('temperature'), ' °C')}",
        f"Soil Moisture: {_value(data.get('soil_moisture'), ' %')}",
        f"Humidity: {_value(data.get('humidity'), ' %')}",
        f"Soil pH: {_value(data.get('ph'))}",
        f"Nitrogen: {_value(data.get('nitrogen'), ' mg/kg')}",
        f"Phosphorus: {_value(data.get('phosphorus'), ' mg/kg')}",
        f"Potassium: {_value(data.get('potassium'), ' mg/kg')}",
        f"Irrigation: {irrigation}",
    ))


def _log(device_id: str, status: str, *, message_id: str | None = None, error: str | None = None) -> None:
    get_database().whatsapp_delivery_logs.insert_one({"device_id": device_id, "recipient": settings.whatsapp_recipient_number, "status": status, "provider_message_id": message_id, "error": error, "created_at": _now()})


def send_sensor_report(device_id: str) -> dict[str, Any]:
    if not configured():
        raise WhatsAppNotConfigured(configuration_message())
    message = format_sensor_report(device_id)
    url = f"https://graph.facebook.com/{settings.whatsapp_api_version}/{settings.whatsapp_phone_number_id}/messages"
    payload = {"messaging_product": "whatsapp", "to": settings.whatsapp_recipient_number, "type": "template", "template": {"name": settings.whatsapp_template_name, "language": {"code": settings.whatsapp_template_language}, "components": [{"type": "body", "parameters": [{"type": "text", "text": message}]}]}}
    try:
        response = httpx.post(url, headers={"Authorization": f"Bearer {settings.whatsapp_access_token}"}, json=payload, timeout=20)
        body = response.json()
        response.raise_for_status()
        message_id = str((body.get("messages") or [{}])[0].get("id") or "")
        _log(device_id, "sent", message_id=message_id)
        return {"success": True, "message_id": message_id, "device_id": device_id}
    except Exception as exc:
        _log(device_id, "failed", error=str(exc)[:1000])
        raise


def _acquire_lease() -> bool:
    now = _now()
    lease = {"owner": _WORKER_ID, "expires_at": now + timedelta(seconds=max(settings.whatsapp_interval_seconds - 10, 30)), "updated_at": now}
    collection = get_database().scheduler_leases
    if not collection.find_one({"_id": LEASE_NAME}, {"_id": 1}):
        try:
            collection.insert_one({"_id": LEASE_NAME, **lease})
            return True
        except DuplicateKeyError:
            return False
    result = collection.update_one(
        {"_id": LEASE_NAME, "$or": [{"expires_at": {"$lte": now}}, {"owner": _WORKER_ID}]},
        {"$set": lease},
    )
    return result.modified_count == 1


async def run_whatsapp_scheduler(stop: asyncio.Event) -> None:
    """One MongoDB-leased sender per deployment; failures never stop FastAPI."""
    while not stop.is_set():
        try:
            device_id = settings.whatsapp_device_id or settings.public_landing_sensor_device_id
            if configured() and device_id and _acquire_lease():
                await asyncio.to_thread(send_sensor_report, device_id)
        except Exception:
            # Delivery failures are persisted by send_sensor_report; configuration
            # errors are intentionally non-fatal to the API process.
            pass
        try:
            await asyncio.wait_for(stop.wait(), timeout=max(settings.whatsapp_interval_seconds, 60))
        except asyncio.TimeoutError:
            continue


def status() -> dict[str, Any]:
    latest = get_database().whatsapp_delivery_logs.find_one({}, {"_id": False}, sort=[("created_at", -1)])
    return {"configured": configured(), "message": configuration_message(), "latest_delivery": latest}
