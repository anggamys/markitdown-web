"""Unit tests: conversion service + error tiers (PRD FR-003, FR-007)."""

import pytest

from src.config.settings import Settings
from src.services.conversion_service import ConversionService, classify_error


@pytest.fixture
def service() -> ConversionService:
    settings = Settings(
        app_env="test", max_file_size_mb=50, temp_dir="/tmp", enable_plugins=False
    )
    return ConversionService(settings)


def test_txt_conversion_success(service):
    res = service.convert_bytes(b"# Hello\n\nWorld", "notes.txt")
    assert res.succeeded, res.error_message
    assert "Hello" in res.markdown
    assert res.output_filename == "notes.md"
    assert res.output_size_bytes > 0


def test_json_conversion_success(service):
    res = service.convert_bytes(b'{"a": 1}', "data.json")
    assert res.succeeded


def test_conversion_failure_never_raises(service):
    res = service.convert_bytes(b"%PDF-1.4 corrupted \x00\xff", "broken.pdf")
    assert res.source_filename == "broken.pdf"
    assert res.status in ("SUCCESS", "FAILED")
    if not res.succeeded:
        assert res.error_message and res.error_category in (
            "file",
            "conversion",
            "system",
        )
        # No technical internals leaked to the user message.
        assert "Traceback" not in res.error_message


def test_classify_error_tiers():
    assert classify_error(ValueError("file is corrupted")) == "file"
    assert classify_error(ValueError("not a pdf document")) == "file"
    assert classify_error(ValueError("something odd happened")) == "conversion"
    assert classify_error(MemoryError()) == "system"
    assert classify_error(TimeoutError()) == "system"
    assert classify_error(OSError("disk gone")) == "system"
