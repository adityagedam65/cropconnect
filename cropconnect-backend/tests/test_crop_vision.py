import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from fastapi.testclient import TestClient

from app import app
from crop_analysis import CropAnalyzer, EXPERT_MESSAGE
from notifications.notifier import Notifier
from vision.dataset_lookup import DatasetLookup, DatasetUnavailableError
from vision.image_validator import ImageValidation
from vision.motion_detection import FieldMonitor
from vision_models.classifier import Classification, CropDiseaseClassifier, DetectorCropDiseaseClassifier, classification_from_detector_label
from vision_models.detector import Detection, PlantDetector


class FakeDetector(PlantDetector):
    def __init__(self, label="plant", confidence=0.9):
        self.detection = Detection(label, confidence)

    def detect(self, _image):
        return [self.detection]


class FakeClassifier(CropDiseaseClassifier):
    def __init__(self, result):
        self.result = result

    def classify(self, _image):
        return self.result


class RecordingNotifier(Notifier):
    def __init__(self):
        self.events = []

    def send_notification(self, _title, _message, event):
        self.events.append(event)


class CropVisionTests(unittest.TestCase):
    def test_invalid_upload_bytes_are_rejected_before_model_loading(self):
        with patch("routers.vision.require_auth_owner", return_value=(1, "demo@example.com")):
            response = TestClient(app).post(
                "/api/vision/analyze",
                content=b"not-an-image",
                headers={"Authorization": "Bearer test-token", "Content-Type": "image/jpeg"},
            )
        self.assertEqual(response.status_code, 422)
        self.assertIn("proper crop or leaf photo", response.json()["detail"])

    def dataset(self, records=None):
        directory = tempfile.TemporaryDirectory()
        path = Path(directory.name) / "dataset.json"
        path.write_text(json.dumps({"records": records or [{
            "crop_name": "Tomato", "disease_name": "Early Blight", "recommendation": "Verified advice"
        }]}), encoding="utf-8")
        self.addCleanup(directory.cleanup)
        return DatasetLookup(path)

    def analyzer(self, classification):
        return CropAnalyzer(FakeDetector(), FakeClassifier(classification), self.dataset())

    @patch("crop_analysis.validate_image", return_value=ImageValidation(False, "Please upload a proper crop or leaf photo."))
    def test_invalid_image_stops_before_classifier(self, _validation):
        classifier = FakeClassifier(Classification("Tomato", "Early Blight", 0.99))
        result = CropAnalyzer(FakeDetector(), classifier, self.dataset()).analyze(b"ignored")
        self.assertFalse(result["valid_image"])
        self.assertIn("proper crop", result["message"])

    @patch("crop_analysis.validate_image", return_value=ImageValidation(True, "ok", object()))
    def test_known_result_returns_only_dataset_recommendation(self, _validation):
        result = self.analyzer(Classification("Tomato", "Early Blight", 0.92)).analyze(b"ignored")
        self.assertTrue(result["result_found"])
        self.assertEqual(result["recommendation"], "Verified advice")
        self.assertEqual(result["source"], "dataset")

    @patch("crop_analysis.validate_image", return_value=ImageValidation(True, "ok", object()))
    def test_unknown_result_never_invents_recommendation(self, _validation):
        result = self.analyzer(Classification("Rice", "Unknown Disease", 0.92)).analyze(b"ignored")
        self.assertFalse(result["result_found"])
        self.assertEqual(result["message"], EXPERT_MESSAGE)
        self.assertNotIn("recommendation", result)

    @patch("crop_analysis.validate_image", return_value=ImageValidation(True, "ok", object()))
    def test_low_confidence_result_requires_expert(self, _validation):
        result = self.analyzer(Classification("Tomato", "Early Blight", 0.40)).analyze(b"ignored")
        self.assertFalse(result["result_found"])
        self.assertEqual(result["source"], "low_confidence")
        self.assertIn("expert", result["message"])

    def test_missing_dataset_is_explicit(self):
        with self.assertRaises(DatasetUnavailableError):
            DatasetLookup("missing-crop-dataset.json")

    def test_detector_fallback_maps_known_disease_label(self):
        classifier = DetectorCropDiseaseClassifier(FakeDetector("Tomato leaf late blight", 0.91))
        self.assertEqual(classifier.classify(object()), Classification("Tomato", "Late Blight", 0.91))

    def test_detector_fallback_rejects_unknown_label(self):
        self.assertIsNone(classification_from_detector_label("person", 0.99))

    def test_classifier_accepts_windows_safe_class_label(self):
        self.assertEqual("Tomato__Late Blight".replace("__", ": "), "Tomato: Late Blight")

    def test_deployed_detector_loads_from_configured_path(self):
        from config import settings
        from crop_analysis import _path_from_config
        from vision_models.detector import UltralyticsPlantDetector

        model_path = _path_from_config(settings.vision_yolo_model_path)
        self.assertTrue(model_path.is_file())
        detector = UltralyticsPlantDetector(model_path)
        self.assertIsInstance(detector, UltralyticsPlantDetector)

    def test_motion_events_respect_cooldown_and_person_detection(self):
        notifier = RecordingNotifier()
        motion = type("AlwaysMotion", (), {"detect": lambda _self, _frame: True})()
        monitor = FieldMonitor(
            capture=None,
            motion_detector=motion,
            notifier=notifier,
            person_detector=FakeDetector("person", 0.91),
            cooldown_seconds=60,
        )
        first = monitor.process_frame(object(), now=100)
        second = monitor.process_frame(object(), now=101)
        third = monitor.process_frame(object(), now=161)
        self.assertEqual(first["event"], "person_detected")
        self.assertIsNone(second)
        self.assertEqual(third["event"], "person_detected")
        self.assertEqual(len(notifier.events), 2)


if __name__ == "__main__":
    unittest.main()
