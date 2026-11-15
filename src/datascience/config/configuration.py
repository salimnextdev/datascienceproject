from src.datascience.constants import *
from src.datascience.utils.common import read_yaml, create_directories
from src.datascience.entity.config_entity import (
    DataIngestionConfig, DataValidationConfig, DataTransformationConfig,
    ModelTrainerConfig, ModelEvaluationConfig, DataDriftConfig,
)
class ConfigurationManager:
    def __init__(self,
                 config_filepath=CONFIG_FILEPATH,
                 schema_filepath=SCHEMA_FILEPATH,
                 params_filepath=PARAMS_FILEPATH):
        self.config=read_yaml(config_filepath)
        self.schema=read_yaml(schema_filepath)
        self.params=read_yaml(params_filepath)

        create_directories([self.config.artifacts_root])


    def get_data_ingestion_config(self)-> DataIngestionConfig:
        config=self.config.data_ingestion
        create_directories([config.root_dir])

        data_ingestion_config=DataIngestionConfig(
            root_dir=config.root_dir,
            source_URL=config.source_URL,
            local_data_file=config.local_data_file,
            unzip_dir=config.unzip_dir

        )
        return data_ingestion_config

    def get_data_validation_config(self)-> DataValidationConfig:
            config = self.config.data_validation
            schema = self.schema.COLUMNS
            
            create_directories([config.root_dir])
    
            data_validation_config=DataValidationConfig(
                root_dir=config.root_dir,
                unzip_data_dir=config.unzip_dir,
                STATUS_FILE=config.STATUS_FILE,
                all_schema=schema
            )
    
            return data_validation_config

    def get_data_transformation_config(self)-> DataTransformationConfig:
           config=self.config.data_transformation
           create_directories([config.root_dir])
           data_transformation_config=DataTransformationConfig(
               root_dir=config.root_dir,
               data_path=config.data_path
           )
           return data_transformation_config

    def get_model_trainer_config(self) -> ModelTrainerConfig:
        config = self.config.model_trainer
        schema = self.schema.TARGET_COLUMN

        create_directories([config.root_dir])

        return ModelTrainerConfig(
            root_dir=config.root_dir,
            train_data_path=config.train_data_path,
            test_data_path=config.test_data_path,
            model_name=config.model_name,
            param_grids={
                "ElasticNet":        dict(self.params.ElasticNet),
                "RandomForest":      dict(self.params.RandomForest),
                "GradientBoosting":  dict(self.params.GradientBoosting),
            },
            target_column=schema.name,
            cv_folds=int(config.cv_folds),
            mlflow_uri=config.mlflow_uri,
        )

    def get_model_evaluation_config(self) -> ModelEvaluationConfig:
        config = self.config.model_evaluation
        schema = self.schema.TARGET_COLUMN

        create_directories([config.root_dir])

        return ModelEvaluationConfig(
            root_dir=config.root_dir,
            test_data_path=config.test_data_path,
            model_path=config.model_path,
            all_params={},
            metric_file_name=config.metric_file_name,
            target_column=schema.name,
            mlflow_uri="https://dagshub.com/salimnextdev/datascienceproject.mlflow",
        )

    def get_data_drift_config(self) -> DataDriftConfig:
        config = self.config.data_drift
        create_directories([config.root_dir])
        return DataDriftConfig(
            root_dir=Path(config.root_dir),
            train_data_path=Path(config.train_data_path),
            test_data_path=Path(config.test_data_path),
            inference_log=Path(config.inference_log),
            drift_report_json=Path(config.drift_report_json),
            drift_report_html=Path(config.drift_report_html),
            drift_threshold=float(config.drift_threshold),
        )