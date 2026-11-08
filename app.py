import subprocess
import sys

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


@app.get("/")
def homepage():
    return render_template("index.html", features=FEATURES)


@app.get("/train")
def training():
    try:
        subprocess.run([sys.executable, "main.py"], check=True, capture_output=True, text=True)
    except subprocess.CalledProcessError as error:
        app.logger.error("Training failed: %s", error.stderr or error.stdout)
        return "Training failed. Check the application logs for details.", 500
    return "Training completed successfully."


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

    return render_template("results.html", prediction=float(prediction[0]))


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
