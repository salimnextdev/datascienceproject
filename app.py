import json
from datetime import datetime, timezone
import os
from pathlib import Path

import pandas as pd
from flask import Flask, render_template, request

from src.datascience.pipeline.prediction_pipeline import PredictionPipeline

app = Flask(__name__)

FEATURES = [
    ("fixed acidity", "fixed_acidity", "Fixed acidity"),
    ("volatile acidity", "volatile_acidity", "Volatile acidity"),
    ("citric acid", "citric_acid", "Citric acid"),
    ("residual sugar", "residual_sugar", "Residual sugar"),
    ("chlorides", "chlorides", "Chlorides"),
    ("free sulfur dioxide", "free_sulfur_dioxide", "Free sulfur dioxide"),
    ("total sulfur dioxide", "total_sulfur_dioxide", "Total sulfur dioxide"),
    ("density", "density", "Density"),
    ("pH", "pH", "pH"),
    ("sulphates", "sulphates", "Sulphates"),
    ("alcohol", "alcohol", "Alcohol"),
]

_RANGES_PATH = Path("artifacts/data_transformation/feature_ranges.json")
_INFERENCE_LOG = Path("artifacts/data_drift/inference_log.jsonl")


def _load_ranges():
    if _RANGES_PATH.is_file():
        return json.loads(_RANGES_PATH.read_text())
    return None


def _validate_ranges(values: dict, ranges: dict) -> list[str]:
    warnings = []
    for col, val in values.items():
        if col in ranges:
            lo, hi = ranges[col]["min"], ranges[col]["max"]
            if not (lo <= val <= hi):
                warnings.append(f"{col} value {val} is outside training range [{lo:.4g}, {hi:.4g}].")
    return warnings


def _log_inference(values: dict) -> None:
    try:
        _INFERENCE_LOG.parent.mkdir(parents=True, exist_ok=True)
        record = {**values, "timestamp": datetime.now(timezone.utc).isoformat()}
        with open(_INFERENCE_LOG, "a") as f:
            f.write(json.dumps(record) + "\n")
    except Exception:
        app.logger.warning("Failed to write inference log", exc_info=True)


_S3_BUCKET = os.environ.get("INFERENCE_LOG_BUCKET")
_S3_KEY = "inference_log.jsonl"


def _sync_inference_log_to_s3() -> None:
    if not _S3_BUCKET:
        return
    try:
        import boto3
        boto3.client("s3").upload_file(str(_INFERENCE_LOG), _S3_BUCKET, _S3_KEY)
    except Exception:
        app.logger.warning("Failed to sync inference log to S3", exc_info=True)


@app.get("/")
def homepage():
    return render_template("index.html", features=FEATURES)


@app.route("/predict", methods=["GET", "POST"])
def predict():
    if request.method == "GET":
        return render_template("index.html", features=FEATURES)

    try:
        values = {
            column: float(request.form[field_name])
            for column, field_name, _ in FEATURES
        }
    except (KeyError, ValueError):
        return render_template(
            "index.html",
            features=FEATURES,
            error="Enter a valid number for every field.",
        ), 400

    range_warnings = _validate_ranges(values, _load_ranges() or {})

    try:
        data = pd.DataFrame([values], columns=[column for column, _, _ in FEATURES])
        prediction = PredictionPipeline().predict(data)
    except Exception:
        app.logger.exception("Prediction failed")
        return render_template(
            "index.html",
            features=FEATURES,
            error="Prediction failed. Make sure the model has been trained.",
        ), 500

    _log_inference(values)
    _sync_inference_log_to_s3()

    return render_template(
        "results.html",
        prediction=float(prediction[0]),
        warnings=range_warnings,
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
