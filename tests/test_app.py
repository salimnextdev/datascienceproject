import json
import pytest
import pandas as pd
import joblib
from pathlib import Path
from unittest.mock import patch
from sklearn.linear_model import ElasticNet

from app import app as flask_app, _validate_ranges, _load_ranges

FEATURE_COLS = [
    "fixed acidity", "volatile acidity", "citric acid", "residual sugar",
    "chlorides", "free sulfur dioxide", "total sulfur dioxide",
    "density", "pH", "sulphates", "alcohol",
]

SAMPLE_RANGES = {col: {"min": 0.0, "max": 10.0} for col in FEATURE_COLS}


# ── _validate_ranges ──────────────────────────────────────────────────────────

def test_validate_ranges_no_warnings_when_in_range():
    values = {col: 5.0 for col in FEATURE_COLS}
    assert _validate_ranges(values, SAMPLE_RANGES) == []


def test_validate_ranges_warns_when_out_of_range():
    values = {col: 5.0 for col in FEATURE_COLS}
    values["alcohol"] = 99.0
    warnings = _validate_ranges(values, SAMPLE_RANGES)
    assert len(warnings) == 1
    assert "alcohol" in warnings[0]


def test_validate_ranges_empty_when_no_ranges():
    values = {col: 5.0 for col in FEATURE_COLS}
    assert _validate_ranges(values, {}) == []


# ── Flask routes ──────────────────────────────────────────────────────────────

@pytest.fixture
def client(tmp_path):
    flask_app.config["TESTING"] = True
    with flask_app.test_client() as c:
        yield c


def test_homepage_returns_200(client):
    assert client.get("/").status_code == 200


def test_predict_get_returns_200(client):
    assert client.get("/predict").status_code == 200


def test_predict_post_missing_field_returns_400(client):
    resp = client.post("/predict", data={"fixed_acidity": "7.0"})
    assert resp.status_code == 400


def test_predict_post_invalid_value_returns_400(client):
    data = {field: "abc" for _, field, _ in flask_app.config.get("FEATURES", [
        ("fixed acidity", "fixed_acidity", ""),
        ("volatile acidity", "volatile_acidity", ""),
        ("citric acid", "citric_acid", ""),
        ("residual sugar", "residual_sugar", ""),
        ("chlorides", "chlorides", ""),
        ("free sulfur dioxide", "free_sulfur_dioxide", ""),
        ("total sulfur dioxide", "total_sulfur_dioxide", ""),
        ("density", "density", ""),
        ("pH", "pH", ""),
        ("sulphates", "sulphates", ""),
        ("alcohol", "alcohol", ""),
    ])}
    resp = client.post("/predict", data=data)
    assert resp.status_code == 400


def test_predict_post_valid_input(client, tmp_path, monkeypatch):
    model = ElasticNet()
    X = pd.DataFrame([{col: 5.0 for col in FEATURE_COLS}])
    y = [6.0]
    model.fit(X, y)

    model_path = tmp_path / "model.joblib"
    joblib.dump(model, model_path)

    monkeypatch.setattr(
        "app._RANGES_PATH", tmp_path / "feature_ranges.json"
    )

    with patch("app.PredictionPipeline") as MockPipeline:
        MockPipeline.return_value.predict.return_value = [5.8]
        data = {field: "5.0" for _, field, _ in [
            ("fixed acidity", "fixed_acidity", ""),
            ("volatile acidity", "volatile_acidity", ""),
            ("citric acid", "citric_acid", ""),
            ("residual sugar", "residual_sugar", ""),
            ("chlorides", "chlorides", ""),
            ("free sulfur dioxide", "free_sulfur_dioxide", ""),
            ("total sulfur dioxide", "total_sulfur_dioxide", ""),
            ("density", "density", ""),
            ("pH", "pH", ""),
            ("sulphates", "sulphates", ""),
            ("alcohol", "alcohol", ""),
        ]}
        resp = client.post("/predict", data=data)
    assert resp.status_code == 200
