from src.datascience import logger
from src.datascience.config.configuration import ConfigurationManager
from src.datascience.components.model_trainer import ModelTrainer


class ModelTrainerTrainingPipeline:
    def initiate_model_trainer(self) -> dict:
        config = ConfigurationManager()
        model_trainer_config = config.get_model_trainer_config()
        return ModelTrainer(config=model_trainer_config).train()
