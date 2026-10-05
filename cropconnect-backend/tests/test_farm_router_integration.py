import os
import unittest
from unittest.mock import patch

from fastapi import HTTPException
from fastapi.testclient import TestClient

os.environ.setdefault("CROP_DATA_SECRET_KEY", "test-data-secret-for-unit-tests")
os.environ.setdefault("CROP_AUTH_TOKEN_SECRET", "test-auth-secret-for-unit-tests")

from app import app  # noqa: E402
from routers import farm as farm_routes  # noqa: E402


class FakeCursor:
    def __init__(self, rows=None):
        self.rows = rows or []
        self.lastrowid = 1
        self.rowcount = 1

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, traceback):
        return False

    def execute(self, *_args, **_kwargs):
        return None

    def fetchall(self):
        return self.rows

    def fetchone(self):
        return self.rows[0] if self.rows else None


class FakeConnection:
    def __init__(self, cursor):
        self._cursor = cursor

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, traceback):
        return False

    def cursor(self, **_kwargs):
        return self._cursor

    def commit(self):
        return None


class FarmRouterIntegrationTests(unittest.TestCase):
    def test_chat_history_returns_list_when_authenticated(self):
        client = TestClient(app)
        fake_conn = FakeConnection(FakeCursor([
            {
                "id": 1,
                "message_type": "user",
                "text": "When should I irrigate?",
                "related_to_plant_or_soil": 1,
                "created_at": "2026-05-26T00:00:00+00:00",
            }
        ]))

        with patch.object(farm_routes, "require_auth_owner", return_value=(7, "farmer@example.com")), patch.object(
            farm_routes,
            "get_connection",
            return_value=fake_conn,
        ):
            response = client.get("/api/farm/chat-history", headers={"Authorization": "Bearer test"})

        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.json()["items"], list)

    def test_chat_history_returns_401_without_auth(self):
        client = TestClient(app)

        with patch.object(
            farm_routes,
            "require_auth_owner",
            side_effect=HTTPException(status_code=401, detail="Authentication required"),
        ):
            response = client.get("/api/farm/chat-history")

        self.assertEqual(response.status_code, 401)

    def test_dashboard_snapshot_returns_200_when_authenticated(self):
        client = TestClient(app)
        payload = {
            "user_id": 7,
            "email": "farmer@example.com",
            "device_id": "ccdev_test",
            "source": "dashboard",
            "sensor_data": {"soilMoisture": 45},
            "pump_data": {"pump1": {"on": False}},
            "timers": {},
            "weather_data": None,
            "market_data": None,
            "telemetry_packet": {},
        }

        with patch.object(farm_routes, "require_auth_owner", return_value=(7, "farmer@example.com")):
            response = client.post("/api/farm/snapshot", json=payload, headers={"Authorization": "Bearer test"})

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()["ok"])

    def test_dashboard_snapshot_returns_401_without_auth(self):
        client = TestClient(app)

        with patch.object(
            farm_routes,
            "require_auth_owner",
            side_effect=HTTPException(status_code=401, detail="Authentication required"),
        ):
            response = client.post("/api/farm/snapshot", json={"sensor_data": {}})

        self.assertEqual(response.status_code, 401)


if __name__ == "__main__":
    unittest.main()
