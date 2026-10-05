"""Two-stage Camera 1 crop image analysis."""

from pathlib import Path
from typing import Any
import logging

from config import settings
from vision.dataset_lookup import DatasetLookup
from vision.image_validator import validate_image
from vision_models.classifier import CropDiseaseClassifier, DetectorCropDiseaseClassifier, UltralyticsCropDiseaseClassifier, UnavailableCropDiseaseClassifier
from vision_models.detector import ModelUnavailableError, PlantDetector, UltralyticsPlantDetector, UnavailablePlantDetector

logger = logging.getLogger(__name__)
EXPERT_MESSAGE = "No reliable result was found in the available CropConnect dataset. Please consult an agricultural expert."


class CropAnalyzer:
    def __init__(self, detector: PlantDetector, classifier: CropDiseaseClassifier, dataset: DatasetLookup):
        self.detector, self.classifier, self.dataset = detector, classifier, dataset

    def analyze(self, source: str | Path | bytes) -> dict[str, Any]:
        validation = validate_image(source, self.detector, confidence_threshold=settings.vision_crop_confidence_threshold, blur_threshold=settings.vision_blur_threshold, min_width=settings.vision_min_image_width, min_height=settings.vision_min_image_height, min_brightness=settings.vision_min_brightness)
        if not validation.valid:
            return {"valid_image": False, "result_found": False, "message": validation.message}
        try:
            classification = self.classifier.classify(validation.image)
        except ModelUnavailableError as exc:
            logger.warning("Crop classifier unavailable: %s", exc)
            return {"valid_image": True, "result_found": False, "source": "model_unavailable", "message": EXPERT_MESSAGE}
        if classification is None or classification.confidence < settings.vision_disease_confidence_threshold:
            return {"valid_image": True, "result_found": False, "confidence": classification.confidence if classification else None, "source": "low_confidence" if classification else "no_classification", "message": "The result is uncertain. Please consult an agricultural expert."}
        record = self.dataset.lookup(classification.crop_name, classification.disease_name)
        if record is None:
            return {"valid_image": True, "result_found": False, "crop": classification.crop_name, "condition": classification.disease_name, "confidence": classification.confidence, "source": "dataset_no_match", "message": EXPERT_MESSAGE}
        return {"valid_image": True, "result_found": True, "crop": record["crop_name"], "condition": record["disease_name"], "confidence": classification.confidence, "source": "dataset", "recommendation": record.get("recommendation"), "symptoms": record.get("symptoms"), "severity": record.get("severity"), "additional_information": record.get("additional_information"), "message": "A matching CropConnect dataset result was found."}


def _path_from_config(value: str) -> Path:
    path = Path(value)
    return path if path.is_absolute() else Path(__file__).resolve().parent / path


def build_crop_analyzer() -> CropAnalyzer:
    try:
        detector = UltralyticsPlantDetector(
            _path_from_config(settings.vision_yolo_model_path), settings.vision_crop_confidence_threshold
        )
    except ModelUnavailableError as exc:
        logger.warning("Crop validation model is unavailable: %s", exc)
        detector = UnavailablePlantDetector(str(exc))
    try:
        classifier = UltralyticsCropDiseaseClassifier(_path_from_config(settings.vision_classifier_model_path))
    except ModelUnavailableError as exc:
        if isinstance(detector, UnavailablePlantDetector):
            logger.warning("Crop disease model is unavailable: %s", exc)
            classifier = UnavailableCropDiseaseClassifier(str(exc))
        else:
            logger.warning("Crop disease classifier is unavailable; using the disease-labelled detector: %s", exc)
            classifier = DetectorCropDiseaseClassifier(detector)
    return CropAnalyzer(detector, classifier, DatasetLookup(_path_from_config(settings.vision_dataset_path)))
