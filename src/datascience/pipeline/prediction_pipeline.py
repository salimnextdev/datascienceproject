import joblib
from pathlib import Path


class PredictionPipeline:
    def __init__(self):
        model_path = Path("artifacts/model_trainer/model.joblib")
        if not model_path.is_file():
            raise FileNotFoundError(
                f"Trained model not found at {model_path}. Run the training pipeline first."
            )
        self.model = joblib.load(model_path)

    def predict(self, data):
        return self.model.predict(data)
