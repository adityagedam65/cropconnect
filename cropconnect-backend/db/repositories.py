"""Native MongoDB repositories for core CropConnect data."""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from db.mongodb import get_database
from pymongo import ReturnDocument


def _now() -> datetime:
    return datetime.now(timezone.utc)


def next_id(name: str) -> int:
    result = get_database().counters.find_one_and_update(
        {"_id": name}, {"$inc": {"value": 1}}, upsert=True, return_document=ReturnDocument.AFTER
    )
    return int(result["value"])


def create_user(document: dict[str, Any]) -> dict[str, Any]:
    document = {"id": next_id("users"), "created_at": _now(), **document}
    get_database().users.insert_one(document)
    return document


def find_user_by_id(user_id: int) -> dict[str, Any] | None:
    return get_database().users.find_one({"id": int(user_id)}, {"_id": False})


def find_user_by_email(email: str) -> dict[str, Any] | None:
    return get_database().users.find_one({"email": email}, {"_id": False})


def update_user(user_id: int, updates: dict[str, Any]) -> dict[str, Any] | None:
    get_database().users.update_one({"id": int(user_id)}, {"$set": updates})
    return find_user_by_id(user_id)


def ensure_device(device_id: str, **fields: Any) -> None:
    get_database().devices.update_one(
        {"device_id": device_id},
        {"$setOnInsert": {"device_id": device_id, "created_at": _now()}, "$set": fields},
        upsert=True,
    )


def active_device_key(device_id: str) -> dict[str, Any] | None:
    return get_database().esp32_device_keys.find_one(
        {"device_id": device_id, "status": "active"}, {"_id": False}, sort=[("id", -1)]
    )


def insert_device_key(document: dict[str, Any]) -> None:
    get_database().esp32_device_keys.insert_one({"id": next_id("esp32_device_keys"), "created_at": _now(), **document})


def revoke_device_keys(device_id: str) -> None:
    get_database().esp32_device_keys.update_many(
        {"device_id": device_id, "status": "active"},
        {"$set": {"status": "revoked", "revoked_at": _now(), "rotated_at": _now()}},
    )


def insert_sensor_reading(document: dict[str, Any]) -> int:
    reading_id = next_id("sensor_readings")
    get_database().sensor_readings.insert_one({"id": reading_id, "recorded_at": _now(), **document})
    return reading_id


def latest_sensor_reading(device_id: str) -> dict[str, Any] | None:
    return get_database().sensor_readings.find_one(
        {"device_id": device_id}, {"_id": False}, sort=[("recorded_at", -1), ("id", -1)]
    )


def list_sensor_readings(device_id: str, limit: int) -> list[dict[str, Any]]:
    return list(
        get_database().sensor_readings.find({"device_id": device_id}, {"_id": False})
        .sort([("recorded_at", -1), ("id", -1)])
        .limit(limit)
    )


def save_token(document: dict[str, Any]) -> dict[str, Any]:
    token = {"id": next_id("tokens"), "created_at": _now(), **document}
    get_database().password_reset_tokens.insert_one(token)
    return token


def find_valid_token(email: str, token_hash: str) -> dict[str, Any] | None:
    return get_database().password_reset_tokens.find_one(
        {"email": email, "token_hash": token_hash, "used_at": None, "expires_at": {"$gt": _now()}},
        {"_id": False}, sort=[("id", -1)],
    )


def use_token(token_id: int) -> None:
    get_database().password_reset_tokens.update_one({"id": int(token_id)}, {"$set": {"used_at": _now()}})


def insert_chat_record(document: dict[str, Any]) -> None:
    get_database().chat_messages.insert_one({"id": next_id("chat_messages"), "created_at": _now(), **document})


def list_chat_records(user_id: int, limit: int) -> list[dict[str, Any]]:
    return list(get_database().chat_messages.find({"user_id": int(user_id)}, {"_id": False}).sort("id", -1).limit(limit))


def save_pump_state(document: dict[str, Any]) -> dict[str, Any]:
    state = {"id": next_id("pump_states"), "created_at": _now(), **document}
    get_database().pump_states.insert_one(state)
    get_database().current_pump_state.update_one(
        {"user_id": document.get("user_id"), "pump_id": document["pump_id"]},
        {"$set": {**document, "updated_at": _now()}, "$setOnInsert": {"id": state["id"]}},
        upsert=True,
    )
    return state


def list_current_pump_states(user_id: int, device_id: str) -> list[dict[str, Any]]:
    return list(get_database().current_pump_state.find({"user_id": int(user_id), "device_id": device_id}, {"_id": False}).sort("pump_id", 1))


def replace_pump_timers(user_id: int, email: str, device_id: str, timers: list[dict[str, Any]]) -> None:
    collection = get_database().pump_timers
    collection.delete_many({"user_id": int(user_id), "$or": [{"device_id": device_id}, {"device_id": None}]})
    if timers:
        collection.insert_many([{"id": next_id("pump_timers"), "user_id": int(user_id), "email": email, "device_id": device_id, "active": True, "created_at": _now(), "updated_at": _now(), **timer} for timer in timers])


def list_pump_timers(user_id: int, device_id: str) -> list[dict[str, Any]]:
    return list(get_database().pump_timers.find({"user_id": int(user_id), "active": True, "$or": [{"device_id": device_id}, {"device_id": None}]}, {"_id": False}).sort([("pump_id", 1), ("start_time", 1)]))


def list_pump_timers_by_device(device_id: str) -> list[dict[str, Any]]:
    return list(get_database().pump_timers.find({"device_id": device_id, "active": True}, {"_id": False}).sort([("pump_id", 1), ("start_time", 1)]))


def list_current_pump_states_by_device(device_id: str) -> list[dict[str, Any]]:
    return list(get_database().current_pump_state.find({"device_id": device_id}, {"_id": False}).sort("pump_id", 1))


def save_relay_states(device_id: str, states: dict[int, bool]) -> None:
    now = _now()
    collection = get_database().relay_statuses
    for relay_number, is_on in states.items():
        collection.update_one({"device_id": device_id, "relay_number": int(relay_number)}, {"$set": {"is_on": bool(is_on), "reported_at": now}}, upsert=True)


def relay_states(device_id: str) -> list[dict[str, Any]]:
    return list(get_database().relay_statuses.find({"device_id": device_id}, {"_id": False}))