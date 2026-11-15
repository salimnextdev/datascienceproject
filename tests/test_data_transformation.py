import json
import pytest
import pandas as pd

from src.datascience.components.data_transformation import DataTransformation, FEATURE_COLUMNS
from src.datascience.entity.config_entity import DataTransformationConfig


@pytest.fixture
def config(tmp_path):
    csv = tmp_path / "data.csv"
    df = pd.DataFrame({
        col: [float(i) for i in range(20)]
        for col in FEATURE_COLUMNS
    })
    df["quality"] = [5] * 20
    df.to_csv(csv, index=False)
    return DataTransformationConfig(root_dir=tmp_path, data_path=csv)


def test_creates_train_and_test_csv(config):
    DataTransformation(config).train_test_splitting()
    assert (config.root_dir / "train.csv").exists()
    assert (config.root_dir / "test.csv").exists()


def test_split_ratio(config):
    DataTransformation(config).train_test_splitting()
    train = pd.read_csv(config.root_dir / "train.csv")
    test = pd.read_csv(config.root_dir / "test.csv")
    assert len(train) == 16
    assert len(test) == 4


def test_feature_ranges_json_created(config):
    DataTransformation(config).train_test_splitting()
    ranges_path = config.root_dir / "feature_ranges.json"
    assert ranges_path.exists()
    ranges = json.loads(ranges_path.read_text())
    assert set(ranges.keys()) == set(FEATURE_COLUMNS)
    for col, bounds in ranges.items():
        assert "min" in bounds and "max" in bounds
        assert bounds["min"] <= bounds["max"]
