"""Create a complete local/demo CropConnect account and device dataset."""
import os
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from db.repositories import create_user, ensure_device, find_user_by_email, insert_device_key, insert_sensor_reading, save_pump_state, update_user, revoke_device_keys
from security_crypto import encrypt_text, hash_password
from services.esp32_service import esp32_key_hash

DEMO_EMAIL = os.getenv("DEMO_EMAIL", "demo@cropconnect.local").strip().lower()
DEMO_PASSWORD = os.getenv("DEMO_PASSWORD", "Demo@12345")
DEMO_DEVICE_ID = os.getenv("DEMO_DEVICE_ID", "demo-esp32-001").strip()
DEMO_API_KEY = os.getenv("DEMO_ESP32_API_KEY", "cc_esp32_demo_key_2026")

def seed_demo() -> int:
    if not DEMO_EMAIL or not DEMO_DEVICE_ID or len(DEMO_PASSWORD) < 8 or not DEMO_API_KEY: raise ValueError("Demo values are invalid")
    user = find_user_by_email(DEMO_EMAIL)
    values = {"password": hash_password(DEMO_PASSWORD), "phone": encrypt_text("9999999999"), "name": encrypt_text("Demo Farmer"), "state": encrypt_text("Maharashtra"), "location": encrypt_text("Pune"), "land_size": 2.5, "location_type": "city", "district": encrypt_text("Pune"), "city": encrypt_text("Pune"), "village": "", "sensor_device_id": DEMO_DEVICE_ID, "sensors": "3", "pumps": "2", "sensor_setup_complete": True, "sensor_setup_status": "complete", "email_verified": True}
    user = update_user(user["id"], values) if user else create_user({"email": DEMO_EMAIL, **values})
    ensure_device(DEMO_DEVICE_ID, display_name="Demo ESP32", location="Pune demo farm")
    revoke_device_keys(DEMO_DEVICE_ID); insert_device_key({"device_id": DEMO_DEVICE_ID, "key_hash": esp32_key_hash(DEMO_API_KEY), "encrypted_key": encrypt_text(DEMO_API_KEY), "status": "active"})
    insert_sensor_reading({"device_id": DEMO_DEVICE_ID, "soil_moisture": 62.4, "humidity": 74.2, "temperature": 28.6, "ph": 6.8, "nitrogen": 42, "phosphorus": 19, "potassium": 31, "raw_payload": {"source": "seed_demo", "demo": True}})
    save_pump_state({"user_id": user["id"], "email": DEMO_EMAIL, "device_id": DEMO_DEVICE_ID, "pump_id": "pump1", "is_on": False, "runtime_minutes": 0, "schedule": {}, "sent_to_esp32": False, "message": "Demo pump ready"})
    print(f"CropConnect demo data is ready. Email: {DEMO_EMAIL}; Password: {DEMO_PASSWORD}; Device: {DEMO_DEVICE_ID}; API key: {DEMO_API_KEY}")
    return 0

if __name__ == "__main__": raise SystemExit(seed_demo())
