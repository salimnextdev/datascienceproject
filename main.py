from src.datascience import logger
from src.datascience.pipeline.data_ingestion_pipeline import DataIngestionTrainingPipeline

logger.info("welcome to our custom logging data science")

STAGE_NAME = "Data Ingestion Stage"
try:
    logger.info("f>>>> stage {STAGE_NAME} started<<<<")
    obj = DataIngestionTrainingPipeline()
    obj.initiate_data_ingestion()
    logger.info(f">>> stage {STAGE_NAME} completed <<<<\n\nx==========x")
except Exception as e:
    raise e