# End-to-end integration coverage for POST /api/crops/recommend.
#
# Unlike tests/test_crop_suitability.py (which tests the pure scoring
# functions directly), this exercises the actual FastAPI route: auth,
# device-ownership checks, the "no live sensor data" early return, and the
# full response contract the frontend (CropPlanner.jsx) depends on --
# including the weather_context key added when weather was wired into
# crop scoring.
import os
import unittest
from unittest.mock import patch

from fastapi.testclient import TestClient

os.environ.setdefault("CROP_DATA_SECRET_KEY", "test-data-secret-for-unit-tests")
os.environ.setdefault("CROP_AUTH_TOKEN_SECRET", "test-auth-secret-for-unit-tests")

from app import app  # noqa: E402
from routers import ai as ai_routes  # noqa: E402


class CropRecommendEndpointIntegrationTests(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    def profile(self, **overrides):
        base = {
            "state": "Maharashtra",
            "district": "Pune",
            "city": "Pune",
            "village": "",
            "locationType": "city",
            "landSize": 2,
            "sensorDeviceId": "ccdev_test",
        }
        base.update(overrides)
        return base

    def sensor_context(self, **overrides):
        sensor_data = {
            "soil_moisture": 55,
            "humidity": 60,
            "temperature": 26,
            "ph": 6.5,
            "nitrogen": None,
            "phosphorus": None,
            "potassium": None,
        }
        sensor_data.update(overrides)
        return {
            "device_id": "ccdev_test",
            "source": "esp32",
            "sensor_data": sensor_data,
            "readings": [],
            "recorded_at": 1700000000,
            "message": "",
        }

    def base_patches(self, profile=None, sensor_context=None, weather_context=None):
        return (
            patch.object(ai_routes, "require_auth_owner", return_value=(7, "farmer@example.com")),
            patch.object(ai_routes, "enforce_ai_rate_limit"),
            patch.object(ai_routes, "rate_limit_authenticated_request"),
            patch.object(ai_routes, "owner_profile_context", return_value=profile or self.profile()),
            patch.object(ai_routes, "latest_sensor_context", return_value=sensor_context or self.sensor_context()),
            patch.object(
                ai_routes,
                "get_weather_context",
                return_value=weather_context
                if weather_context is not None
                else {
                    "rainfall_7day_mm": 28.0,
                    "rain_probability_today": 40,
                    "resolved_location": "Pune",
                    "source": "open-meteo",
                },
            ),
        )

    def test_crop_recommend_returns_ranked_crops_with_weather_context(self):
        patches = self.base_patches()
        with patches[0], patches[1], patches[2], patches[3], patches[4], patches[5]:
            response = self.client.post("/api/crops/recommend", json={"goal": "balanced", "season": "Kharif"})

        self.assertEqual(response.status_code, 200)
        payload = response.json()

        self.assertTrue(payload["ok"])
        self.assertEqual(payload["source"], "algorithm")
        self.assertEqual(payload["model"], "crop-suitability-v1")
        self.assertIsInstance(payload["crops"], list)
        self.assertGreater(len(payload["crops"]), 0)

        # Frontend (CropPlanner.jsx) contract: every field it reads must be present.
        first_crop = payload["crops"][0]
        for field in (
            "name", "category", "season", "cropType", "fit", "suitability",
            "moisture_range", "temp_range", "humidity_range", "ph_range",
            "description", "status_message", "missingReadings",
        ):
            self.assertIn(field, first_crop)

        # Crops must be sorted descending by numeric fit.
        fits = [int(crop["fit"].removesuffix("%")) for crop in payload["crops"]]
        self.assertEqual(fits, sorted(fits, reverse=True))

        # Weather was fetched and surfaced in the response.
        self.assertEqual(payload["weather_context"]["rainfall_7day_mm"], 28.0)
        self.assertEqual(payload["weather_context"]["source"], "open-meteo")
        self.assertNotIn("unavailable", payload["summary"])

    def test_crop_recommend_degrades_gracefully_when_weather_is_unavailable(self):
        unavailable_weather = {
            "rainfall_7day_mm": None,
            "rain_probability_today": None,
            "resolved_location": None,
            "source": "unavailable",
        }
        patches = self.base_patches(weather_context=unavailable_weather)
        with patches[0], patches[1], patches[2], patches[3], patches[4], patches[5]:
            response = self.client.post("/api/crops/recommend", json={"goal": "balanced"})

        self.assertEqual(response.status_code, 200)
        payload = response.json()

        # Missing weather must never fail the request or silently score
        # rainfall as zero -- it should just be reported as a missing factor.
        self.assertTrue(payload["ok"])
        self.assertGreater(len(payload["crops"]), 0)
        self.assertIn("rainfall", payload["crops"][0]["missingReadings"])
        self.assertIn("unavailable", payload["summary"])

    def test_crop_recommend_uses_ml_model_when_full_npk_is_present(self):
        rice_sensor_context = self.sensor_context(
            nitrogen=90, phosphorus=42, potassium=43, temperature=21,
            humidity=82, ph=6.5, soil_moisture=75,
        )
        patches = self.base_patches(sensor_context=rice_sensor_context)
        with patches[0], patches[1], patches[2], patches[3], patches[4], patches[5]:
            response = self.client.post("/api/crops/recommend", json={"goal": "balanced", "season": "Kharif"})

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload["source"], "ml_model")
        self.assertEqual(payload["model"], "crop-random-forest-v1")
        self.assertIn("Rice", [crop["name"] for crop in payload["crops"][:2]])

    def test_crop_recommend_falls_back_when_npk_is_missing(self):
        patches = self.base_patches()  # Default fixture intentionally has N/P/K as None.
        with patches[0], patches[1], patches[2], patches[3], patches[4], patches[5]:
            response = self.client.post("/api/crops/recommend", json={"goal": "balanced", "season": "Kharif"})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["source"], "algorithm")

    def test_crop_recommend_without_device_returns_400(self):
        patches = self.base_patches(profile=self.profile(sensorDeviceId=""))
        with patches[0], patches[1], patches[2], patches[3], patches[4], patches[5]:
            response = self.client.post("/api/crops/recommend", json={"goal": "balanced"})

        self.assertEqual(response.status_code, 400)

    def test_crop_recommend_with_no_core_sensor_readings_returns_empty_crops(self):
        empty_sensor_context = self.sensor_context(soil_moisture=None, humidity=None, temperature=None, ph=None)
        patches = self.base_patches(sensor_context=empty_sensor_context)
        with patches[0], patches[1], patches[2], patches[3], patches[4], patches[5]:
            response = self.client.post("/api/crops/recommend", json={"goal": "balanced"})

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload["source"], "no_live_sensor_data")
        self.assertEqual(payload["crops"], [])


if __name__ == "__main__":
    unittest.main()
