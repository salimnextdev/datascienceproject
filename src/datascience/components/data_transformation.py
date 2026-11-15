import json
import os
from src.datascience import logger
from sklearn.model_selection import train_test_split
import pandas as pd
from src.datascience.entity.config_entity import DataTransformationConfig

FEATURE_COLUMNS = [
    "fixed acidity", "volatile acidity", "citric acid", "residual sugar",
    "chlorides", "free sulfur dioxide", "total sulfur dioxide",
    "density", "pH", "sulphates", "alcohol",
]


class DataTransformation:
    def __init__(self, config: DataTransformationConfig):
        self.config = config

    def train_test_splitting(self):
        data = pd.read_csv(self.config.data_path)
        train, test = train_test_split(data, test_size=0.2, random_state=42)

        train.to_csv(os.path.join(self.config.root_dir, "train.csv"), index=False)
        test.to_csv(os.path.join(self.config.root_dir, "test.csv"), index=False)

        ranges = {
            col: {"min": float(train[col].min()), "max": float(train[col].max())}
            for col in FEATURE_COLUMNS
        }
        with open(os.path.join(self.config.root_dir, "feature_ranges.json"), "w") as f:
            json.dump(ranges, f, indent=2)

        logger.info("Splitted data into train and test sets")
        logger.info(train.shape)
        logger.info(test.shape)