PYTHON     := venv/bin/python
PIP        := venv/bin/pip
PYTEST     := venv/bin/pytest
FLASK_APP  := app.py
IMAGE_NAME := datascienceproject-api
IMAGE_TAG  := local
PORT       := 8080

.DEFAULT_GOAL := help

# ── Help ──────────────────────────────────────────────────────────────────────
.PHONY: help
help:
	@echo ""
	@echo "  Wine Quality MLOps Project"
	@echo ""
	@echo "  Setup"
	@echo "    make install          Install all dependencies into venv"
	@echo "    make install-api      Install API-only dependencies (mirrors container)"
	@echo ""
	@echo "  Data Science"
	@echo "    make ingest           Run data ingestion stage"
	@echo "    make validate         Run data validation stage"
	@echo "    make transform        Run data transformation stage"
	@echo "    make train            Run model training stage"
	@echo "    make evaluate         Run model evaluation stage"
	@echo "    make drift            Run data drift detection stage"
	@echo "    make pipeline         Run the full ML pipeline (all 6 stages)"
	@echo ""
	@echo "  Quality"
	@echo "    make test             Run pytest with coverage"
	@echo "    make lint             Run flake8"
	@echo "    make check            lint + test"
	@echo ""
	@echo "  App"
	@echo "    make serve            Start Flask dev server on port $(PORT)"
	@echo ""
	@echo "  Docker"
	@echo "    make docker-build     Build the Docker image"
	@echo "    make docker-run       Run the container on port $(PORT)"
	@echo "    make docker-stop      Stop the running container"
	@echo ""
	@echo "  DVC"
	@echo "    make dvc-pull         Pull artifacts from DVC remote"
	@echo "    make dvc-push         Push artifacts to DVC remote"
	@echo "    make dvc-status       Show DVC artifact status"
	@echo ""
	@echo "  Cleanup"
	@echo "    make clean            Remove artifacts, logs, and cache"
	@echo "    make clean-venv       Remove the virtual environment"
	@echo ""

# ── Setup ─────────────────────────────────────────────────────────────────────
.PHONY: install
install: venv
	$(PIP) install --upgrade pip
	$(PIP) install -r requirements.txt

.PHONY: install-api
install-api: venv
	$(PIP) install --upgrade pip
	$(PIP) install -r requirements-api.txt

venv:
	python3 -m venv venv

# ── Pipeline stages ───────────────────────────────────────────────────────────
.PHONY: ingest
ingest:
	$(PYTHON) -c "\
from src.datascience.pipeline.data_ingestion_pipeline import DataIngestionTrainingPipeline; \
DataIngestionTrainingPipeline().initiate_data_ingestion()"

.PHONY: validate
validate:
	$(PYTHON) -c "\
from src.datascience.pipeline.data_validation_pipeline import DataValidationTrainingPipeline; \
DataValidationTrainingPipeline().initiate_data_validation()"

.PHONY: transform
transform:
	$(PYTHON) -c "\
from src.datascience.pipeline.data_transformation_pipeline import DataTransformationTrainingPipeline; \
DataTransformationTrainingPipeline().initiate_data_transformation()"

.PHONY: train
train:
	$(PYTHON) -c "\
from src.datascience.pipeline.model_trainer_pipeline import ModelTrainerTrainingPipeline; \
report = ModelTrainerTrainingPipeline().initiate_model_trainer(); \
print('\\nModel selection results:'); \
[print(f'  {k}: RMSE={v[\"test_rmse\"]:.4f}  R2={v[\"test_r2\"]:.4f}') for k,v in report.items() if k != 'winner']; \
print(f'  Winner: {report[\"winner\"]}')"

.PHONY: evaluate
evaluate:
	$(PYTHON) -c "\
from src.datascience.pipeline.model_evaluation_pipeline import ModelEvaluationTrainingPipeline; \
ModelEvaluationTrainingPipeline().initiate_model_evaluation()"

.PHONY: drift
drift:
	$(PYTHON) -c "\
from src.datascience.pipeline.data_drift_pipeline import DataDriftPipeline; \
DataDriftPipeline().run()"

.PHONY: pipeline
pipeline:
	$(PYTHON) main.py

# ── Quality ───────────────────────────────────────────────────────────────────
.PHONY: test
test:
	$(PYTEST) tests/ \
		--cov=src/datascience --cov=app \
		--cov-report=term-missing \
		--cov-report=xml:coverage.xml \
		--junitxml=test-results.xml \
		-v

.PHONY: lint
lint:
	$(PYTHON) -m flake8 src/ app.py main.py \
		--max-line-length=120 \
		--ignore=E501,W503

.PHONY: check
check: lint test

# ── App ───────────────────────────────────────────────────────────────────────
.PHONY: serve
serve:
	FLASK_APP=$(FLASK_APP) FLASK_ENV=development $(PYTHON) app.py

# ── Docker ────────────────────────────────────────────────────────────────────
.PHONY: docker-build
docker-build:
	docker build -t $(IMAGE_NAME):$(IMAGE_TAG) .

.PHONY: docker-run
docker-run:
	docker run --rm -p $(PORT):8080 \
		-e MLFLOW_TRACKING_USERNAME \
		-e MLFLOW_TRACKING_PASSWORD \
		-e INFERENCE_LOG_BUCKET \
		--name $(IMAGE_NAME) \
		$(IMAGE_NAME):$(IMAGE_TAG)

.PHONY: docker-stop
docker-stop:
	docker stop $(IMAGE_NAME) 2>/dev/null || true

# ── DVC ───────────────────────────────────────────────────────────────────────
.PHONY: dvc-pull
dvc-pull:
	$(PYTHON) -m dvc pull

.PHONY: dvc-push
dvc-push:
	$(PYTHON) -m dvc push

.PHONY: dvc-status
dvc-status:
	$(PYTHON) -m dvc status

# ── Cleanup ───────────────────────────────────────────────────────────────────
.PHONY: clean
clean:
	rm -rf artifacts/data_ingestion \
	       artifacts/data_transformation \
	       artifacts/data_validation \
	       artifacts/model_trainer \
	       artifacts/model_evaluation \
	       artifacts/data_drift \
	       logs/ \
	       coverage.xml \
	       test-results.xml \
	       .pytest_cache \
	       __pycache__ \
	       src/**/__pycache__
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -name "*.pyc" -delete

.PHONY: clean-venv
clean-venv:
	rm -rf venv
