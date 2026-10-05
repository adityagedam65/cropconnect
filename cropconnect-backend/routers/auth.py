import hashlib
import secrets
from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, Depends, HTTPException, Request, Response
from pydantic import BaseModel
from config import settings
from db.repositories import create_user, ensure_device, find_user_by_email, find_user_by_id, find_valid_token, save_token, update_user, use_token
from models import AuthLoginIn, AuthPasswordResetConfirmIn, AuthPasswordResetRequestIn, AuthProfileUpdateIn, AuthSignupIn
from security_crypto import encrypt_text, hash_password, refresh_auth_token, verify_password
from services import rate_limit as rate_limit_service
from services.auth_service import auth_token_for_user, auth_token_from_request, clear_auth_cookie, generate_sensor_device_id, send_password_reset_email, set_auth_cookie, set_csrf_cookie, smtp_configured, token_hash, user_row_to_payload
from services.deps import get_current_user
from services.email_service import send_verification_email

router = APIRouter()
ENCRYPTED_PROFILE_FIELDS = {"name", "phone", "state", "location", "city", "village", "district"}
class VerifyEmailIn(BaseModel):
    email: str
    code: str

def verification_token_hash(user_id: int, code: str) -> str:
    return hashlib.sha256(f"{user_id}:{code}:{settings.crop_auth_token_secret}".encode()).hexdigest()

def load_owner_profile(owner_id: int):
    row = find_user_by_id(owner_id)
    return user_row_to_payload(row) if row else {}

@router.post("/api/auth/signup")
def auth_signup(payload: AuthSignupIn, request: Request, response: Response):
    email = payload.email.strip().lower(); rate_limit_service.rate_limit_public_request(request, "auth-signup-ip", 5, 3600)
    if find_user_by_email(email): raise HTTPException(status_code=409, detail="An account with this email already exists")
    location_type = payload.location_type or "city"; city = payload.city or (payload.location if location_type == "city" else ""); village = payload.village or (payload.location if location_type == "village" else "")
    device_id = generate_sensor_device_id(); ensure_device(device_id)
    row = create_user({"email": email, "password": hash_password(payload.password), "phone": encrypt_text(payload.phone or ""), "name": encrypt_text(payload.name), "state": encrypt_text(payload.state or ""), "location": encrypt_text(payload.location or ""), "land_size": payload.land_size, "location_type": location_type, "district": encrypt_text(payload.district or ""), "city": encrypt_text(city), "village": encrypt_text(village), "sensor_device_id": device_id, "sensors": payload.sensors or "0", "pumps": payload.pumps or "0", "sensor_setup_complete": bool(payload.sensor_setup_complete), "sensor_setup_status": payload.sensor_setup_status or "pending", "email_verified": False})
    user = user_row_to_payload(row); sent = False
    if smtp_configured():
        code = str(secrets.randbelow(900000) + 100000); save_token({"email": email, "token_hash": verification_token_hash(row["id"], code), "expires_at": datetime.now(timezone.utc) + timedelta(hours=24)}); sent = send_verification_email(email, user.get("name", ""), code)
    token = auth_token_for_user(user); csrf = set_auth_cookie(response, token)
    return {"ok": True, "user": user, "token": token, "csrfToken": csrf, "emailVerificationSent": sent}

@router.post("/api/auth/verify-email")
def verify_email(payload: VerifyEmailIn):
    email = payload.email.strip().lower(); code = payload.code.strip(); user = find_user_by_email(email)
    if len(code) != 6 or not code.isdigit() or not user: raise HTTPException(status_code=400, detail="Invalid or expired verification code.")
    token = find_valid_token(email, verification_token_hash(user["id"], code))
    if not token: raise HTTPException(status_code=400, detail="Invalid or expired verification code.")
    use_token(token["id"]); update_user(user["id"], {"email_verified": True}); return {"ok": True, "message": "Email verified successfully."}

