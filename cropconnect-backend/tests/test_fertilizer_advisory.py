import os
import unittest
from unittest.mock import patch

from fastapi.testclient import TestClient

os.environ.setdefault("CROP_DATA_SECRET_KEY", "test-data-secret-for-unit-tests")
os.environ.setdefault("CROP_AUTH_TOKEN_SECRET", "test-auth-secret-for-unit-tests")

from app import app  # noqa: E402
from fertilizer_advisory import evaluate_fertilizer_advice, nutrient_status  # noqa: E402
from routers import fertilizer as fertilizer_routes  # noqa: E402


class FertilizerAdvisoryTests(unittest.TestCase):
    def test_status_bands_and_boundaries(self):
        for low_max, medium_max in ((280, 560), (10, 25), (110, 280)):
            self.assertEqual(nutrient_status(None, low_max, medium_max), "unavailable")
            self.assertEqual(nutrient_status(low_max - 0.1, low_max, medium_max), "low")
            self.assertEqual(nutrient_status(low_max, low_max, medium_max), "medium")
            self.assertEqual(nutrient_status(medium_max, low_max, medium_max), "medium")
            self.assertEqual(nutrient_status(medium_max + 0.1, low_max, medium_max), "high")

    def test_missing_values_are_not_treated_as_zero(self):
        advice = evaluate_fertilizer_advice(None, 10, None)
        self.assertEqual(advice["nutrients"]["nitrogen"]["status"], "unavailable")
        self.assertEqual(advice["nutrients"]["phosphorus"]["status"], "medium")
        self.assertEqual(advice["missingReadings"], ["nitrogen", "potassium"])

    def test_endpoint_blocks_unverified_mg_per_kg_conversion(self):
        client = TestClient(app)
        with (
            patch.object(fertilizer_routes, "require_auth_owner", return_value=(7, "farmer@example.com")),
            patch.object(fertilizer_routes, "rate_limit_authenticated_request"),
            patch.object(fertilizer_routes, "owner_profile_context", return_value={"sensorDeviceId": "ccdev_test"}),
            patch.object(fertilizer_routes, "latest_sensor_context", return_value={"sensor_data": {"nitrogen": 90, "phosphorus": 42, "potassium": 43}}),
        ):
            response = client.post("/api/fertilizer/advice")
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload["unit_status"], "unsupported")
        self.assertIn("mg/kg", payload["message"])
        self.assertEqual(payload["advice"]["nutrients"]["nitrogen"]["status"], "unavailable")
