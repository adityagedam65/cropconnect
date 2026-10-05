"""Train the real PlantDisease416x416 YOLO detector."""
from __future__ import annotations

import argparse
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", type=Path, default=Path("data/prepared/plant_disease/dataset.yaml"))
    parser.add_argument("--model", default="yolov8n.pt", help="Ultralytics base detector or checkpoint")
    parser.add_argument("--epochs", type=int, default=40)
    parser.add_argument("--imgsz", type=int, default=416)
    parser.add_argument("--batch", type=int, default=8)
    parser.add_argument("--device", default="cpu")
    parser.add_argument("--project", default="runs/plant_detector")
    parser.add_argument("--name", default="yolov8n-416")
    args = parser.parse_args()
    try:
        from ultralytics import YOLO
    except ImportError as exc:
        raise SystemExit("Ultralytics is required. Install backend requirements before training.") from exc
    result = YOLO(args.model).train(
        data=str(args.data.resolve()), epochs=args.epochs, imgsz=args.imgsz,
        batch=args.batch, device=args.device, project=args.project, name=args.name,
        pretrained=True, patience=10, plots=True,
    )
    print(result.save_dir)


if __name__ == "__main__":
    main()
