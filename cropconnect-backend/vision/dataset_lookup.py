"""Verified crop/disease dataset access with one load per service instance."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


class DatasetUnavailableError(RuntimeError):
    """Raised when the configured dataset is missing or malformed."""


class DatasetLookup:
    def __init__(self, dataset_path: str | Path):
        path = Path(dataset_path)
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
            records = payload["records"]
            if not isinstance(records, list):
                raise ValueError("records must be a list")
            self._records = records
        except (OSError, json.JSONDecodeError, KeyError, TypeError, ValueError) as exc:
            raise DatasetUnavailableError(f"Crop disease dataset unavailable: {path}") from exc

    def lookup(self, crop_name: str, disease_name: str) -> dict[str, Any] | None:
        crop = crop_name.strip().casefold()
        disease = disease_name.strip().casefold()
        for record in self._records:
            if not isinstance(record, dict):
                continue
            if (
                str(record.get("crop_name", "")).strip().casefold() == crop
                and str(record.get("disease_name", "")).strip().casefold() == disease
            ):
                return dict(record)
        return None