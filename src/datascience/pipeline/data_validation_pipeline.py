import pandas as pd

from src.datascience.config.configuration import ConfigurationManager
from src.datascience.components.data_validation import DataValidation
from src.datascience import logger

STAGE_NAME = "Data Validation Stage"


class DataValidationTrainingPipeline:
    def __init__(self):
        pass

    def initiate_data_validation(self):
        config = ConfigurationManager()
        data_validation_config = config.get_data_validation_config()
        data_validation = DataValidation(config=data_validation_config)

        data_validation.validate_all_columns()
        validation_data = pd.read_csv(data_validation_config.unzip_data_dir)
        data_validation.validate_column_data_types(
            data=validation_data,
            expected_schema=data_validation_config.all_schema,
            status_file=data_validation_config.STATUS_FILE,
        )


if __name__ == "__main__":
    try:
        logger.info(f">>>>> stage {STAGE_NAME} started <<<<<")
        pipeline = DataValidationTrainingPipeline()
        pipeline.initiate_data_validation()
        logger.info(f">>>>> stage {STAGE_NAME} completed <<<<<\n\nx==========x")
    except Exception:
        logger.exception(f"Stage {STAGE_NAME} failed")
        raise