import json
import pandas as pd
import mlflow
from evidently.report import Report
from evidently.metric_preset import DataDriftPreset

from src.datascience import logger
from src.datascience.entity.config_entity import DataDriftConfig

TARGET_COLUMN = "quality"
_MIN_INFERENCE_ROWS = 30


class DataDrift:
    def __init__(self, config: DataDriftConfig):
        self.config = config

    def _load_current(self) -> tuple[pd.DataFrame, str]:
        """Return (current_data, source_label). Prefers inference log over test.csv."""
        log = self.config.inference_log
        if log.exists() and log.stat().st_size > 0:
            df = pd.read_json(log, lines=True).drop(
                columns=["timestamp", TARGET_COLUMN], errors="ignore"
            )
            if len(df) >= _MIN_INFERENCE_ROWS:
                logger.info("Drift: using inference log (%d rows)", len(df))
                return df, "inference_log"
            logger.info(
                "Drift: inference log has only %d rows (< %d), falling back to test.csv",
                len(df), _MIN_INFERENCE_ROWS,
            )
        return (
            pd.read_csv(self.config.test_data_path).drop(columns=[TARGET_COLUMN], errors="ignore"),
            "test_csv",
        )

    def run(self) -> dict:
        train = pd.read_csv(self.config.train_data_path).drop(columns=[TARGET_COLUMN], errors="ignore")
        current, source = self._load_current()

        report = Report(metrics=[DataDriftPreset()])
        report.run(reference_data=train, current_data=current)

        report.save_html(str(self.config.drift_report_html))

        result = report.as_dict()
        drift_summary = result["metrics"][0]["result"]
        drifted = drift_summary["number_of_drifted_columns"]
        total = drift_summary["number_of_columns"]
        share = drift_summary["share_of_drifted_columns"]

        per_column = {
            m["result"]["column_name"]: m["result"]["drift_detected"]
            for m in result["metrics"][1:]
            if "column_name" in m.get("result", {})
        }

        summary = {
            "drifted_columns": drifted,
            "total_columns": total,
            "drift_share": share,
            "per_column": per_column,
            "current_data_source": source,
        }

        with open(self.config.drift_report_json, "w") as f:
            json.dump(summary, f, indent=2)

        logger.info("Drift report: %d/%d columns drifted (%.2f%%) [source: %s]", drifted, total, share * 100, source)

        with mlflow.start_run(run_name="data_drift"):
            mlflow.log_metric("drifted_columns", drifted)
            mlflow.log_metric("total_columns", total)
            mlflow.log_metric("drift_share", share)
            mlflow.log_param("current_data_source", source)
            mlflow.log_artifact(str(self.config.drift_report_html), artifact_path="drift")
            mlflow.log_artifact(str(self.config.drift_report_json), artifact_path="drift")

        return summary
