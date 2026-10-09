"""Unit tests: file validation incl. content-integrity signatures (PRD FR-002)."""

import pytest

from src.config.settings import Settings
from src.services.validation_service import ValidationService


@pytest.fixture
def validator() -> ValidationService:
    settings = Settings(
        app_env="test", max_file_size_mb=1, temp_dir="/tmp", enable_plugins=False
    )
    return ValidationService(settings)


def test_valid_pdf(validator):
    assert validator.validate("paper.pdf", 1024).valid


def test_invalid_extension(validator):
    res = validator.validate("malware.exe", 1024)
    assert not res.valid and "Unsupported" in res.error
    assert res.category == "user"


def test_empty_file(validator):
    assert not validator.validate("paper.pdf", 0).valid


def test_file_size_limit(validator):
    res = validator.validate("big.pdf", 2 * 1024 * 1024)
    assert not res.valid and "too large" in res.error.lower()


def test_pdf_signature_ok(validator):
    assert validator.validate("a.pdf", 100, b"%PDF-1.7 rest").valid


def test_pdf_signature_mismatch(validator):
    res = validator.validate("a.pdf", 100, b"PK\x03\x04 not a pdf")
    assert not res.valid and res.category == "file"


def test_docx_requires_zip_signature(validator):
    assert validator.validate("a.docx", 100, b"PK\x03\x04...").valid
    res = validator.validate("a.docx", 100, b"%PDF-1.4 wrong")
    assert not res.valid


def test_json_signature(validator):
    assert validator.validate("a.json", 10, b'{"a": 1}').valid
    assert not validator.validate("a.json", 10, b"not json").valid


def test_txt_rejects_binary(validator):
    res = validator.validate("a.txt", 10, b"hi\x00there")
    assert not res.valid


def test_no_content_skips_signature(validator):
    assert validator.validate("a.pdf", 100).valid
