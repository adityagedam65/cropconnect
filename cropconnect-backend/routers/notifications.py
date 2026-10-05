"""Authenticated WhatsApp reporting controls."""
from fastapi import APIRouter, Depends, HTTPException

from services.auth_service import owner_profile_context
from services.deps import get_current_user
from services.whatsapp_service import WhatsAppNotConfigured, send_sensor_report, status

router = APIRouter()


@router.get("/api/notifications/whatsapp/status")
def whatsapp_status(_user: tuple[int, str] = Depends(get_current_user)):
    return {"ok": True, **status()}


@router.post("/api/notifications/whatsapp/test")
def send_whatsapp_test(current_user: tuple[int, str] = Depends(get_current_user)):
    profile = owner_profile_context(current_user[0])
    device_id = str(profile.get("sensorDeviceId") or "").strip()
    if not device_id:
        raise HTTPException(status_code=400, detail="No sensor device is configured for this account")
    try:
        return send_sensor_report(device_id)
    except WhatsAppNotConfigured as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=502, detail="WhatsApp provider rejected the report; check the delivery log.") from exc
