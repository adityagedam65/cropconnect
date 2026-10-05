"""Camera 2 motion detection with filtering, optional person detection, and cooldown."""

import logging
import time
from dataclasses import dataclass
from typing import Any, Callable

from notifications.notifier import ConsoleNotifier, Notifier
from vision_models.detector import PlantDetector

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class MotionEvent:
    event: str
    timestamp: float
    confidence: float | None = None

    def as_dict(self) -> dict[str, Any]:
        result = {"event": self.event, "timestamp": self.timestamp}
        if self.confidence is not None:
            result["confidence"] = self.confidence
        return result


class MotionDetector:
    def __init__(self, threshold: int = 25, min_area: float = 1500.0):
        self.threshold, self.min_area, self._previous_gray = threshold, min_area, None

    def detect(self, frame: Any) -> bool:
        try:
            import cv2
            gray = cv2.GaussianBlur(cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY), (21, 21), 0)
        except ImportError:
            return False
        if self._previous_gray is None:
            self._previous_gray = gray
            return False
        delta = cv2.absdiff(self._previous_gray, gray)
        self._previous_gray = gray
        mask = cv2.dilate(cv2.threshold(delta, self.threshold, 255, cv2.THRESH_BINARY)[1], None, iterations=2)
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        return any(cv2.contourArea(contour) >= self.min_area for contour in contours)


class FieldMonitor:
    def __init__(self, capture: Any, motion_detector: MotionDetector, notifier: Notifier | None = None, person_detector: PlantDetector | None = None, cooldown_seconds: float = 60.0, person_confidence: float = 0.5, frame_interval_seconds: float = 0.1, clock: Callable[[], float] = time.monotonic):
        self.capture, self.motion_detector, self.notifier = capture, motion_detector, notifier or ConsoleNotifier()
        self.person_detector, self.cooldown_seconds, self.person_confidence = person_detector, cooldown_seconds, person_confidence
        self.frame_interval_seconds, self.clock, self._last_notification_at = frame_interval_seconds, clock, None

    def process_frame(self, frame: Any, now: float | None = None) -> dict[str, Any] | None:
        if not self.motion_detector.detect(frame):
            return None
        timestamp, event_name, confidence = self.clock() if now is None else now, "motion_detected", None
        if self.person_detector is not None:
            for detection in self.person_detector.detect(frame):
                if detection.label.casefold() == "person" and detection.confidence >= self.person_confidence:
                    event_name, confidence = "person_detected", detection.confidence
                    break
        if self._last_notification_at is not None and timestamp - self._last_notification_at < self.cooldown_seconds:
            return None
        event = MotionEvent(event_name, timestamp, confidence).as_dict()
        try:
            self.notifier.send_notification("Person detected in field" if event_name == "person_detected" else "Motion detected in field", "CropConnect detected activity in the monitored field.", event)
        except Exception:
            logger.exception("Field notification failed")
        self._last_notification_at = timestamp
        return event

    def run(self, stop_event: Any | None = None, max_frames: int | None = None) -> dict[str, Any]:
        try:
            import cv2
        except ImportError:
            return {"ok": False, "message": "OpenCV is required for field monitoring."}
        frames = 0
        try:
            if not self.capture.isOpened():
                return {"ok": False, "message": "Camera unavailable."}
            while max_frames is None or frames < max_frames:
                if stop_event is not None and stop_event.is_set():
                    break
                success, frame = self.capture.read()
                if not success or frame is None:
                    return {"ok": False, "frames": frames, "message": "Camera disconnected."}
                self.process_frame(frame)
                frames += 1
                if cv2.waitKey(1) & 0xFF == ord("q"):
                    break
                if self.frame_interval_seconds > 0:
                    time.sleep(self.frame_interval_seconds)
            return {"ok": True, "frames": frames, "message": "Field monitor stopped."}
        finally:
            self.capture.release()
            cv2.destroyAllWindows()


def start_field_monitor() -> dict[str, Any]:
    import cv2
    from config import settings
    from crop_analysis import _path_from_config
    from vision_models.detector import ModelUnavailableError, UltralyticsPlantDetector

    capture = cv2.VideoCapture(settings.camera_2_index)
    person_detector = None
    try:
        person_detector = UltralyticsPlantDetector(_path_from_config(settings.vision_yolo_model_path), settings.motion_detection_confidence)
    except ModelUnavailableError as exc:
        logger.warning("Optional person detector unavailable; motion-only mode: %s", exc)
    return FieldMonitor(capture, MotionDetector(settings.motion_threshold, settings.min_motion_area), cooldown_seconds=settings.motion_cooldown_seconds, person_detector=person_detector, person_confidence=settings.motion_detection_confidence, frame_interval_seconds=settings.motion_frame_interval_seconds).run()