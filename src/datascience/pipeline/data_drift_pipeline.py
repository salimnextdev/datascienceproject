from src.datascience import logger
from src.datascience.config.configuration import ConfigurationManager
from src.datascience.components.data_drift import DataDrift

STAGE_NAME = "Data Drift Stage"


class DataDriftPipeline:
    def __init__(self):
        pass

    def run(self) -> dict:
        config = ConfigurationManager()
        drift_config = config.get_data_drift_config()
        return DataDrift(config=drift_config).run()
