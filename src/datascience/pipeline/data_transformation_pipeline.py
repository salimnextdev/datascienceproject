from src.datascience.config.configuration import ConfigurationManager
from src.datascience.components.data_transformation import DataTransformation
from src.datascience import logger
from pathlib import Path

STAGE_NAME = "Data Transformation Stage"


class DataTransformationTrainingPipeline:
    def __init__(self):
        pass

    def initiate_data_transformation(self):
        config = ConfigurationManager()
        status_file = Path(config.get_data_validation_config().STATUS_FILE)
        with status_file.open() as f:
            statuses = [
                line.rsplit(":", 1)[-1].strip().lower()
                for line in f
                if line.strip()
            ]

        if not statuses or any(status != "true" for status in statuses):
            raise ValueError("Data validation failed; see the validation status file.")

        data_transformation_config = config.get_data_transformation_config()
        data_transformation = DataTransformation(config=data_transformation_config)
        data_transformation.train_test_splitting()


if __name__ == "__main__":
    try:
        logger.info(f">>>>> stage {STAGE_NAME} started <<<<<")
        pipeline = DataTransformationTrainingPipeline()
        pipeline.initiate_data_transformation()
        logger.info(f">>>>> stage {STAGE_NAME} completed <<<<<\n\nx==========x")
    except Exception as Error:
        logger.exception(f"Stage {STAGE_NAME} failed")
        raise Error