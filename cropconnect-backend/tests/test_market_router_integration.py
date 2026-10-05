import os
import unittest
from unittest.mock import patch

from fastapi.testclient import TestClient

os.environ.setdefault("CROP_DATA_SECRET_KEY", "test-data-secret-for-unit-tests")
os.environ.setdefault("CROP_AUTH_TOKEN_SECRET", "test-auth-secret-for-unit-tests")

from app import app  # noqa: E402
from routers import market as market_routes  # noqa: E402
from services import auth_service, market_service  # noqa: E402


class FakeCursor:
    def __init__(self, row=None):
        self.row = row
        self.lastrowid = 1
        self.rowcount = 1

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, traceback):
        return False

    def execute(self, *_args, **_kwargs):
        return None

    def fetchone(self):
        return self.row

    def fetchall(self):
        return [self.row] if self.row else []


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


class MarketRouterIntegrationTests(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)
        self.original_data_gov_api_key = market_routes.settings.data_gov_api_key
        self.original_gemini_api_key = market_routes.settings.gemini_api_key

    def tearDown(self):
        market_routes.settings.data_gov_api_key = self.original_data_gov_api_key
        market_routes.settings.gemini_api_key = self.original_gemini_api_key

    def auth_patches(self, profile=None):
        fake_conn = FakeConnection(FakeCursor())
        return (
            patch.object(market_routes, "require_auth_owner", return_value=(7, "farmer@example.com")),
            patch.object(market_routes, "rate_limit_authenticated_request"),
            patch.object(auth_service, "get_connection", return_value=fake_conn),
            patch.object(market_routes, "owner_profile_context", return_value=profile or self.profile()),
        )

    def profile(self):
        return {
            "state": "Maharashtra",
            "district": "Pune",
            "city": "Pune",
            "village": "",
            "locationType": "city",
            "landSize": 2,
            "sensorDeviceId": "ccdev_test",
        }

    def market_record(self):
        return {
            "state": "Maharashtra",
            "district": "Pune",
            "market": "Pune",
            "commodity": "Tomato",
            "variety": "Local",
            "grade": "FAQ",
            "arrival_date": "26/05/2026",
            "min_price": "1000",
            "max_price": "1400",
            "modal_price": "1200",
        }

    def test_market_prices_returns_503_when_data_gov_key_missing(self):
        market_routes.settings.data_gov_api_key = ""

        with self.auth_patches()[0], self.auth_patches()[1], self.auth_patches()[2], self.auth_patches()[3]:
            response = self.client.get("/api/market/prices", headers={"Authorization": "Bearer test"})

        self.assertEqual(response.status_code, 503)

    def test_market_prices_returns_400_when_profile_has_no_state(self):
        market_routes.settings.data_gov_api_key = "test-data-gov-key"
        profile = self.profile()
        profile["state"] = ""

        with patch.object(market_routes, "require_auth_owner", return_value=(7, "farmer@example.com")), patch.object(
            market_routes,
            "rate_limit_authenticated_request",
        ), patch.object(auth_service, "get_connection", return_value=FakeConnection(FakeCursor())), patch.object(
            market_routes,
            "owner_profile_context",
            return_value=profile,
        ):
            response = self.client.get("/api/market/prices", headers={"Authorization": "Bearer test"})

        self.assertEqual(response.status_code, 400)

    def test_market_prices_returns_200_with_mocked_market_records(self):
        market_routes.settings.data_gov_api_key = "test-data-gov-key"

        with patch.object(market_routes, "require_auth_owner", return_value=(7, "farmer@example.com")), patch.object(
            market_routes,
            "rate_limit_authenticated_request",
        ), patch.object(auth_service, "get_connection", return_value=FakeConnection(FakeCursor())), patch.object(
            market_routes,
            "owner_profile_context",
            return_value=self.profile(),
        ), patch.object(market_routes, "data_gov_market_records", return_value=[self.market_record()]):
            response = self.client.get("/api/market/prices", headers={"Authorization": "Bearer test"})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["recordsCount"], 1)

    def test_market_insight_returns_503_when_ai_provider_missing(self):
        market_routes.settings.gemini_api_key = ""

        with patch.object(market_routes, "require_auth_owner", return_value=(7, "farmer@example.com")), patch.object(
            market_routes,
            "rate_limit_authenticated_request",
        ), patch.object(auth_service, "get_connection", return_value=FakeConnection(FakeCursor())):
            response = self.client.post("/api/market/insights", json={}, headers={"Authorization": "Bearer test"})

        self.assertEqual(response.status_code, 503)

    def test_market_insight_returns_200_with_mocked_ai_response(self):
        market_routes.settings.data_gov_api_key = "test-data-gov-key"
        market_routes.settings.gemini_api_key = "test-gemini-key"
        ai_response = '{"summary":"Prices are steady","recommendations":[{"title":"Hold","action":"Wait","reason":"Stable modal price","confidence":"medium"}],"watch":["Rain"]}'

        with patch.object(market_routes, "require_auth_owner", return_value=(7, "farmer@example.com")), patch.object(
            market_routes,
            "rate_limit_authenticated_request",
        ), patch.object(auth_service, "get_connection", return_value=FakeConnection(FakeCursor())), patch.object(
            market_routes,
            "owner_profile_context",
            return_value=self.profile(),
        ), patch.object(market_service, "data_gov_market_records", return_value=[self.market_record()]), patch.object(
            market_routes,
            "latest_sensor_context",
            return_value={"source": "esp32", "sensor_data": {}, "message": ""},
        ), patch.object(market_routes, "chat_completion_text", return_value=ai_response):
            response = self.client.post("/api/market/insights", json={}, headers={"Authorization": "Bearer test"})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["summary"], "Prices are steady")


if __name__ == "__main__":
    unittest.main()
