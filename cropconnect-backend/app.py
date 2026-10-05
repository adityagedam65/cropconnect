# FastAPI application creation, middleware, and router registration.
import asyncio
import os
import re
import secrets
import sys
import uuid
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import PlainTextResponse

from config import settings, validate_required_environment
from db.demo_seed import seed_demo_admin
from db.migrations import run_database_migrations
from db.mongodb import get_database, ping_database
from logging_config import request_id_var
from routers import ai as ai_router
from routers import auth as auth_router
from routers import farm as farm_router
from routers import fertilizer as fertilizer_router
from routers import market as market_router
from routers import notifications as notifications_router
from routers import public as public_router
from routers import pumps as pumps_router
from routers import sensors as sensors_router
from routers import weather as weather_router
from routers import vision as vision_router
from security_crypto import require_data_secret
from services.auth_service import AUTH_COOKIE_NAME, CSRF_COOKIE_NAME
from services.whatsapp_service import run_whatsapp_scheduler

PLACEHOLDER_SECRETS = {
    "replace-with-a-long-random-secret",
    "replace-with-a-different-long-random-secret",
}

_sentry_dsn = os.environ.get("SENTRY_DSN", "").strip()
if _sentry_dsn:
    import sentry_sdk
    from sentry_sdk.integrations.fastapi import FastApiIntegration
    from sentry_sdk.integrations.starlette import StarletteIntegration

    _sentry_environment = os.environ.get("RAILWAY_ENVIRONMENT", "development")
    _sentry_is_production = _sentry_environment == "production"
    sentry_sdk.init(
        dsn=_sentry_dsn,
        environment=_sentry_environment,
        traces_sample_rate=0.05 if _sentry_is_production else 1.0,
        profiles_sample_rate=0.01 if _sentry_is_production else 0,
        integrations=[
            StarletteIntegration(),
            FastApiIntegration(),
        ],
        before_send=lambda event, hint: event,
    )

CSRF_HEADER_NAME = "x-csrf-token"
FRONTEND_ORIGINS = [
    origin.strip().rstrip("/")
    for origin in settings.frontend_origins.split(",")
    if origin.strip()
]
if "*" in FRONTEND_ORIGINS:
    raise RuntimeError("FRONTEND_ORIGINS cannot contain '*' when credentialed auth cookies are enabled")
FRONTEND_ORIGIN_REGEX = r"^https://[a-z0-9-]+(?:-[a-z0-9-]+)?\.vercel\.app$"
FRONTEND_ORIGIN_PATTERN = re.compile(FRONTEND_ORIGIN_REGEX)


def is_trusted_frontend_origin(origin: str) -> bool:
    normalized = (origin or "").rstrip("/")
    return normalized in FRONTEND_ORIGINS or bool(FRONTEND_ORIGIN_PATTERN.fullmatch(normalized))

CSRF_EXEMPT_PATHS = {
    "/api/auth/signup",
    "/api/auth/login",
    "/api/auth/password-reset-request",
    "/api/auth/password-reset-confirm",
    "/api/auth/verify-email",
    "/api/enquiries",
    "/api/utils/translate",
    "/api/telemetry/ingest",
    "/data",
}


@asynccontextmanager
async def lifespan(_app: FastAPI):
    whatsapp_stop = asyncio.Event()
    whatsapp_task = None
    try:
        env_problems = validate_required_environment()
        if env_problems:
            # Fail loudly before serving traffic when required production env is unsafe.
            print("FATAL: Invalid production environment:\n- " + "\n- ".join(env_problems), file=sys.stderr)
            sys.exit(1)
        require_data_secret()
        configured_secrets = {
            os.environ.get("CROP_DATA_SECRET_KEY") or settings.crop_data_secret_key,
            os.environ.get("CROP_AUTH_TOKEN_SECRET") or settings.crop_auth_token_secret,
        }
        if configured_secrets & PLACEHOLDER_SECRETS:
            raise RuntimeError("FATAL: Placeholder secret detected. Rotate secrets before running in production.")
        ping_database()
        database = get_database()
        run_database_migrations(database)
        seed_demo_admin(database)
        whatsapp_task = asyncio.create_task(run_whatsapp_scheduler(whatsapp_stop))
        yield
    except BaseException as exc:
        if _sentry_dsn:
            sentry_sdk.capture_exception(exc)
        raise
    finally:
        whatsapp_stop.set()
        if whatsapp_task:
            whatsapp_task.cancel()
            try:
                await whatsapp_task
            except asyncio.CancelledError:
                pass


app = FastAPI(title="CropConnect ESP32 Ingestion API", version="1.0.0", lifespan=lifespan)


@app.middleware("http")
async def attach_request_id(request: Request, call_next):
    rid = request.headers.get("x-request-id") or str(uuid.uuid4())[:8]
    token = request_id_var.set(rid)
    try:
        response = await call_next(request)
    finally:
        request_id_var.reset(token)
    response.headers["x-request-id"] = rid
    return response


@app.middleware("http")
async def add_security_response_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Content-Security-Policy"] = "default-src 'self'; frame-ancestors 'none'; base-uri 'self'"
    return response


@app.middleware("http")
async def reject_untrusted_browser_origins(request: Request, call_next):
    if request.method in {"POST", "PUT", "PATCH", "DELETE"}:
        origin = (request.headers.get("origin") or "").rstrip("/")
        if origin and not is_trusted_frontend_origin(origin):
            return PlainTextResponse("Origin is not allowed", status_code=403)
        auth_cookie = request.cookies.get(AUTH_COOKIE_NAME)
        if auth_cookie and request.url.path not in CSRF_EXEMPT_PATHS:
            csrf_cookie = request.cookies.get(CSRF_COOKIE_NAME)
            csrf_header = request.headers.get(CSRF_HEADER_NAME)
            if not csrf_cookie or not csrf_header or not secrets.compare_digest(csrf_cookie, csrf_header):
                return PlainTextResponse("CSRF token is missing or invalid", status_code=403)
    return await call_next(request)


app.add_middleware(
    CORSMiddleware,
    allow_origins=FRONTEND_ORIGINS,
    allow_origin_regex=FRONTEND_ORIGIN_REGEX,
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type", "X-API-Key", "X-CSRF-Token"],
)

app.include_router(public_router.router)
app.include_router(auth_router.router)
app.include_router(sensors_router.router)
app.include_router(pumps_router.router)
app.include_router(farm_router.router)
app.include_router(market_router.router)
app.include_router(weather_router.router)
app.include_router(fertilizer_router.router)
app.include_router(ai_router.router)
app.include_router(vision_router.router)
app.include_router(notifications_router.router)


def create_app():
    return app


if __name__ == "__main__":
    import uvicorn

    port = int(os.environ.get("PORT", 5000))
    uvicorn.run(app, host="0.0.0.0", port=port)
