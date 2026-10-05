# Pytest fixtures for DB-backed endpoint integration tests.
import os

import mongomock
import pytest

os.environ.setdefault("CROP_DATA_SECRET_KEY", "test-data-secret-for-unit-tests")
os.environ.setdefault("CROP_AUTH_TOKEN_SECRET", "test-auth-secret-for-unit-tests")

from routers import auth as auth_routes  # noqa: E402
from services import rate_limit as rate_limit_service  # noqa: E402
from db import mongodb  # noqa: E402


@pytest.fixture
def fake_db(monkeypatch):
    client = mongomock.MongoClient()
    monkeypatch.setattr(mongodb, "_client", client)
    database = client.cropconnect_test
    database.users.create_index("email", unique=True)
    database.devices.create_index("device_id", unique=True)
    return {
        "users": database.users,
        "devices": database.devices,
        "readings": database.sensor_readings,
        "rate_limits": database.public_rate_limits,
    }
