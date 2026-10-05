import unittest

from crop_suitability import rank_crops, score_crop, score_factor


class CropSuitabilityTests(unittest.TestCase):
    def test_factor_scoring_handles_missing_in_range_and_outside_values(self):
        self.assertIsNone(score_factor(None, 5, 7))
        self.assertEqual(score_factor(6, 5, 7), 100)
        self.assertEqual(score_factor(4, 5, 7), 50)
        self.assertEqual(score_factor(2, 5, 7), 0)

    def test_crop_score_renormalizes_available_factors_and_preserves_contract_fields(self):
        crop = {
            "name": "Example", "category": "Cereal", "season": "Rabi", "crop_type": "Food Crops",
            "ph_range": [6, 7], "moisture_range": [40, 60], "temp_range": [20, 30],
            "humidity_range": [50, 70], "rainfall_range": None, "nitrogen_range": None,
            "phosphorus_range": None, "potassium_range": None, "description_template": "Example crop.",
        }
        result = score_crop({"ph": 6.5, "soil_moisture": 50, "temperature": 25, "humidity": 60}, crop)
        self.assertEqual(result["fit"], "100%")
        self.assertEqual(result["missingReadings"], ["nitrogen", "phosphorus", "potassium", "rainfall"])
        self.assertEqual(set(result), {"name", "category", "season", "cropType", "fit", "suitability", "moisture_range", "temp_range", "humidity_range", "ph_range", "rainfall_range", "description", "status_message", "missingReadings"})

    def test_rainfall_forecast_is_used_when_present_and_skipped_when_absent(self):
        crop = {
            "name": "Example", "category": "Cereal", "season": "Rabi", "crop_type": "Food Crops",
            "ph_range": [6, 7], "moisture_range": [40, 60], "temp_range": [20, 30],
            "humidity_range": [50, 70], "rainfall_range": [10, 35], "nitrogen_range": None,
            "phosphorus_range": None, "potassium_range": None, "description_template": "Example crop.",
        }
        base_readings = {"ph": 6.5, "soil_moisture": 50, "temperature": 25, "humidity": 60}

        # No rainfall data supplied (weather lookup failed/unavailable): treated as
        # missing, never as zero, and the crop is still scored from the rest.
        without_rain = score_crop(base_readings, crop)
        self.assertEqual(without_rain["fit"], "100%")
        self.assertIn("rainfall", without_rain["missingReadings"])

        # Rainfall within range contributes to a perfect score too.
        with_good_rain = score_crop({**base_readings, "rainfall": 20}, crop)
        self.assertEqual(with_good_rain["fit"], "100%")
        self.assertNotIn("rainfall", with_good_rain["missingReadings"])

        # Rainfall far outside the crop's range pulls the score down and is
        # reported as the limiting factor.
        with_bad_rain = score_crop({**base_readings, "rainfall": 90}, crop)
        self.assertLess(int(with_bad_rain["fit"].removesuffix("%")), 100)
        self.assertIn("Rainfall", with_bad_rain["status_message"])

    def test_requested_season_is_a_bonus_not_a_filter(self):
        crops = rank_crops({"ph": 6.5, "soil_moisture": 50, "temperature": 25, "humidity": 60}, season="Rabi", top_n=15)
        self.assertEqual(len(crops), 15)
        self.assertTrue(any(crop["season"] != "Rabi" for crop in crops))


if __name__ == "__main__":
    unittest.main()
