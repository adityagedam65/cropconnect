import unittest

from crop_ml_recommendation import is_model_available, rank_crops_ml


RICE_READINGS = {
    "nitrogen": 90, "phosphorus": 42, "potassium": 43,
    "temperature": 21, "humidity": 82, "ph": 6.5, "soil_moisture": 75,
}


class CropMlRecommendationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if not is_model_available():
            raise RuntimeError("Run scripts/train_crop_model.py before ML recommendation tests")

    def test_rice_like_readings_rank_rice_in_top_two(self):
        crops = rank_crops_ml(RICE_READINGS)
        self.assertIn("Rice", [crop["name"] for crop in crops[:2]])

    def test_missing_required_feature_raises_value_error(self):
        readings = {**RICE_READINGS, "nitrogen": None}
        with self.assertRaisesRegex(ValueError, "nitrogen"):
            rank_crops_ml(readings)

    def test_bad_moisture_reduces_fit_without_changing_model_probability(self):
        good_rice = next(crop for crop in rank_crops_ml(RICE_READINGS, top_n=22) if crop["name"] == "Rice")
        bad_rice = next(crop for crop in rank_crops_ml({**RICE_READINGS, "soil_moisture": 0}, top_n=22) if crop["name"] == "Rice")
        self.assertEqual(good_rice["model_probability"], bad_rice["model_probability"])
        self.assertLess(int(bad_rice["fit"].removesuffix("%")), int(good_rice["fit"].removesuffix("%")))

    def test_missing_soil_moisture_does_not_adjust_probability(self):
        rice = next(crop for crop in rank_crops_ml({**RICE_READINGS, "soil_moisture": None}, top_n=22) if crop["name"] == "Rice")
        self.assertEqual(rice["moisture_adjustment"], 1.0)
        self.assertIn("soil_moisture", rice["missingReadings"])

    def test_full_dataset_crop_list_is_covered_by_crop_knowledge(self):
        # Every crop the model can predict must have a matching entry in
        # crop_knowledge.py, or moisture/season fusion and the description
        # fields silently degrade to "Unknown"/no profile for that crop.
        crops = rank_crops_ml(RICE_READINGS, top_n=22)
        self.assertEqual(len(crops), 22)
        unknown = [c["name"] for c in crops if c["category"] == "Unknown"]
        self.assertEqual(unknown, [])

    def test_matching_season_gives_a_bonus_without_changing_model_probability(self):
        no_season = next(c for c in rank_crops_ml(RICE_READINGS, top_n=22) if c["name"] == "Rice")
        matching = next(c for c in rank_crops_ml(RICE_READINGS, top_n=22, season="Kharif") if c["name"] == "Rice")
        non_matching = next(c for c in rank_crops_ml(RICE_READINGS, top_n=22, season="Rabi") if c["name"] == "Rice")

        self.assertEqual(no_season["model_probability"], matching["model_probability"])
        self.assertEqual(no_season["model_probability"], non_matching["model_probability"])
        self.assertGreaterEqual(int(matching["fit"].removesuffix("%")), int(no_season["fit"].removesuffix("%")))
        self.assertEqual(int(non_matching["fit"].removesuffix("%")), int(no_season["fit"].removesuffix("%")))
        self.assertIn("season", matching["status_message"].lower())

    def test_fit_percentage_never_exceeds_100(self):
        # A season bonus on an already-high-confidence prediction must be
        # capped, not overflow past 100%.
        crops = rank_crops_ml(RICE_READINGS, top_n=22, season="Kharif")
        for crop in crops:
            self.assertLessEqual(int(crop["fit"].removesuffix("%")), 100)


if __name__ == "__main__":
    unittest.main()
