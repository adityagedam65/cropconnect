import unittest

from irrigation_advisory import evaluate_irrigation_advice, summarize_advice


class IrrigationAdvisoryTests(unittest.TestCase):
    def test_missing_soil_moisture_is_insufficient_data_without_zero_substitution(self):
        advice = evaluate_irrigation_advice(None, None, None)
        self.assertEqual(advice["action"], "insufficient_data")
        self.assertIsNone(advice["soil_moisture"])
        self.assertIsNone(advice["rain_probability_today"])
        self.assertIsNone(advice["rainfall_7day_mm"])
        self.assertIn("unavailable", advice["reason"])

    def test_very_wet_soil_holds_regardless_of_rain(self):
        self.assertEqual(evaluate_irrigation_advice(85, 0, 0)["action"], "hold")
        self.assertEqual(evaluate_irrigation_advice(85, 100, 50)["action"], "hold")

    def test_dry_soil_with_likely_rain_delays(self):
        self.assertEqual(evaluate_irrigation_advice(20, 80, 5)["action"], "delay")

    def test_dry_soil_without_likely_rain_irrigates(self):
        self.assertEqual(evaluate_irrigation_advice(20, 10, 5)["action"], "irrigate")

    def test_adequate_soil_with_likely_rain_delays(self):
        self.assertEqual(evaluate_irrigation_advice(55, 75, 5)["action"], "delay")

    def test_adequate_soil_without_likely_rain_monitors(self):
        self.assertEqual(evaluate_irrigation_advice(55, 20, 5)["action"], "monitor")

    def test_missing_rain_probability_with_adequate_soil_monitors(self):
        advice = evaluate_irrigation_advice(55, None, None)
        self.assertEqual(advice["action"], "monitor")
        self.assertIn("unavailable", advice["reason"])

    def test_summary_lookup_covers_every_action(self):
        expected = {
            "irrigate": "Irrigation is recommended now.",
            "delay": "Delay irrigation and recheck after the expected rain.",
            "hold": "Hold off on irrigation — soil is already very wet.",
            "monitor": "No irrigation action needed right now — keep monitoring.",
            "insufficient_data": "Not enough sensor data to give irrigation advice yet.",
        }
        for action, summary in expected.items():
            self.assertEqual(summarize_advice({"action": action}), summary)
