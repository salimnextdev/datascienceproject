import json
import pytest
import pandas as pd
import joblib

from src.datascience.components.model_trainer import ModelTrainer
from src.datascience.entity.config_entity import ModelTrainerConfig

FEATURE_COLS = [
    "fixed acidity", "volatile acidity", "citric acid", "residual sugar",
    "chlorides", "free sulfur dioxide", "total sulfur dioxide",
    "density", "pH", "sulphates", "alcohol",
]

# Minimal grids so tests run fast
PARAM_GRIDS = {
    "ElasticNet":       {"alpha": [0.1], "l1_ratio": [0.5]},
    "RandomForest":     {"n_estimators": [10], "max_depth": [3]},
    "GradientBoosting": {"n_estimators": [10], "learning_rate": [0.1], "max_depth": [3]},
}


def _make_csv(path, n=60):
    df = pd.DataFrame({col: [float(i % 10) for i in range(n)] for col in FEATURE_COLS})
    df["quality"] = [5 + (i % 3) for i in range(n)]
    df.to_csv(path, index=False)


@pytest.fixture
def config(tmp_path, monkeypatch):
    train_csv = tmp_path / "train.csv"
    test_csv = tmp_path / "test.csv"
    _make_csv(train_csv)
    _make_csv(test_csv, n=20)
    monkeypatch.setenv("MLFLOW_TRACKING_PASSWORD", "test-token")

    return ModelTrainerConfig(
        root_dir=tmp_path,
        train_data_path=train_csv,
        test_data_path=test_csv,
        model_name="model.joblib",
        param_grids=PARAM_GRIDS,
        target_column="quality",
        cv_folds=2,
        mlflow_uri="file:///tmp/mlruns",
    )


def test_model_file_created(config):
    ModelTrainer(config).train()
    assert (config.root_dir / "model.joblib").exists()


def test_selection_report_created(config):
    ModelTrainer(config).train()
    assert (config.root_dir / "model_selection.json").exists()


def test_selection_report_has_all_models(config):
    report = ModelTrainer(config).train()
    assert "ElasticNet" in report
    assert "RandomForest" in report
    assert "GradientBoosting" in report


def test_selection_report_has_winner(config):
    report = ModelTrainer(config).train()
    assert "winner" in report
    assert report["winner"] in ("ElasticNet", "RandomForest", "GradientBoosting")


def test_winner_is_lowest_test_rmse(config):
    report = ModelTrainer(config).train()
    winner = report["winner"]
    winner_rmse = report[winner]["test_rmse"]
    for name, result in report.items():
        if name == "winner":
            continue
        assert winner_rmse <= result["test_rmse"]


def test_saved_model_can_predict(config):
    ModelTrainer(config).train()
    model = joblib.load(config.root_dir / "model.joblib")
    sample = pd.DataFrame([{col: 5.0 for col in FEATURE_COLS}])
    preds = model.predict(sample)
    assert len(preds) == 1


def test_report_metrics_are_valid(config):
    report = ModelTrainer(config).train()
    for name in ("ElasticNet", "RandomForest", "GradientBoosting"):
        assert report[name]["cv_rmse"] > 0
        assert report[name]["test_rmse"] > 0
        assert -1.0 <= report[name]["test_r2"] <= 1.0
