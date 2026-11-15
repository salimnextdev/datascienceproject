import json
import os
from pathlib import Path

import joblib
import mlflow
import mlflow.sklearn
import numpy as np
import pandas as pd
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from urllib.parse import urlparse

from src.datascience.entity.config_entity import ModelEvaluationConfig
from src.datascience.utils.common import save_json


class ModelEvaluation:
    def __init__(self, config: ModelEvaluationConfig):
        self.config = config

    def eval_metrics(self, actual, pred):
        rmse = np.sqrt(mean_squared_error(actual, pred))
        mae = mean_absolute_error(actual, pred)
        r2 = r2_score(actual, pred)
        return rmse, mae, r2

    def _winner_name(self) -> str:
        report = Path(self.config.model_path).parent / "model_selection.json"
        if report.exists():
            return json.loads(report.read_text()).get("winner", "BestModel")
        return "BestModel"

    def log_into_mlflow(self):
        test_data = pd.read_csv(self.config.test_data_path)
        model = joblib.load(self.config.model_path)

        test_x = test_data.drop([self.config.target_column], axis=1)
        test_y = test_data[self.config.target_column]

        os.environ.setdefault("MLFLOW_TRACKING_USERNAME", "salimnextdev")
        if not os.environ.get("MLFLOW_TRACKING_PASSWORD"):
            raise RuntimeError(
                "MLFLOW_TRACKING_PASSWORD is not set. Export your DagsHub access token "
                "in the shell before running python main.py."
            )

        mlflow.set_tracking_uri(self.config.mlflow_uri)
        mlflow.set_registry_uri(self.config.mlflow_uri)
        tracking_uri_type_store = urlparse(mlflow.get_tracking_uri()).scheme

        with mlflow.start_run(run_name="final_evaluation"):
            predicted_qualities = model.predict(test_x)
            rmse, mae, r2 = self.eval_metrics(test_y, predicted_qualities)

            scores = {"rmse": rmse, "mae": mae, "r2_score": r2}
            save_json(path=Path(self.config.metric_file_name), data=scores)

            mlflow.log_metric("rmse", rmse)
            mlflow.log_metric("r2", r2)
            mlflow.log_metric("mae", mae)
            mlflow.log_artifact(str(self.config.model_path), artifact_path="joblib_model")

            registered_name = self._winner_name()
            if tracking_uri_type_store != "file":
                mlflow.sklearn.log_model(model, "model", registered_model_name=registered_name)
            else:
                mlflow.sklearn.log_model(model, "model")