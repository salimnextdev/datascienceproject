import pytest
import pandas as pd

from src.datascience.components.data_validation import DataValidation
from src.datascience.entity.config_entity import DataValidationConfig

SCHEMA = {
    "fixed acidity": "float64",
    "volatile acidity": "float64",
    "quality": "int64",
}


@pytest.fixture
def config(tmp_path):
    csv = tmp_path / "data.csv"
    status = tmp_path / "status.txt"
    return DataValidationConfig(
        root_dir=tmp_path,
        STATUS_FILE=str(status),
        unzip_data_dir=csv,
        all_schema=SCHEMA,
    )


def _write_csv(path, df):
    df.to_csv(path, index=False)


def test_validate_all_columns_passes(config):
    _write_csv(config.unzip_data_dir, pd.DataFrame(columns=SCHEMA.keys()))
    assert DataValidation(config).validate_all_columns() is True


def test_validate_all_columns_fails_on_missing_column(config):
    _write_csv(config.unzip_data_dir, pd.DataFrame(columns=["fixed acidity"]))
    assert DataValidation(config).validate_all_columns() is False


def test_validate_column_data_types_passes(config, tmp_path):
    df = pd.DataFrame({
        "fixed acidity": pd.array([7.0], dtype="float64"),
        "volatile acidity": pd.array([0.5], dtype="float64"),
        "quality": pd.array([6], dtype="int64"),
    })
    status_file = str(tmp_path / "dtype_status.txt")
    result = DataValidation(config).validate_column_data_types(df, SCHEMA, status_file)
    assert result is True


def test_validate_column_data_types_fails_on_wrong_type(config, tmp_path):
    df = pd.DataFrame({
        "fixed acidity": pd.array([7.0], dtype="float64"),
        "volatile acidity": pd.array([0.5], dtype="float64"),
        "quality": pd.array([6.0], dtype="float64"),  # should be int64
    })
    status_file = str(tmp_path / "dtype_status.txt")
    result = DataValidation(config).validate_column_data_types(df, SCHEMA, status_file)
    assert result is False
