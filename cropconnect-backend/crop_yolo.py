"""YOLO detection flow for the PlantDisease416x416 dataset."""
from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from config import settings
from vision.image_validator import validate_image
from vision_models.detector import ModelUnavailableError, PlantDetector, UltralyticsPlantDetector, UnavailablePlantDetector

_CROPS = ("Bell pepper", "Blueberry", "Cherry", "Corn", "Potato", "Raspberry", "Soyabean", "Soybean", "Squash", "Strawberry", "Tomato", "Apple", "Peach", "Grape")


def _model_path() -> Path:
    path = Path(settings.vision_yolo_model_path)
    return path if path.is_absolute() else Path(__file__).resolve().parent / path


def interpret_dataset_label(raw_label: str) -> dict[str, str]:
    """Derive display fields only from the YOLO dataset's original class label."""
    class_name = re.sub(r"\s+", " ", raw_label.replace("_", " ")).strip()
    label_lower = class_name.casefold()
    crop = next((item for item in _CROPS if label_lower.startswith(item.casefold())), "Unknown crop")
    tail = class_name[len(crop):].strip() if crop != "Unknown crop" else class_name
    condition = re.sub(r"\bleaf\b", "", tail, flags=re.IGNORECASE).strip(" -_").title() or "Leaf"
    return {"class_name": class_name, "crop": crop, "condition": condition}


class YoloCropAnalyzer:
    def __init__(self, detector: PlantDetector):
        self.detector = detector

    def analyze(self, content: bytes) -> dict[str, Any]:
        validation = validate_image(
            content,
            self.detector,
            confidence_threshold=settings.vision_crop_confidence_threshold,
            blur_threshold=settings.vision_blur_threshold,
            min_width=settings.vision_min_image_width,
            min_height=settings.vision_min_image_height,
            min_brightness=settings.vision_min_brightness,
        )
        quality = {"valid": validation.valid, "blur_score": validation.blur_score, "brightness": validation.brightness}
        if not validation.valid:
            return {"valid_image": False, "result_found": False, "image_quality": quality, "message": validation.message}

        detections = []
        for item in validation.detections:
            box = None
            if item.box:
                x1, y1, x2, y2 = item.box
                box = {"x1": x1, "y1": y1, "x2": x2, "y2": y2}
            detections.append({**interpret_dataset_label(item.label), "confidence": round(float(item.confidence), 6), "box": box})
        primary = max(detections, key=lambda item: item["confidence"])
        return {
            "valid_image": True,
            "result_found": True,
            "source": "yolo",
            "image_quality": quality,
            "detections": detections,
            "primary_result": primary,
            # Existing Crop Scan page compatibility.
            "crop": primary["crop"], "condition": primary["condition"],
            "confidence": primary["confidence"], "class_name": primary["class_name"],
            "message": "YOLO detected a supported crop or leaf class.",
        }


def build_yolo_crop_analyzer() -> YoloCropAnalyzer:
    try:
        return YoloCropAnalyzer(UltralyticsPlantDetector(_model_path(), settings.vision_crop_confidence_threshold))
    except ModelUnavailableError:
        # The endpoint remains healthy and tells the operator exactly what is
        # missing; no result is fabricated while the model is unavailable.
        return YoloCropAnalyzer(UnavailablePlantDetector("Crop detection model is not installed."))
