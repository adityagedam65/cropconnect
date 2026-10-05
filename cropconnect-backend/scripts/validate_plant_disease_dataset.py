"""Validate YOLO image/annotation pairs and write a repeatable JSON report."""
from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path

IMAGE_SUFFIXES = {".jpg", ".jpeg", ".png", ".webp"}


def labels_from(root: Path) -> list[str]:
    files = list(root.rglob("_darknet.labels"))
    if not files:
        raise FileNotFoundError(f"No _darknet.labels file found under {root}")
    labels = [line.strip() for line in files[0].read_text(encoding="utf-8").splitlines() if line.strip()]
    if not labels:
        raise ValueError("The class-label file is empty")
    return labels


def validate(root: Path) -> dict:
    labels = labels_from(root)
    images = sorted(path for path in root.rglob("*") if path.suffix.casefold() in IMAGE_SUFFIXES)
    missing_labels, malformed, orphan_labels, class_counts = [], [], [], Counter()
    image_stems = {path.with_suffix("") for path in images}
    for image in images:
        label = image.with_suffix(".txt")
        if not label.exists():
            missing_labels.append(str(image.relative_to(root)))
            continue
        for line_no, line in enumerate(label.read_text(encoding="utf-8").splitlines(), 1):
            parts = line.split()
            try:
                if len(parts) != 5:
                    raise ValueError("expected five values")
                class_id = int(parts[0])
                values = [float(value) for value in parts[1:]]
                if not 0 <= class_id < len(labels):
                    raise ValueError(f"class id {class_id} is outside 0..{len(labels) - 1}")
                x, y, width, height = values
                if not (0 <= x <= 1 and 0 <= y <= 1 and 0 < width <= 1 and 0 < height <= 1):
                    raise ValueError("YOLO coordinates must be normalized and width/height positive")
                class_counts[class_id] += 1
            except ValueError as exc:
                malformed.append({"file": str(label.relative_to(root)), "line": line_no, "error": str(exc)})
    for label in root.rglob("*.txt"):
        if label.name != "_darknet.labels" and label.with_suffix("") not in image_stems:
            orphan_labels.append(str(label.relative_to(root)))
    return {
        "dataset": str(root), "class_count": len(labels), "classes": labels,
        "image_count": len(images), "annotation_count_by_class": {labels[key]: class_counts[key] for key in range(len(labels))},
        "missing_labels": missing_labels, "orphan_labels": orphan_labels, "malformed_annotations": malformed,
        "valid": not (missing_labels or orphan_labels or malformed),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("dataset_path", type=Path)
    parser.add_argument("--report", type=Path, default=Path("data/reports/plant_disease_dataset_report.json"))
    args = parser.parse_args()
    report = validate(args.dataset_path.resolve())
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps({key: report[key] for key in ("image_count", "class_count", "valid", "missing_labels", "orphan_labels", "malformed_annotations")}, indent=2))
    if not report["valid"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
