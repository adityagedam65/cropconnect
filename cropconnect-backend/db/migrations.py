"""MongoDB indexes and lightweight startup migrations."""
from db.mongodb import get_database


def ensure_all_tables(database=None) -> None:
    database = get_database() if database is None else database
    database.users.create_index("email", unique=True)
    database.users.create_index("sensor_device_id", unique=True, sparse=True)
    database.devices.create_index("device_id", unique=True)
    database.sensor_readings.create_index([("device_id", 1), ("recorded_at", -1)])
    database.esp32_device_keys.create_index("key_hash", unique=True)
    database.esp32_device_keys.create_index([("device_id", 1), ("status", 1)])
    database.current_pump_state.create_index([("user_id", 1), ("pump_id", 1)], unique=True)
    database.relay_statuses.create_index([("device_id", 1), ("relay_number", 1)], unique=True)
    database.public_rate_limits.create_index([("bucket", 1), ("client_host", 1), ("requested_at", 1)])
    database.whatsapp_delivery_logs.create_index([("created_at", -1)])
    database.scheduler_leases.create_index("expires_at", expireAfterSeconds=0)


def run_database_migrations(database=None) -> None:
    ensure_all_tables(database)
