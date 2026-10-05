import unittest

from irrigation_advisory import HIGH_MOISTURE_THRESHOLD, LOW_MOISTURE_THRESHOLD
from stress_detection import evaluate_stress_conditions


class StressDetectionTests(unittest.TestCase):
    def types(self, **values):
        return {item["type"] for item in evaluate_stress_conditions(**values)["conditions"]}

    def test_water_stress_thresholds(self):
        self.assertIn("water_stress", self.types(soil_moisture=LOW_MOISTURE_THRESHOLD - 0.1, ph=None, temperature=None, humidity=None))
        self.assertNotIn("water_stress", self.types(soil_moisture=LOW_MOISTURE_THRESHOLD, ph=None, temperature=None, humidity=None))
        self.assertIn("water_stress", self.types(soil_moisture=HIGH_MOISTURE_THRESHOLD, ph=None, temperature=None, humidity=None))

    def test_ph_heat_and_fungal_indicators(self):
        self.assertIn("ph_stress", self.types(soil_moisture=None, ph=5.4, temperature=None, humidity=None))
        self.assertNotIn("ph_stress", self.types(soil_moisture=None, ph=5.5, temperature=None, humidity=None))
        self.assertIn("heat_stress", self.types(soil_moisture=None, ph=None, temperature=38.1, humidity=None))
        self.assertNotIn("heat_stress", self.types(soil_moisture=None, ph=None, temperature=38, humidity=None))
        self.assertIn("fungal_risk_indicator", self.types(soil_moisture=None, ph=None, temperature=20, humidity=85.1))
        self.assertNotIn("fungal_risk_indicator", self.types(soil_moisture=None, ph=None, temperature=20, humidity=85))

    def test_missing_readings_produce_no_false_flags(self):
        result = evaluate_stress_conditions(None, None, None, None)
        self.assertEqual(result["conditions"], [])
        self.assertEqual(set(result["missingReadings"]), {"soil_moisture", "ph", "temperature", "humidity"})
