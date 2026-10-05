"""OpenCV quality checks followed by plant detection."""

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from vision_models.detector import Detection, PlantDetector


@dataclass(frozen=True)
class ImageValidation:
    valid: bool
    message: str
    image: Any | None = None
    detections: tuple[Detection, ...] = ()
    blur_score: float | None = None
    brightness: float | None = None


def _read_image(source: str | Path | bytes) -> Any:
    try:
        import cv2
        import numpy as np
        image = cv2.imread(str(source)) if isinstance(source, (str, Path)) else cv2.imdecode(np.frombuffer(source, dtype=np.uint8), cv2.IMREAD_COLOR)
    except (ImportError, OSError, TypeError, ValueError) as exc:
        raise ValueError("OpenCV could not read the image") from exc
    if image is None:
        raise ValueError("The image is corrupt or uses an unsupported format")
    return image


def validate_image(source: str | Path | bytes, detector: PlantDetector, *, confidence_threshold: float = 0.5, blur_threshold: float = 40.0, min_width: int = 160, min_height: int = 160, min_brightness: float = 25.0) -> ImageValidation:
    try:
        import cv2
    except ImportError:
        return ImageValidation(False, "OpenCV is required for crop image validation.")
    try:
        image = _read_image(source)
    except ValueError as exc:
        return ImageValidation(False, str(exc))
    height, width = image.shape[:2]
    if width < min_width or height < min_height:
        return ImageValidation(False, "Please upload a higher-resolution crop or leaf photo.")
    grayscale = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    brightness = float(grayscale.mean())
    blur_score = float(cv2.Laplacian(grayscale, cv2.CV_64F).var())
    if brightness < min_brightness:
        return ImageValidation(False, "The image is too dark. Please upload a well-lit crop or leaf photo.", image, (), blur_score, brightness)
    if blur_score < blur_threshold:
        return ImageValidation(False, "The image is too blurry. Please upload a sharper crop or leaf photo.", image, (), blur_score, brightness)
    try:
        detections = tuple(detector.detect(image))
    except Exception:
        return ImageValidation(
            False,
            "Crop detection model is not installed.", image, (), blur_score, brightness,
        )
    plant_detections = tuple(detection for detection in detections if detection.confidence >= confidence_threshold and _is_plant_label(detection.label))
    if not plant_detections:
        return ImageValidation(False, "No supported plant/leaf detected. Please capture a clear image of the crop or affected leaf.", image, detections, blur_score, brightness)
    return ImageValidation(True, "Crop image accepted.", image, plant_detections, blur_score, brightness)


def _is_plant_label(label: str) -> bool:
    normalized = label.casefold().replace("_", " ")
    return "leaf" in normalized
