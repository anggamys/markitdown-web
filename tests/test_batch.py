"""Unit tests: batch orchestration + ZIP output (PRD FR-008/009/010)."""

import pytest

from src.config.settings import Settings
from src.services.batch_service import BatchService
from src.services.conversion_service import ConversionService
from src.services.validation_service import ValidationService
from src.utils.file_utils import create_zip


@pytest.fixture
def batch() -> BatchService:
    settings = Settings(
        app_env="test", max_file_size_mb=50, temp_dir="/tmp", enable_plugins=False
    )
    return BatchService(ValidationService(settings), ConversionService(settings))


def test_batch_mixed_success_and_failure(batch):
    result = batch.convert_batch(
        [
            ("a.txt", b"# A"),
            ("evil.exe", b"nope"),
            ("b.txt", b"# B"),
        ]
    )
    assert len(result.successes) == 2
    assert len(result.failures) == 1
    assert result.failures[0].error_category == "user"


def test_failed_file_does_not_stop_batch(batch):
    result = batch.convert_batch([("evil.exe", b"x"), ("good.txt", b"# Good")])
    assert len(result.successes) == 1
    assert result.successes[0].source_filename == "good.txt"


def test_zip_contains_only_successes(batch):
    result = batch.convert_batch([("a.txt", b"# A"), ("evil.exe", b"x")])
    data = create_zip([(r.output_filename, r.markdown) for r in result.successes])
    assert data[:2] == b"PK"
    assert len(result.successes) == 1
