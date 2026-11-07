from src.datascience import logger
from src.datascience.pipeline.data_ingestion_pipeline import DataIngestionTrainingPipeline
from src.datascience.pipeline.data_validation_pipeline import DataValidationTrainingPipeline
from src.datascience.pipeline.data_transformation_pipeline import DataTransformationTrainingPipeline
logger.info("welcome to our custom logging data science")

try:
    ingestion_stage = "Data Ingestion Stage"
    logger.info(f">>>>> stage {ingestion_stage} started <<<<<")
    ingestion_pipeline = DataIngestionTrainingPipeline()
    ingestion_pipeline.initiate_data_ingestion()
    logger.info(f">>>>> stage {ingestion_stage} completed <<<<<\n\nx==========x")

    validation_stage = "Data Validation Stage"
    logger.info(f">>>>> stage {validation_stage} started <<<<<")
    validation_pipeline = DataValidationTrainingPipeline()
    validation_pipeline.initiate_data_validation()
    logger.info(f">>>>> stage {validation_stage} completed <<<<<\n\nx==========x")

    transformation_stage = "Data Transformation Stage"
    logger.info(f">>>>> stage {transformation_stage} started <<<<<")
    transformation_pipeline = DataTransformationTrainingPipeline()
    transformation_pipeline.initiate_data_transformation()
    logger.info(f">>>>> stage {transformation_stage} completed <<<<<\n\nx==========x")

except Exception:
    logger.exception("Pipeline execution failed")
    raise
