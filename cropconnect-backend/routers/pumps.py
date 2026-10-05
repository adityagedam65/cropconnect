from datetime import datetime, timedelta, timezone
from typing import Any
from fastapi import APIRouter, Cookie, Header, HTTPException, Query, Request
from fastapi.responses import PlainTextResponse
from config import settings
from db.repositories import list_current_pump_states, list_current_pump_states_by_device, list_pump_timers, list_pump_timers_by_device, relay_states, replace_pump_timers, save_pump_state, save_relay_states
from models import PumpStateSaveIn, PumpTimersSaveIn, RelayStatusIn
from pump_control import PumpStateIn, relay_command_text
from services.auth_service import decimal_to_float, owner_profile_context, require_auth_owner
from services.esp32_service import check_api_key, require_esp32_get_write_enabled

AUTH_COOKIE_NAME = "cropconnect_auth"
FARM_TIMER_TIMEZONE = timezone(timedelta(minutes=settings.farm_timer_utc_offset_minutes))
router = APIRouter()

def pump_id_to_relay_number(pump_id: Any) -> int:
    return int("".join(ch for ch in str(pump_id) if ch.isdigit()) or 0)

def parse_relay_states(values: dict[str, Any]) -> dict[int, bool]:
    result = {}
    for key, value in values.items():
        key = str(key).lower().replace("relay", "").lstrip("r")
        try: number = int(key)
        except ValueError: continue
        result[number] = str(value).lower() in {"1", "true", "on", "yes", "high"}
    return result

def timer_row_is_active(row: dict[str, Any], now: datetime | None = None) -> bool:
    try: start_hour, start_minute = map(int, str(row.get("start_time", "")).split(":")[:2]); duration = int(row.get("duration_minutes") or 0)
    except (TypeError, ValueError): return False
    now = now or datetime.now(FARM_TIMER_TIMEZONE); current_day = (now.weekday() + 1) % 7; start = start_hour * 60 + start_minute; current = now.hour * 60 + now.minute
    return any(0 <= ((current_day - int(day)) % 7) * 1440 + current - start < duration for day in (row.get("days") or range(7)))

def active_timer_pump_ids(device_id: str) -> set[str]:
    return {str(row.get("pump_id")) for row in list_pump_timers_by_device(device_id) if timer_row_is_active(row)}

def desired_states(device_id: str) -> dict[int, bool]:
    states = {number: False for number in range(1, 9)}
    for row in list_current_pump_states_by_device(device_id):
        number = pump_id_to_relay_number(row.get("pump_id"))
        if 1 <= number <= 8: states[number] = bool(row.get("is_on"))
    for pump_id in active_timer_pump_ids(device_id):
        number = pump_id_to_relay_number(pump_id)
        if 1 <= number <= 8: states[number] = True
    return states

def relay_status_payload(device_id: str) -> dict[str, Any]:
    applied = {number: None for number in range(1, 9)}; updated_at = None
    for row in relay_states(device_id):
        number = int(row.get("relay_number") or 0)
        if 1 <= number <= 8:
            applied[number] = bool(row.get("is_on")); updated_at = max(updated_at, row.get("reported_at")) if updated_at else row.get("reported_at")
    return {"desired": {str(k): v for k, v in desired_states(device_id).items()}, "applied": {str(k): v for k, v in applied.items()}, "updated_at": decimal_to_float(updated_at)}

def owner_device(owner_id: int) -> str:
    device_id = str(owner_profile_context(owner_id).get("sensorDeviceId") or "").strip()
    if not device_id: raise HTTPException(status_code=400, detail="No sensor device is configured for this account")
    return device_id

@router.get("/api/esp32/relay-command", response_class=PlainTextResponse)
def esp32_relay_command(x_api_key: str | None = Header(default=None), api_key: str | None = Query(default=None), device_id: str = Query(default="")):
    if not device_id.strip(): raise HTTPException(status_code=400, detail="device_id is required")
    check_api_key(x_api_key, api_key, device_id); return relay_command_text(desired_states(device_id))

@router.get("/esp32/relay-command", response_class=PlainTextResponse)
def esp32_relay_command_short(x_api_key: str | None = Header(default=None), api_key: str | None = Query(default=None), device_id: str = Query(default="")): return esp32_relay_command(x_api_key, api_key, device_id)

@router.post("/api/esp32/relay-status")
def esp32_relay_status(payload: RelayStatusIn, x_api_key: str | None = Header(default=None), api_key: str | None = Query(default=None)):
    check_api_key(x_api_key, api_key, payload.device_id); save_relay_states(payload.device_id, parse_relay_states(payload.relays)); return {"ok": True, "device_id": payload.device_id, "status": relay_status_payload(payload.device_id)}

@router.get("/api/esp32/relay-status")
def get_esp32_relay_status(x_api_key: str | None = Header(default=None), api_key: str | None = Query(default=None), device_id: str = Query(default="")):
    check_api_key(x_api_key, api_key, device_id); return {"ok": True, "status": relay_status_payload(device_id)}

