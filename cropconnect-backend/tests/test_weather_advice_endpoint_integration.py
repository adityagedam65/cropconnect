import os
import unittest
from unittest.mock import patch

from fastapi.testclient import TestClient

os.environ.setdefault("CROP_DATA_SECRET_KEY", "test-data-secret-for-unit-tests")
os.environ.setdefault("CROP_AUTH_TOKEN_SECRET", "test-auth-secret-for-unit-tests")

from app import app  # noqa: E402
from routers import weather as weather_routes  # noqa: E402


class WeatherAdviceEndpointIntegrationTests(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    def profile(self, **overrides):
        profile = {
            "state": "Maharashtra", "district": "Pune", "city": "Pune",
            "village": "", "sensorDeviceId": "ccdev_test",
        }
        profile.update(overrides)
        return profile

    def sensor_context(self, soil_moisture=55):
        return {
            "device_id": "ccdev_test", "source": "esp32",
            "sensor_data": {"soil_moisture": soil_moisture}, "readings": [],
            "recorded_at": 1700000000, "message": "",
        }

    def patches(self, profile=None, sensor_context=None, weather_context=None):
        return (
            patch.object(weather_routes, "require_auth_owner", return_value=(7, "farmer@example.com")),
            patch.object(weather_routes, "rate_limit_authenticated_request"),
            patch.object(weather_routes, "owner_profile_context", return_value=profile or self.profile()),
            patch.object(weather_routes, "latest_sensor_context", return_value=sensor_context or self.sensor_context()),
            patch.object(weather_routes, "get_weather_context", return_value=weather_context or {
                "rainfall_7day_mm": 28.0, "rain_probability_today": 75,
                "resolved_location": "Pune", "source": "open-meteo",
            }),
        )

    def test_weather_advice_returns_full_algorithm_response(self):
        patches = self.patches()
        with patches[0], patches[1], patches[2], patches[3], patches[4]:
            response = self.client.post("/api/weather/advice")

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertTrue(payload["ok"])
        self.assertEqual(payload["source"], "algorithm")
        self.assertEqual(payload["advice"]["action"], "delay")
        self.assertIn("reason", payload["advice"])
        self.assertEqual(payload["summary"], "Delay irrigation and recheck after the expected rain.")
        self.assertIn("sensor_context", payload)
        self.assertIn("weather_context", payload)

    def test_weather_advice_without_device_returns_400(self):
        patches = self.patches(profile=self.profile(sensorDeviceId=""))
        with patches[0], patches[1], patches[2], patches[3], patches[4]:
            response = self.client.post("/api/weather/advice")

        self.assertEqual(response.status_code, 400)

    def test_weather_advice_handles_unavailable_weather(self):
        unavailable = {
            "rainfall_7day_mm": None, "rain_probability_today": None,
            "resolved_location": None, "source": "unavailable",
        }
        patches = self.patches(weather_context=unavailable)
        with patches[0], patches[1], patches[2], patches[3], patches[4]:
            response = self.client.post("/api/weather/advice")

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload["advice"]["action"], "monitor")
        self.assertEqual(payload["weather_context"]["source"], "unavailable")
