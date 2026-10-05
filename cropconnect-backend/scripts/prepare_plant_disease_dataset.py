"""Create Ultralytics' images/labels split layout from the supplied dataset."""
from __future__ import annotations

import argparse
import shutil
from pathlib import Path

import yaml

from validate_plant_disease_dataset import IMAGE_SUFFIXES, labels_from, validate


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("dataset_path", type=Path)
    parser.add_argument("--output", type=Path, default=Path("data/prepared/plant_disease"))
    args = parser.parse_args()
    source, output = args.dataset_path.resolve(), args.output.resolve()
    report = validate(source)
    if not report["valid"]:
        raise SystemExit("Dataset validation failed; see validation report before preparing data.")
    split_map = {"train": "train", "test": "test"}
    for source_name, output_name in split_map.items():
        source_split = source / source_name
        if not source_split.exists():
            continue
        for image in source_split.iterdir():
            if image.suffix.casefold() not in IMAGE_SUFFIXES:
                continue
            image_target = output / "images" / output_name / image.name
            label_target = output / "labels" / output_name / image.with_suffix(".txt").name
            image_target.parent.mkdir(parents=True, exist_ok=True)
            label_target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(image, image_target)
            shutil.copy2(image.with_suffix(".txt"), label_target)
    labels = labels_from(source)
    yaml_path = output / "dataset.yaml"
    yaml_path.write_text(yaml.safe_dump({"path": str(output), "train": "images/train", "val": "images/test", "test": "images/test", "names": {index: label for index, label in enumerate(labels)}}, sort_keys=False), encoding="utf-8")
    print(yaml_path)


if __name__ == "__main__":
    main()
