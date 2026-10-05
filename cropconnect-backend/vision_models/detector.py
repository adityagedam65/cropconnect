"""Plant detection adapters. YOLO is optional until a trained artifact is supplied."""

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any


# Ultralytics otherwise attempts to create a profile-specific settings folder,
# which is not writable in some Windows service accounts. Keep its small
# runtime cache beside the backend instead.
os.environ.setdefault("YOLO_CONFIG_DIR", str(Path(__file__).resolve().parents[1] / ".ultralytics"))


class ModelUnavailableError(RuntimeError):
    """Raised when a configured model cannot be loaded or used."""


@dataclass(frozen=True)
class Detection:
    label: str
    confidence: float
    box: tuple[int, int, int, int] | None = None


class PlantDetector:
    def detect(self, image: Any) -> list[Detection]:
        raise NotImplementedError


class UnavailablePlantDetector(PlantDetector):
    """Defers a missing optional model error until image validation runs."""

    def __init__(self, reason: str):
        self.reason = reason

    def detect(self, image: Any) -> list[Detection]:
        raise ModelUnavailableError(self.reason)


class UltralyticsPlantDetector(PlantDetector):
    def __init__(self, model_path: str | Path, confidence: float = 0.5):
        path = Path(model_path)
        if not path.is_file():
            raise ModelUnavailableError(f"YOLO plant model not found: {path}")
        try:
            from ultralytics import YOLO
        except ImportError as exc:
            raise ModelUnavailableError("Install ultralytics to use the YOLO plant detector") from exc
        self._model = YOLO(str(path))
        self._confidence = confidence

    def detect(self, image: Any) -> list[Detection]:
        try:
            result = self._model.predict(image, conf=self._confidence, verbose=False)[0]
            detections = []
            for box in result.boxes:
                class_id = int(box.cls[0])
                coordinates = tuple(int(value) for value in box.xyxy[0].tolist())
                detections.append(Detection(str(result.names[class_id]), float(box.conf[0]), coordinates))
            return detections
        except Exception as exc:
            raise ModelUnavailableError(f"YOLO plant detection failed: {exc}") from exc
