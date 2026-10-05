"""Run real YOLO inference against an image and retain all boxes/classes."""
from __future__ import annotations

import argparse
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("model", type=Path)
    parser.add_argument("image", type=Path)
    parser.add_argument("--confidence", type=float, default=0.5)
    args = parser.parse_args()
    from ultralytics import YOLO
    result = YOLO(str(args.model)).predict(str(args.image), conf=args.confidence, verbose=False)[0]
    for box in result.boxes:
        class_id = int(box.cls[0])
        print({"class_id": class_id, "class_name": result.names[class_id], "confidence": float(box.conf[0]), "box": [float(value) for value in box.xyxy[0].tolist()]})


if __name__ == "__main__":
    main()
