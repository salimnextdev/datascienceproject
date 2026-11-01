import os
from src.datascience import logger
import pandas as pd
from src.datascience.entity.config_entity import DataValidationConfig

class DataValidation:
    def __init__(self,config: DataValidationConfig):
        self.config=config

    def validate_all_columns(self)-> bool:
        try:
            data = pd.read_csv(self.config.unzip_data_dir)
            validation_status = set(data.columns) == set(self.config.all_schema)
            with open(self.config.STATUS_FILE, 'w') as f:
                f.write(f"validation status: {validation_status}\n")

            return validation_status
        except Exception as e:
            raise e

    def validate_column_data_types(self, data: pd.DataFrame, expected_schema: dict, status_file: str) -> bool:
        validation_status = True

        for column, expected_dtype in expected_schema.items():
            if column not in data.columns:
                column_status = False
            else:
                column_status = str(data[column].dtype) == str(expected_dtype)

            validation_status = validation_status and column_status

        with open(status_file, 'a') as status:
            status.write(f"data type validation status: {validation_status}\n")

        return validation_status