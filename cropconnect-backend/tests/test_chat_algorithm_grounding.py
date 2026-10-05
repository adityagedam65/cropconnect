"""Regression tests for deterministic advice injected into Gemini chat context."""
import unittest
from unittest.mock import patch

from fastapi.testclient import TestClient

from app import app
from routers import ai as ai_routes


class ChatAlgorithmGroundingTests(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)
        self.captured_messages = []

    @staticmethod
    def profile():
        return {"sensorDeviceId": "ccdev_test", "city": "Pune", "state": "Maharashtra"}

    @staticmethod
    def sensor_context():
        return {
            "source": "esp32",
            "sensor_data": {"soil_moisture": 20},
            "recorded_at": 1,
            "message": "",
        }

    def chat_patches(self):
        def fake_completion(messages, **_kwargs):
            self.captured_messages = messages
            return "Grounded farming advice."

        return (
            patch.object(ai_routes.settings, "gemini_api_key", "test-key"),
            patch.object(ai_routes, "require_auth_owner", return_value=(7, "farmer@example.com")),
            patch.object(ai_routes, "enforce_ai_rate_limit"),
            patch.object(ai_routes, "rate_limit_authenticated_request"),
            patch.object(ai_routes, "classify_farm_scope_with_ai", return_value=True),
            patch.object(ai_routes, "owner_profile_context", return_value=self.profile()),
            patch.object(ai_routes, "latest_sensor_context", return_value=self.sensor_context()),
            patch.object(ai_routes, "get_weather_context", return_value={"rain_probability_today": 10, "rainfall_7day_mm": 0}),
            patch.object(ai_routes, "google_search", return_value=[]),
            patch.object(ai_routes, "insert_chat_record"),
            patch.object(ai_routes, "chat_completion_text", side_effect=fake_completion),
        )

    def dashboard_context(self):
        return next(
            message["content"]
            for message in self.captured_messages
            if "Current CropConnect dashboard context" in message["content"]
        )

    def test_irrigation_keywords_trigger_grounded_context(self):
        patches = self.chat_patches()
        with patches[0], patches[1], patches[2], patches[3], patches[4], patches[5], patches[6], patches[7], patches[8], patches[9], patches[10]:
            response = self.client.post("/api/ai/chat", json={"message": "Should I water my field today?"})

        self.assertEqual(response.status_code, 200)
        context = self.dashboard_context()
        self.assertIn("algorithm_results", context)
        self.assertIn("irrigation_advice", context)
        self.assertIn('"action": "irrigate"', context)

    def test_unrelated_message_has_no_algorithm_results(self):
        patches = self.chat_patches()
        with patches[0], patches[1], patches[2], patches[3], patches[4], patches[5], patches[6], patches[7], patches[8], patches[9], patches[10]:
            response = self.client.post("/api/ai/chat", json={"message": "What's the weather like in general?"})

        self.assertEqual(response.status_code, 200)
        self.assertNotIn("algorithm_results", self.dashboard_context())


if __name__ == "__main__":
    unittest.main()