@router.post("/api/auth/login")
def auth_login(payload: AuthLoginIn, request: Request, response: Response):
    email = payload.email.strip().lower(); rate_limit_service.rate_limit_public_request(request, "auth-login-ip", 20, 900)
    row = find_user_by_email(email)
    if not row or not verify_password(payload.password, row.get("password", "")): raise HTTPException(status_code=401, detail="Email and password do not match")
    user = user_row_to_payload(row); token = auth_token_for_user(user); csrf = set_auth_cookie(response, token); return {"ok": True, "user": user, "token": token, "csrfToken": csrf}

@router.post("/api/auth/logout")
def auth_logout(response: Response):
    clear_auth_cookie(response); return {"ok": True}

@router.get("/api/auth/csrf")
def auth_csrf(response: Response, _current_user: tuple[int, str] = Depends(get_current_user)):
    csrf = secrets.token_urlsafe(32); set_csrf_cookie(response, csrf); return {"ok": True, "csrfToken": csrf}

@router.get("/api/auth/refresh")
def auth_refresh(response: Response, request: Request):
    fresh = refresh_auth_token(auth_token_from_request(request.headers.get("authorization"), request.cookies.get("cropconnect_auth")))
    if not fresh: return {"ok": True, "refreshed": False}
    csrf = set_auth_cookie(response, fresh); return {"ok": True, "refreshed": True, "token": fresh, "csrfToken": csrf}

@router.get("/api/auth/profile")
def auth_profile(current_user: tuple[int, str] = Depends(get_current_user)):
    user = load_owner_profile(current_user[0])
    if not user: raise HTTPException(status_code=404, detail="User not found")
    return {"ok": True, "user": user}

@router.post("/api/auth/password-reset-request")
def auth_password_reset_request(payload: AuthPasswordResetRequestIn, request: Request):
    email = payload.email.strip().lower(); rate_limit_service.rate_limit_public_request(request, "password-reset", 3, 900); row = find_user_by_email(email)
    if row and smtp_configured():
        reset = secrets.token_urlsafe(32); save_token({"email": email, "token_hash": token_hash(reset), "expires_at": datetime.now(timezone.utc) + timedelta(minutes=settings.password_reset_token_ttl_minutes)}); send_password_reset_email(email, f"{settings.frontend_public_url.rstrip('/')}/reset-password?email={email}&token={reset}")
    return {"ok": True, "message": "If an account exists, password reset instructions will be sent."}

@router.post("/api/auth/password-reset-confirm")
def auth_password_reset_confirm(payload: AuthPasswordResetConfirmIn, request: Request):
    email = payload.email.strip().lower(); rate_limit_service.rate_limit_public_request(request, "password-reset-confirm", 8, 900); token = find_valid_token(email, token_hash(payload.token.strip())); user = find_user_by_email(email)
    if not token or not user: raise HTTPException(status_code=400, detail="Reset link is invalid or expired")
    update_user(user["id"], {"password": hash_password(payload.password)}); use_token(token["id"]); return {"ok": True, "message": "Password has been reset"}

@router.post("/api/auth/profile")
def auth_profile_update(payload: AuthProfileUpdateIn, current_user: tuple[int, str] = Depends(get_current_user)):
    data = payload.model_dump(exclude_unset=True); allowed = {"name", "phone", "state", "location", "land_size", "location_type", "district", "city", "village", "sensors", "pumps", "sensor_setup_status", "sensor_setup_complete"}; updates = {}
    for key, value in data.items():
        if key in allowed and value is not None: updates[key] = encrypt_text(value) if key in ENCRYPTED_PROFILE_FIELDS else value
    if not updates: raise HTTPException(status_code=400, detail="No profile fields provided")
    row = update_user(current_user[0], updates)
    if not row: raise HTTPException(status_code=404, detail="User not found")
    return {"ok": True, "user": user_row_to_payload(row)}
