# End-to-End Wine Quality Data Science Project

## Workflows -- ML Pipeline

1. Data ingestion
2. Data validation
3. Data transformation
4. Model training
5. Model evaluation

## Adding or changing a pipeline stage

1. Update `config/config.yaml`.
2. Update `schema.yaml`.
3. Update `params.yaml`.
4. Update the relevant entities in `src/datascience/entity/config_entity.py`.
5. Update the configuration manager in `src/datascience/config/configuration.py`.
6. Implement or update a component in `src/datascience/components/`.
7. Implement or update the stage pipeline in `src/datascience/pipeline/`.
8. Wire the stage into `main.py`.

## Project description

This repository contains an end-to-end machine-learning project for estimating
the sensory quality score of a wine from its physicochemical measurements. The
project combines a reproducible batch training pipeline, model and metric
tracking, and a small Flask web application for making predictions from a
browser form.

The prediction target is `quality`. It is not an input feature. The model
expects the following 11 numeric features, with the column names and order
matching the training data:

1. `fixed acidity`
2. `volatile acidity`
3. `citric acid`
4. `residual sugar`
5. `chlorides`
6. `free sulfur dioxide`
7. `total sulfur dioxide`
8. `density`
9. `pH`
10. `sulphates`
11. `alcohol`

### End-to-end workflow

The pipeline is orchestrated by `main.py`. It runs these stages in sequence:

1. **Data ingestion** -- downloads the wine-quality ZIP archive from the
   dataset URL in `config/config.yaml` if it is not already present, then
   extracts it under `artifacts/data_ingestion/`.
2. **Data validation** -- reads the configured CSV and checks that its columns
   match the expected schema. It also checks column data types. The expected
   columns, types, and target name are defined in `schema.yaml`; validation
   status is written to `artifacts/data_validation/status.txt`.
3. **Data transformation** -- reads the ingested CSV and creates a reproducible
   80/20 train/test split using `random_state=42`. The resulting files are
   `artifacts/data_transformation/train.csv` and `test.csv`.
4. **Model training** -- separates the `quality` target from the feature
   columns, fits a scikit-learn `ElasticNet` regressor, and serializes it with
   Joblib to `artifacts/model_trainer/model.joblib`. The `alpha` and
   `l1_ratio` hyperparameters are read from `params.yaml`.
5. **Model evaluation** -- loads the trained model and test set, calculates
   root mean squared error (RMSE), mean absolute error (MAE), and R-squared
   (R²), saves the scores to
   `artifacts/model_evaluation/metrics.json`, and logs parameters, metrics, and
   model information to MLflow.

### Web application and routes

`app.py` provides the Flask application. The current prediction interface is
an HTML form, not a JSON request/response API.

| Route | Method | Behavior |
|---|---|---|
| `/` | GET | Renders `templates/index.html` with one numeric input for each of the 11 model features. |
| `/predict` | GET | Renders the prediction form. |
| `/predict` | POST | Reads the submitted form fields, constructs a feature row, runs the trained model, and renders `templates/results.html` with the predicted quality score. Invalid or missing numeric inputs return the form with an error. |
| `/train` | GET | Runs `main.py` as a subprocess and returns a success response when the full pipeline completes. Failures are logged and return HTTP 500. |

Predictions require the trained model to exist at
`artifacts/model_trainer/model.joblib`. Run training before making predictions
if this file is not present. The `/train` endpoint starts ingestion, validation,
transformation, training, and evaluation; it is intended for a trusted
development environment and should be protected or disabled before exposing
the application to untrusted users.

### Tools, libraries, and services

| Area | Technology | Role in this project |
|---|---|---|
| Language | Python | Implements the training pipeline, model evaluation, and web application. |
| Data handling | pandas, NumPy | Reads CSV files, builds feature data, and supports numerical metric calculations. |
| Machine learning | scikit-learn | Splits the dataset, fits the `ElasticNet` regressor, and calculates regression metrics. |
| Model persistence | Joblib | Saves and reloads the locally trained scikit-learn model. |
| Configuration | YAML, PyYAML, `python-box` | Stores pipeline paths, schema, target definition, and model parameters in readable configuration files. |
| Web application | Flask, Jinja templates | Handles browser routes and renders the input and result pages. |
| Production web server | Gunicorn | Serves the Flask WSGI application in the container. |
| Experiment tracking and registry | MLflow | Records evaluation runs, parameters, metrics, and model versions. |
| Remote tracking service | DagsHub | Hosts the configured MLflow tracking and model registry endpoint. A DagsHub access token is required when the pipeline logs remotely. |
| Containerization | Docker | Packages the application, Python dependencies, templates, and trained model into an image. |
| Container base | Chainguard Python | Provides the development build stage and a minimal, non-root Python runtime stage. |
| Logging | Python `logging` | Writes pipeline and application logs to the console and the local `logs/` directory. |
| Dataset hosting | GitHub-hosted ZIP archive | Provides the source wine-quality data configured in `config/config.yaml`. |

The main development dependencies are listed in `requirements.txt`. The
container installs the API and training runtime dependencies from
`requirements-api.txt`; it does not install notebook-only tools.

### Configuration and generated artifacts

- `config/config.yaml` defines dataset URLs and input/output paths for each
  stage.
- `schema.yaml` defines expected data columns, their types, and the target
  column name.
- `params.yaml` defines the `ElasticNet` hyperparameters (`alpha` and
  `l1_ratio`).
- `src/datascience/entity/config_entity.py` defines typed configuration
  records passed from configuration to pipeline components.
- `src/datascience/config/configuration.py` loads the YAML files and constructs
  those records.
- `artifacts/` contains downloaded data, validation status, train/test data,
  the Joblib model, and evaluation metrics. These are generated runtime
  artifacts rather than source code.

The model is stored locally as `model.joblib`. MLflow may also serialize its
own logged or registered model in the format selected by the installed MLflow
version. The local Joblib model and the MLflow model artifact are separate
outputs.

### Container deployment

The `Dockerfile` uses a multi-stage build. It installs dependencies in
Chainguard's `python:latest-dev` image, then copies the application into
Chainguard's minimal `python:latest` runtime image. The final image runs as a
non-root user and starts Gunicorn on port `8080`. `.dockerignore` excludes the
local virtual environment, notebooks, logs, and secret files while retaining
the trained model required for prediction.

Build and run the image from the repository root:

```bash
docker build -t datascienceproject-api:local .
docker run --rm -p 8080:8080 datascienceproject-api:local
```

Open `http://localhost:8080` to use the prediction form. If `/train` is used
inside the container, provide the remote-tracking credentials at container
runtime rather than adding them to the Dockerfile or image. For example, with
the variables already exported in the shell:

```bash
docker run --rm -p 8080:8080 \
  -e MLFLOW_TRACKING_USERNAME \
  -e MLFLOW_TRACKING_PASSWORD \
  datascienceproject-api:local
```

Never commit access tokens or passwords. Rotate any credential that has been
exposed in source, notebook output, shell history, or a Git commit.