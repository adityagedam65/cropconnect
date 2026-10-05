"""Train CropConnect's crop classifier from the public benchmark dataset."""

from __future__ import annotations

import json
import logging
from pathlib import Path

import joblib
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix, precision_recall_fscore_support
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from xgboost import XGBClassifier


logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

BASE_DIR = Path(__file__).resolve().parents[1]
DATA_PATH = BASE_DIR / "data" / "crop_recommendation.csv"
MODEL_DIR = BASE_DIR / "data" / "models"
MODEL_PATH = MODEL_DIR / "crop_random_forest.joblib"
METRICS_PATH = MODEL_DIR / "crop_random_forest_metrics.json"
XGBOOST_MODEL_PATH = MODEL_DIR / "crop_xgboost.joblib"
COMPARISON_PATH = MODEL_DIR / "model_comparison.json"
FEATURES = ["N", "P", "K", "temperature", "humidity", "ph"]
LABEL = "label"
RANDOM_STATE = 42


def model_metrics(model, X_test: pd.DataFrame, y_test: pd.Series, *, classes: list[str] | None = None) -> dict:
    """Calculate the shared, serialisable validation metrics for either candidate."""
    predictions = model.predict(X_test)
    if classes is not None:
        predictions = [classes[int(value)] for value in predictions]
    accuracy = accuracy_score(y_test, predictions)
    precision, recall, f1, _ = precision_recall_fscore_support(
        y_test, predictions, average="macro", zero_division=0
    )
    labels = classes or model.classes_.tolist()
    return {
        "accuracy": accuracy,
        "macro_precision": precision,
        "macro_recall": recall,
        "macro_f1": f1,
        "classification_report": classification_report(y_test, predictions, output_dict=True, zero_division=0),
        "confusion_matrix": confusion_matrix(y_test, predictions, labels=labels).tolist(),
        "classes": labels,
    }


def main() -> None:
    data = pd.read_csv(DATA_PATH)
    required_columns = FEATURES + [LABEL]
    missing_columns = sorted(set(required_columns) - set(data.columns))
    if missing_columns:
        raise ValueError(f"Dataset is missing required columns: {', '.join(missing_columns)}")

    before = len(data)
    data = data.dropna(subset=required_columns)
    logger.info("Dropped %d rows with missing required values.", before - len(data))

    # Rainfall is a seasonal dataset figure, not a live comparable observation.
    # It is intentionally excluded to avoid corrupting live predictions.
    X = data[FEATURES]
    y = data[LABEL]
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, stratify=y, random_state=RANDOM_STATE
    )
    model = RandomForestClassifier(n_estimators=200, random_state=RANDOM_STATE, n_jobs=-1)
    model.fit(X_train, y_train)
    random_forest_metrics = model_metrics(model, X_test, y_test)

    # XGBoost requires contiguous integer class labels. The encoder is only a
    # training/evaluation adapter; production stays on the RF model unless the
    # measured macro-F1 improvement clears the explicit selection threshold.
    encoder = LabelEncoder().fit(y_train)
    xgb_model = XGBClassifier(
        objective="multi:softprob", eval_metric="mlogloss", n_estimators=300,
        learning_rate=0.08, max_depth=6, subsample=0.9, colsample_bytree=0.9,
        random_state=RANDOM_STATE, n_jobs=-1, tree_method="hist",
    )
    xgb_model.fit(X_train, encoder.transform(y_train))
    xgboost_metrics = model_metrics(xgb_model, X_test, y_test, classes=encoder.classes_.tolist())

    MODEL_DIR.mkdir(parents=True, exist_ok=True)
    joblib.dump(model, MODEL_PATH)
    joblib.dump({"model": xgb_model, "label_classes": encoder.classes_.tolist()}, XGBOOST_MODEL_PATH)
    metrics = {
        "dataset_note": "Trained on a public benchmark dataset, not CropConnect's own field data.",
        "training_rows": int(len(X_train)),
        "test_rows": int(len(X_test)),
        "features": FEATURES,
        "excluded_feature": "rainfall (seasonal dataset figure; not comparable to live input)",
        "random_state": RANDOM_STATE,
        **random_forest_metrics,
        "feature_importances": dict(zip(FEATURES, model.feature_importances_.tolist())),
    }
    METRICS_PATH.write_text(json.dumps(metrics, indent=2), encoding="utf-8")

    difference = xgboost_metrics["macro_f1"] - random_forest_metrics["macro_f1"]
    selected_model = "crop-xgboost-v1" if difference > 0.01 else "crop-random-forest-v1"
    justification = (
        "XGBoost macro F1 exceeded Random Forest by more than 0.01."
        if selected_model == "crop-xgboost-v1"
        else "Random Forest remains primary because XGBoost did not exceed its macro F1 by more than 0.01."
    )
    COMPARISON_PATH.write_text(json.dumps({
        "dataset_note": "Trained on a public benchmark dataset, not CropConnect's own field data.",
        "features": FEATURES,
        "excluded_feature": "rainfall (seasonal dataset figure; not comparable to live input)",
        "random_state": RANDOM_STATE,
        "random_forest": random_forest_metrics,
        "xgboost": xgboost_metrics,
        "macro_f1_difference_xgboost_minus_random_forest": difference,
        "selected_model": selected_model,
        "justification": justification,
    }, indent=2), encoding="utf-8")

    for name, result in (("Random Forest", random_forest_metrics), ("XGBoost", xgboost_metrics)):
        print(f"{name} accuracy: {result['accuracy']:.4f}")
        print(f"{name} macro precision: {result['macro_precision']:.4f}")
        print(f"{name} macro recall: {result['macro_recall']:.4f}")
        print(f"{name} macro F1: {result['macro_f1']:.4f}")
    print(f"Selected model: {selected_model}. {justification}")


if __name__ == "__main__":
    main()
