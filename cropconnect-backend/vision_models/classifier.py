"""Crop/disease classification adapters."""

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from vision_models.detector import ModelUnavailableError, PlantDetector


@dataclass(frozen=True)
class Classification:
    crop_name: str
    disease_name: str
    confidence: float


class CropDiseaseClassifier:
    def classify(self, image: Any) -> Classification | None:
        raise NotImplementedError


class UnavailableCropDiseaseClassifier(CropDiseaseClassifier):
    """Keeps the scan endpoint available when its optional model is absent."""

    def __init__(self, reason: str):
        self.reason = reason

    def classify(self, image: Any) -> Classification | None:
        raise ModelUnavailableError(self.reason)


# The PlantDisease416x416 detector used by CropConnect has disease-specific
# labels.  Until a separate YOLO classification checkpoint is deployed, these
# mappings let the scan feature use that trained detector without inventing a
# result.  Every target is represented in crop_disease_dataset.json.
DETECTOR_LABEL_CLASSIFICATIONS = {
    "apple scab leaf": ("Apple", "Scab"),
    "apple leaf": ("Apple", "Healthy"),
    "apple rust leaf": ("Apple", "Rust"),
    "bell pepper leaf": ("Bell Pepper", "Healthy"),
    "bell pepper leaf spot": ("Bell Pepper", "Leaf Spot"),
    "blueberry leaf": ("Blueberry", "Healthy"),
    "cherry leaf": ("Cherry", "Healthy"),
    "corn gray leaf spot": ("Corn", "Gray Leaf Spot"),
    "corn leaf blight": ("Corn", "Leaf Blight"),
    "corn rust leaf": ("Corn", "Rust"),
    "grape leaf": ("Grape", "Healthy"),
    "grape leaf black rot": ("Grape", "Black Rot"),
    "peach leaf": ("Peach", "Healthy"),
    "potato leaf": ("Potato", "Healthy"),
    "potato leaf early blight": ("Potato", "Early Blight"),
    "potato leaf late blight": ("Potato", "Late Blight"),
    "raspberry leaf": ("Raspberry", "Healthy"),
    "soyabean leaf": ("Soybean", "Healthy"),
    "soybean leaf": ("Soybean", "Healthy"),
    "squash powdery mildew leaf": ("Squash", "Powdery Mildew"),
    "strawberry leaf": ("Strawberry", "Healthy"),
    "tomato early blight leaf": ("Tomato", "Early Blight"),
    "tomato septoria leaf spot": ("Tomato", "Septoria Leaf Spot"),
    "tomato leaf": ("Tomato", "Healthy"),
    "tomato leaf bacterial spot": ("Tomato", "Bacterial Spot"),
    "tomato leaf late blight": ("Tomato", "Late Blight"),
    "tomato leaf mosaic virus": ("Tomato", "Mosaic Virus"),
    "tomato leaf yellow virus": ("Tomato", "Yellow Leaf Curl Virus"),
    "tomato mold leaf": ("Tomato", "Leaf Mold"),
    "tomato two spotted spider mites leaf": ("Tomato", "Two-Spotted Spider Mites"),
}


def classification_from_detector_label(label: str, confidence: float) -> Classification | None:
    normalized = " ".join(label.replace("_", " ").split()).casefold()
    result = DETECTOR_LABEL_CLASSIFICATIONS.get(normalized)
    return Classification(*result, confidence) if result else None


class DetectorCropDiseaseClassifier(CropDiseaseClassifier):
    """Classify a scan from disease-labelled detector results as a safe fallback."""

    def __init__(self, detector: PlantDetector):
        self._detector = detector

    def classify(self, image: Any) -> Classification | None:
        candidates = (
            classification_from_detector_label(detection.label, detection.confidence)
            for detection in self._detector.detect(image)
        )
        recognized = [candidate for candidate in candidates if candidate is not None]
        return max(recognized, key=lambda candidate: candidate.confidence, default=None)


class UltralyticsCropDiseaseClassifier(CropDiseaseClassifier):
    def __init__(self, model_path: str | Path):
        path = Path(model_path)
        if not path.is_file():
            raise ModelUnavailableError(f"Crop/disease classifier not found: {path}")
        try:
            from ultralytics import YOLO
        except ImportError as exc:
            raise ModelUnavailableError("Install ultralytics to use the crop/disease classifier") from exc
        self._model = YOLO(str(path))

    def classify(self, image: Any) -> Classification | None:
        try:
            result = self._model.predict(image, verbose=False)[0]
            if result.probs is None:
                return None
            class_id = int(result.probs.top1)
            label = str(result.names[class_id])
            crop_name, separator, disease_name = label.partition(":")
            if not separator:
                crop_name, _, disease_name = label.partition("/")
            if not disease_name:
                crop_name, _, disease_name = label.partition("__")
            return Classification(crop_name.strip(), disease_name.strip() or "Unknown", float(result.probs.top1conf))
        except Exception as exc:
            raise ModelUnavailableError(f"Crop/disease classification failed: {exc}") from exc
