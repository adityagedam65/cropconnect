# Integration coverage for public AI utility routes.
import unittest
from unittest.mock import patch

from fastapi.testclient import TestClient

from app import app
from routers import ai as ai_routes


class AiRouterIntegrationTests(unittest.TestCase):
    def test_translate_returns_translated_text(self):
        client = TestClient(app)
        with (
            patch.object(ai_routes, "PUBLIC_TRANSLATION_ENABLED", True),
            patch.object(ai_routes, "rate_limit_public_request"),
            patch.object(ai_routes, "translate_texts_with_ai", return_value=["नमस्ते"]),
        ):
            response = client.post("/api/utils/translate", json={"text": "Hello", "target_lang": "hi"})

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload["translations"], ["नमस्ते"])
        self.assertEqual(payload["translated"], "नमस्ते")

    def test_translate_rejects_empty_payload(self):
        client = TestClient(app)
        with patch.object(ai_routes, "PUBLIC_TRANSLATION_ENABLED", True), patch.object(ai_routes, "rate_limit_public_request"):
            response = client.post("/api/utils/translate", json={"target_lang": "hi"})

        self.assertEqual(response.status_code, 422)

    def test_irrigation_question_sends_algorithm_advice_to_gemini(self):
        client = TestClient(app)
        captured = {}

        def fake_completion(messages, **_kwargs):
            captured["messages"] = messages
            return "Use the algorithm's irrigation advice."

        with (
            patch.object(ai_routes.settings, "gemini_api_key", "test-key"),
            patch.object(ai_routes, "require_auth_owner", return_value=(7, "farmer@example.com")),
            patch.object(ai_routes, "enforce_ai_rate_limit"),
            patch.object(ai_routes, "rate_limit_authenticated_request"),
            patch.object(ai_routes, "classify_farm_scope_with_ai", return_value=True),
            patch.object(ai_routes, "owner_profile_context", return_value={"sensorDeviceId": "ccdev_test", "city": "Pune", "state": "Maharashtra"}),
            patch.object(ai_routes, "latest_sensor_context", return_value={"source": "esp32", "sensor_data": {"soil_moisture": 20}, "recorded_at": 1, "message": ""}),
            patch.object(ai_routes, "get_weather_context", return_value={"rain_probability_today": 10, "rainfall_7day_mm": 0}),
            patch.object(ai_routes, "google_search", return_value=[]),
            patch.object(ai_routes, "insert_chat_record"),
            patch.object(ai_routes, "chat_completion_text", side_effect=fake_completion),
        ):
            response = client.post("/api/ai/chat", json={"message": "Should I irrigate my field?"})

        self.assertEqual(response.status_code, 200)
        context_message = next(item["content"] for item in captured["messages"] if "Current CropConnect dashboard context" in item["content"])
        self.assertIn("irrigation_advice", context_message)
        self.assertIn('"action": "irrigate"', context_message)


if __name__ == "__main__":
    unittest.main()
