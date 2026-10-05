"""Evaluate a trained crop detector and print measured Ultralytics metrics."""
from __future__ import annotations

import argparse
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("model", type=Path)
    parser.add_argument("--data", type=Path, default=Path("data/prepared/plant_disease/dataset.yaml"))
    parser.add_argument("--imgsz", type=int, default=416)
    parser.add_argument("--device", default="cpu")
    args = parser.parse_args()
    from ultralytics import YOLO
    metrics = YOLO(str(args.model)).val(data=str(args.data.resolve()), imgsz=args.imgsz, device=args.device, plots=True)
    print({"precision": metrics.box.mp, "recall": metrics.box.mr, "map50": metrics.box.map50, "map50_95": metrics.box.map})


if __name__ == "__main__":
    main()
