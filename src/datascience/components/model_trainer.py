import json
import os
from pathlib import Path

import joblib
import mlflow
import mlflow.sklearn
import numpy as np
import pandas as pd
from sklearn.ensemble import GradientBoostingRegressor, RandomForestRegressor
from sklearn.linear_model import ElasticNet
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.model_selection import GridSearchCV
from urllib.parse import urlparse

from src.datascience import logger
from src.datascience.entity.config_entity import ModelTrainerConfig

_MODELS = {
    "ElasticNet": ElasticNet(random_state=42),
    "RandomForest": RandomForestRegressor(random_state=42),
    "GradientBoosting": GradientBoostingRegressor(random_state=42),
}


class ModelTrainer:
    def __init__(self, config: ModelTrainerConfig):
        self.config = config

    def train(self) -> dict:
        train_data = pd.read_csv(self.config.train_data_path)
        test_data = pd.read_csv(self.config.test_data_path)

        train_x = train_data.drop([self.config.target_column], axis=1)
        train_y = train_data[self.config.target_column]
        test_x = test_data.drop([self.config.target_column], axis=1)
        test_y = test_data[self.config.target_column]

        os.environ.setdefault("MLFLOW_TRACKING_USERNAME", "salimnextdev")
        if not os.environ.get("MLFLOW_TRACKING_PASSWORD"):
            raise RuntimeError(
                "MLFLOW_TRACKING_PASSWORD is not set. Export your DagsHub token before running."
            )

        mlflow.set_tracking_uri(self.config.mlflow_uri)
        mlflow.set_registry_uri(self.config.mlflow_uri)
        tracking_uri_type = urlparse(mlflow.get_tracking_uri()).scheme

        results = {}

        for name, estimator in _MODELS.items():
            param_grid = dict(self.config.param_grids.get(name, {}))
            logger.info("Tuning %s with grid: %s", name, param_grid)

            search = GridSearchCV(
                estimator=estimator,
                param_grid=param_grid,
                cv=self.config.cv_folds,
                scoring="neg_root_mean_squared_error",
                n_jobs=-1,
                refit=True,
            )
            search.fit(train_x, train_y)

            best_model = search.best_estimator_
            cv_rmse = -search.best_score_
            test_preds = best_model.predict(test_x)
            test_rmse = np.sqrt(mean_squared_error(test_y, test_preds))
            test_r2 = r2_score(test_y, test_preds)

            results[name] = {
                "model": best_model,
                "best_params": search.best_params_,
                "cv_rmse": cv_rmse,
                "test_rmse": test_rmse,
                "test_r2": test_r2,
            }

            with mlflow.start_run(run_name=name):
                mlflow.log_params(search.best_params_)
                mlflow.log_metric("cv_rmse", cv_rmse)
                mlflow.log_metric("test_rmse", test_rmse)
                mlflow.log_metric("test_r2", test_r2)
                if tracking_uri_type != "file":
                    mlflow.sklearn.log_model(best_model, "model", registered_model_name=name)
                else:
                    mlflow.sklearn.log_model(best_model, "model")

            logger.info("%s — CV RMSE: %.4f  Test RMSE: %.4f  R²: %.4f",
                        name, cv_rmse, test_rmse, test_r2)

        winner = min(results, key=lambda n: results[n]["test_rmse"])
        best = results[winner]

        joblib.dump(best["model"], Path(self.config.root_dir) / self.config.model_name)

        selection_report = {
            name: {
                "best_params": r["best_params"],
                "cv_rmse": r["cv_rmse"],
                "test_rmse": r["test_rmse"],
                "test_r2": r["test_r2"],
            }
            for name, r in results.items()
        }
        selection_report["winner"] = winner

        report_path = Path(self.config.root_dir) / "model_selection.json"
        with open(report_path, "w") as f:
            json.dump(selection_report, f, indent=2)

        logger.info("Winner: %s (Test RMSE: %.4f, R²: %.4f)",
                    winner, best["test_rmse"], best["test_r2"])

        return selection_report
