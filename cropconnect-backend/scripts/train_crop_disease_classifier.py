"""Prepare a YOLO classification split and fine-tune YOLOv8n-cls.

The source dataset is annotated for detection.  Each source image has one
plant-disease annotation, so its image can also be deterministically placed in
the corresponding classification directory.  This script deliberately does
not overwrite a production artifact until Ultralytics has written `best.pt`.
"""
from __future__ import annotations

import argparse
import shutil
from pathlib import Path

import yaml


def classifier_label(detector_label: str) -> str:
    normalized = " ".join(detector_label.replace("_", " ").split())
    mappings = (
        ("Apple Scab Leaf", "Apple: Scab"), ("Apple leaf", "Apple: Healthy"),
        ("Apple rust leaf", "Apple: Rust"), ("Bell pepper leaf spot", "Bell Pepper: Leaf Spot"),
        ("Bell pepper leaf", "Bell Pepper: Healthy"), ("Blueberry leaf", "Blueberry: Healthy"),
        ("Cherry leaf", "Cherry: Healthy"), ("Corn Gray leaf spot", "Corn: Gray Leaf Spot"),
        ("Corn leaf blight", "Corn: Leaf Blight"), ("Corn rust leaf", "Corn: Rust"),
        ("Peach leaf", "Peach: Healthy"), ("Potato leaf early blight", "Potato: Early Blight"),
        ("Potato leaf late blight", "Potato: Late Blight"), ("Potato leaf", "Potato: Healthy"),
        ("Raspberry leaf", "Raspberry: Healthy"), ("Soyabean leaf", "Soybean: Healthy"),
        ("Soybean leaf", "Soybean: Healthy"), ("Squash Powdery mildew leaf", "Squash: Powdery Mildew"),
        ("Strawberry leaf", "Strawberry: Healthy"), ("Tomato Early blight leaf", "Tomato: Early Blight"),
        ("Tomato Septoria leaf spot", "Tomato: Septoria Leaf Spot"), ("Tomato leaf bacterial spot", "Tomato: Bacterial Spot"),
        ("Tomato leaf late blight", "Tomato: Late Blight"), ("Tomato leaf mosaic virus", "Tomato: Mosaic Virus"),
        ("Tomato leaf yellow virus", "Tomato: Yellow Leaf Curl Virus"), ("Tomato mold leaf", "Tomato: Leaf Mold"),
        ("Tomato two spotted spider mites leaf", "Tomato: Two-Spotted Spider Mites"), ("Tomato leaf", "Tomato: Healthy"),
        ("grape leaf black rot", "Grape: Black Rot"), ("grape leaf", "Grape: Healthy"),
    )
    folded = normalized.casefold()
    for source, target in mappings:
        if folded == source.casefold():
            return target
    raise ValueError(f"No classifier label mapping for {detector_label!r}")


def prepare(source: Path, output: Path) -> tuple[set[str], int]:
    metadata = yaml.safe_load((source / "dataset.yaml").read_text(encoding="utf-8"))
    names = {int(index): name for index, name in metadata["names"].items()}
    labels: set[str] = set()
    skipped = 0
    for split, destination in (("train", "train"), ("test", "val")):
        for image in (source / "images" / split).iterdir():
            if image.suffix.casefold() not in {".jpg", ".jpeg", ".png"}:
                continue
            annotation = source / "labels" / split / f"{image.stem}.txt"
            tokens = annotation.read_text(encoding="utf-8").split(maxsplit=1)
            if not tokens:
                skipped += 1
                continue
            class_id = int(tokens[0])
            label = classifier_label(str(names[class_id]))
            labels.add(label)
            # Windows forbids ':' in a directory name. The classifier adapter
            # converts this portable separator back to Crop: Disease.
            target = output / destination / label.replace(": ", "__") / image.name
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(image, target)
    return labels, skipped


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=Path, default=Path("data/prepared/plant_disease"))
    parser.add_argument("--data", type=Path, default=Path("data/prepared/plant_disease_classification"))
    parser.add_argument("--model", default="yolov8n-cls.pt")
    parser.add_argument("--epochs", type=int, default=40)
    parser.add_argument("--imgsz", type=int, default=224)
    parser.add_argument("--batch", type=int, default=16)
    parser.add_argument("--device", default="cpu")
    parser.add_argument("--project", default="runs/crop_disease_classifier")
    parser.add_argument("--name", default="yolov8n-cls-224")
    args = parser.parse_args()
    labels, skipped = prepare(args.source.resolve(), args.data.resolve())
    if len(labels) < 2:
        raise SystemExit("The classification split needs at least two classes.")
    if skipped:
        print(f"Skipped {skipped} image(s) with empty detection annotations.")
    from ultralytics import YOLO
    result = YOLO(args.model).train(data=str(args.data.resolve()), epochs=args.epochs, imgsz=args.imgsz,
                                    batch=args.batch, device=args.device, project=args.project, name=args.name,
                                    pretrained=True, patience=10, plots=True)
    print(result.save_dir)


if __name__ == "__main__":
    main()
