import json
from typing import Any

from fastapi import APIRouter, Cookie, Header, HTTPException, Query

from db.repositories import list_chat_records
from logging_config import configure_logging
from models import DashboardSnapshotIn
from services.auth_service import decimal_to_float, require_auth_owner

AUTH_COOKIE_NAME = "cropconnect_auth"
router = APIRouter()
logger = configure_logging()


def raise_public_error(status_code: int, detail: str, context: str, exc: Exception) -> None:
    logger.exception("%s: %s", context, exc)
    raise HTTPException(status_code=status_code, detail=detail) from exc


def json_text(value: Any) -> str:
    return json.dumps(value if value is not None else {}, ensure_ascii=False)


def parse_json_column(value: Any, fallback: Any) -> Any:
    if value in (None, ""):
        return fallback
    if isinstance(value, (dict, list)):
        return value
    try:
        return json.loads(value)
    except Exception as exc:
        logger.exception("parse_json_column failed: %s", exc)
        return fallback


@router.get("/api/farm/chat-history")
def get_chat_history(
    user_id: int | None = Query(default=None, ge=1),
    email: str | None = Query(default=None, max_length=255),
    limit: int = Query(default=50, ge=1, le=200),
    authorization: str | None = Header(default=None),
    auth_cookie: str | None = Cookie(default=None, alias=AUTH_COOKIE_NAME),
):
    owner_id, _owner_email = require_auth_owner(authorization, auth_cookie)
    rows = list_chat_records(owner_id, limit)

    return {
        "ok": True,
        "items": [
            {
                "id": row["id"],
                "type": "bot" if row["message_type"] == "bot" else "user",
                "text": row["text"],
                "relatedToPlantOrSoil": row.get("related_to_plant_or_soil"),
                "createdAt": decimal_to_float(row.get("created_at")),
            }
            for row in reversed(rows)
        ],
    }


@router.post("/api/farm/snapshot")
def save_dashboard_snapshot(
    payload: DashboardSnapshotIn,
    authorization: str | None = Header(default=None),
    auth_cookie: str | None = Cookie(default=None, alias=AUTH_COOKIE_NAME),
):
    require_auth_owner(authorization, auth_cookie)
    return {"ok": True, "saved": False, "message": "Dashboard snapshots are no longer written automatically"}


@router.get("/api/farm/snapshot/latest")
def get_latest_dashboard_snapshot(
    user_id: int | None = Query(default=None, ge=1),
    email: str | None = Query(default=None, max_length=255),
    authorization: str | None = Header(default=None),
    auth_cookie: str | None = Cookie(default=None, alias=AUTH_COOKIE_NAME),
):
    require_auth_owner(authorization, auth_cookie)
    return {"ok": True, "snapshot": None}
