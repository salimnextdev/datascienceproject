import json
import pytest
import pandas as pd
from unittest.mock import patch, MagicMock
from pathlib import Path

from src.datascience.components.data_drift import DataDrift, TARGET_COLUMN, _MIN_INFERENCE_ROWS
from src.datascience.entity.config_entity import DataDriftConfig

FEATURE_COLS = [
    "fixed acidity", "volatile acidity", "citric acid", "residual sugar",
    "chlorides", "free sulfur dioxide", "total sulfur dioxide",
    "density", "pH", "sulphates", "alcohol",
]


def _make_csv(path, shift=0.0, n=100):
    df = pd.DataFrame({col: [float(i % 10) + shift for i in range(n)] for col in FEATURE_COLS})
    df[TARGET_COLUMN] = [5 + (i % 3) for i in range(n)]
    df.to_csv(path, index=False)


def _make_inference_log(path, shift=0.0, n=None):
    n = n or _MIN_INFERENCE_ROWS
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w") as f:
        for i in range(n):
            record = {col: float(i % 10) + shift for col in FEATURE_COLS}
            record["timestamp"] = "2025-01-15T10:00:00+00:00"
            f.write(json.dumps(record) + "\n")


@pytest.fixture
def config(tmp_path):
    train_csv = tmp_path / "train.csv"
    test_csv = tmp_path / "test.csv"
    _make_csv(train_csv)
    _make_csv(test_csv)
    return DataDriftConfig(
        root_dir=tmp_path,
        train_data_path=train_csv,
        test_data_path=test_csv,
        inference_log=tmp_path / "inference_log.jsonl",
        drift_report_json=tmp_path / "drift_report.json",
        drift_report_html=tmp_path / "drift_report.html",
        drift_threshold=0.3,
    )


def _mock_mlflow():
    m = MagicMock()
    m.start_run.return_value.__enter__ = MagicMock(return_value=None)
    m.start_run.return_value.__exit__ = MagicMock(return_value=False)
    return m


# ── output files ─────────────────────────────────────────────────────────────

@patch("src.datascience.components.data_drift.mlflow")
def test_drift_report_json_created(mock_mlflow, config):
    mock_mlflow.configure_mock(**_mock_mlflow().__dict__)
    DataDrift(config).run()
    assert config.drift_report_json.exists()


@patch("src.datascience.components.data_drift.mlflow")
def test_drift_report_html_created(mock_mlflow, config):
    mock_mlflow.configure_mock(**_mock_mlflow().__dict__)
    DataDrift(config).run()
    assert config.drift_report_html.exists()


@patch("src.datascience.components.data_drift.mlflow")
def test_drift_summary_keys(mock_mlflow, config):
    mock_mlflow.configure_mock(**_mock_mlflow().__dict__)
    summary = DataDrift(config).run()
    assert {"drifted_columns", "total_columns", "drift_share", "per_column", "current_data_source"} <= summary.keys()
    assert summary["total_columns"] == len(FEATURE_COLS)
    assert 0.0 <= summary["drift_share"] <= 1.0


# ── data source selection ─────────────────────────────────────────────────────

@patch("src.datascience.components.data_drift.mlflow")
def test_falls_back_to_test_csv_when_no_log(mock_mlflow, config):
    mock_mlflow.configure_mock(**_mock_mlflow().__dict__)
    summary = DataDrift(config).run()
    assert summary["current_data_source"] == "test_csv"


@patch("src.datascience.components.data_drift.mlflow")
def test_falls_back_to_test_csv_when_log_too_small(mock_mlflow, config):
    mock_mlflow.configure_mock(**_mock_mlflow().__dict__)
    _make_inference_log(config.inference_log, n=_MIN_INFERENCE_ROWS - 1)
    summary = DataDrift(config).run()
    assert summary["current_data_source"] == "test_csv"


@patch("src.datascience.components.data_drift.mlflow")
def test_uses_inference_log_when_sufficient_rows(mock_mlflow, config):
    mock_mlflow.configure_mock(**_mock_mlflow().__dict__)
    _make_inference_log(config.inference_log, n=_MIN_INFERENCE_ROWS)
    summary = DataDrift(config).run()
    assert summary["current_data_source"] == "inference_log"


# ── drift detection ───────────────────────────────────────────────────────────

@patch("src.datascience.components.data_drift.mlflow")
def test_no_drift_on_identical_data(mock_mlflow, config):
    mock_mlflow.configure_mock(**_mock_mlflow().__dict__)
    summary = DataDrift(config).run()
    assert summary["drifted_columns"] == 0


@patch("src.datascience.components.data_drift.mlflow")
def test_drift_detected_on_shifted_inference_log(mock_mlflow, config):
    mock_mlflow.configure_mock(**_mock_mlflow().__dict__)
    _make_inference_log(config.inference_log, shift=100.0, n=_MIN_INFERENCE_ROWS)
    summary = DataDrift(config).run()
    assert summary["drifted_columns"] > 0
    assert summary["current_data_source"] == "inference_log"
