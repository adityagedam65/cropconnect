"""Idempotent local-demo records created when the API starts."""
from __future__ import annotations

from datetime import datetime, timezone

from db.repositories import next_id
from security_crypto import encrypt_text, hash_password
from services.esp32_service import esp32_key_hash

# These credentials are deliberately static for the demo environment.  Do not
# enable this seed in a production deployment with publicly reachable MongoDB.
DEMO_ADMIN_EMAIL = "demo@cropconncet.local"
DEMO_ADMIN_PASSWORD = "Demo@12345"
DEMO_ESP32_DEVICE_ID = "CC-ESP32-DEMO-ADMIN-01"
DEMO_ESP32_API_KEY = "cc_esp32_demo_admin_8PXf4Zq7wK2mR9nV5tY1aC6dH3jL0sE"


def seed_demo_admin(database) -> None:
    """Create the demo admin, ESP32 device, and key without replacing records.

    The password is hashed and the device key is encrypted at rest. Repeated
    application starts leave an existing account and key unchanged.
    """
    now = datetime.now(timezone.utc)
    database.devices.update_one(
        {"device_id": DEMO_ESP32_DEVICE_ID},
        {
            "$setOnInsert": {
                "device_id": DEMO_ESP32_DEVICE_ID,
                "created_at": now,
                "label": "Demo admin ESP32",
            }
        },
        upsert=True,
    )

    if not database.users.find_one({"email": DEMO_ADMIN_EMAIL}, {"_id": 1}):
        database.users.insert_one(
            {
                "id": next_id("users"),
                "email": DEMO_ADMIN_EMAIL,
                "password": hash_password(DEMO_ADMIN_PASSWORD),
                "name": encrypt_text("Demo Administrator"),
                "phone": encrypt_text(""),
                "state": encrypt_text(""),
                "location": encrypt_text(""),
                "location_type": "city",
                "district": encrypt_text(""),
                "city": encrypt_text(""),
                "village": encrypt_text(""),
                "land_size": None,
                "sensor_device_id": DEMO_ESP32_DEVICE_ID,
                "sensors": "1",
                "pumps": "1",
                "sensor_setup_complete": True,
                "sensor_setup_status": "complete",
                "email_verified": True,
                "role": "admin",
                "created_at": now,
            }
        )

    # Store the fixed key once. The key hash is what the ingestion API checks;
    # encrypted_key lets the existing device-key tooling manage the record.
    key_hash = esp32_key_hash(DEMO_ESP32_API_KEY)
    if not database.esp32_device_keys.find_one({"key_hash": key_hash}):
        database.esp32_device_keys.insert_one(
            {
                "id": next_id("esp32_device_keys"),
                "device_id": DEMO_ESP32_DEVICE_ID,
                "key_hash": key_hash,
                "encrypted_key": encrypt_text(DEMO_ESP32_API_KEY),
                "status": "active",
                "created_at": now,
                "label": "Demo admin ESP32 key",
            }
        )
