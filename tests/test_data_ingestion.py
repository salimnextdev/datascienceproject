import zipfile
from pathlib import Path
from unittest.mock import patch, MagicMock
import pytest

from src.datascience.components.data_ingestion import DataIngestion
from src.datascience.entity.config_entity import DataIngestionConfig


@pytest.fixture
def config(tmp_path):
    return DataIngestionConfig(
        root_dir=tmp_path,
        source_URL="https://example.com/data.zip",
        local_data_file=tmp_path / "data.zip",
        unzip_dir=tmp_path / "unzipped",
    )


def test_download_file_skips_if_exists(config):
    config.local_data_file.write_bytes(b"existing")
    with patch("src.datascience.components.data_ingestion.request.urlretrieve") as mock_dl:
        DataIngestion(config).download_file()
    mock_dl.assert_not_called()


def test_download_file_fetches_when_missing(config):
    with patch("src.datascience.components.data_ingestion.request.urlretrieve") as mock_dl:
        mock_dl.return_value = (str(config.local_data_file), {})
        DataIngestion(config).download_file()
    mock_dl.assert_called_once_with(
        url=config.source_URL, filename=config.local_data_file
    )


def test_extract_zip_file(config, tmp_path):
    zip_path = config.local_data_file
    with zipfile.ZipFile(zip_path, "w") as zf:
        zf.writestr("winequality-red.csv", "col1,col2\n1,2\n")

    DataIngestion(config).extract_zip_file()

    assert (config.unzip_dir / "winequality-red.csv").exists()