@router.get("/api/esp32/relay-status/update")
def esp32_relay_status_update(request: Request, x_api_key: str | None = Header(default=None), api_key: str | None = Query(default=None)):
    require_esp32_get_write_enabled(); device_id = str(request.query_params.get("device_id") or "").strip(); check_api_key(x_api_key, api_key, device_id); save_relay_states(device_id, parse_relay_states(dict(request.query_params))); return {"ok": True, "status": relay_status_payload(device_id)}

@router.post("/api/pump/state")
def set_pump_state(payload: PumpStateIn, authorization: str | None = Header(default=None), auth_cookie: str | None = Cookie(default=None, alias=AUTH_COOKIE_NAME)):
    owner_id, owner_email = require_auth_owner(authorization, auth_cookie); device_id = owner_device(owner_id)
    if payload.device_id and payload.device_id != device_id: raise HTTPException(status_code=403, detail="Pump device does not belong to this account")
    message = "Pump command queued for SIM800L."
    row = save_pump_state({"user_id": owner_id, "email": owner_email, "device_id": device_id, "pump_id": payload.pump_id, "is_on": bool(payload.on), "runtime_minutes": payload.runtime or 0, "schedule": payload.schedule or {}, "sent_to_esp32": False, "message": message})
    return {"ok": True, "device_id": device_id, "pump_id": payload.pump_id, "is_on": bool(row["is_on"]), "state": "on" if row["is_on"] else "off", "sent_to_esp32": False, "queued_for_sim800l": True, "message": message, "esp32": None, "updated_at": decimal_to_float(row.get("created_at"))}

@router.post("/api/farm/pump-state")
def save_pump_state_endpoint(payload: PumpStateSaveIn, authorization: str | None = Header(default=None), auth_cookie: str | None = Cookie(default=None, alias=AUTH_COOKIE_NAME)):
    owner_id, owner_email = require_auth_owner(authorization, auth_cookie); device_id = owner_device(owner_id)
    save_pump_state({"user_id": owner_id, "email": owner_email, "device_id": device_id, "pump_id": payload.pump_id, "is_on": bool(payload.on), "runtime_minutes": payload.runtime or 0, "schedule": payload.schedule or {}, "sent_to_esp32": bool(payload.sent_to_esp32), "message": payload.message or ""}); return {"ok": True, "device_id": device_id}

@router.get("/api/farm/pump-states")
def get_pump_states(authorization: str | None = Header(default=None), auth_cookie: str | None = Cookie(default=None, alias=AUTH_COOKIE_NAME)):
    owner_id, _ = require_auth_owner(authorization, auth_cookie); device_id = owner_device(owner_id)
    return {"ok": True, "items": [{"pump_id": row.get("pump_id"), "on": bool(row.get("is_on")), "desired_on": bool(row.get("is_on")), "applied_on": None, "hardware_confirmed": False, "runtime": int(row.get("runtime_minutes") or 0), "schedule": row.get("schedule") or {}, "sent_to_esp32": bool(row.get("sent_to_esp32")), "message": row.get("message") or "", "timer_active": False, "applied_updated_at": None, "updated_at": decimal_to_float(row.get("updated_at"))} for row in list_current_pump_states(owner_id, device_id)]}

@router.post("/api/farm/timers")
def save_pump_timers_endpoint(payload: PumpTimersSaveIn, authorization: str | None = Header(default=None), auth_cookie: str | None = Cookie(default=None, alias=AUTH_COOKIE_NAME)):
    owner_id, owner_email = require_auth_owner(authorization, auth_cookie); device_id = owner_device(owner_id); rows = []
    for pump_id, timers in payload.timers.items():
        for timer in timers:
            duration = int(timer.get("duration") or 0)
            if duration < 1 or duration > 480 or not timer.get("startTime"): raise HTTPException(status_code=400, detail="Timer values are invalid")
            rows.append({"pump_id": str(pump_id), "timer_key": str(timer.get("id") or f"{pump_id}-{timer['startTime']}"), "start_time": timer["startTime"], "duration_minutes": duration, "days": timer.get("days") or []})
    replace_pump_timers(owner_id, owner_email, device_id, rows); return {"ok": True}

@router.get("/api/farm/timers")
def get_pump_timers(authorization: str | None = Header(default=None), auth_cookie: str | None = Cookie(default=None, alias=AUTH_COOKIE_NAME)):
    owner_id, _ = require_auth_owner(authorization, auth_cookie); device_id = owner_device(owner_id); timers: dict[str, list[dict[str, Any]]] = {}
    for row in list_pump_timers(owner_id, device_id): timers.setdefault(row["pump_id"], []).append({"id": row["timer_key"], "startTime": row["start_time"], "duration": int(row["duration_minutes"]), "days": row.get("days") or []})
    return {"ok": True, "timers": timers}
