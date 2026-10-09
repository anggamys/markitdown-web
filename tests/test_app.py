"""Unit tests: validation, filename utils, conversion service."""

from src.config.settings import Settings
from src.services.conversion_service import ConversionService
from src.services.validation_service import ValidationService
from src.utils.file_utils import create_zip, get_output_filename, human_readable_size


def make_services(max_mb: int = 50):
    settings = Settings(max_file_size_mb=max_mb, temp_dir="/tmp", enable_plugins=False)
    return ValidationService(settings), ConversionService(settings)


def test_valid_pdf():
    v, _ = make_services()
    assert v.validate("paper.pdf", 1024).valid


def test_invalid_extension():
    v, _ = make_services()
    res = v.validate("malware.exe", 1024)
    assert not res.valid and "Unsupported" in res.error


def test_file_size_limit():
    v, _ = make_services(max_mb=1)
    res = v.validate("big.pdf", 2 * 1024 * 1024)
    assert not res.valid and "too large" in res.error.lower()


def test_output_filename():
    assert get_output_filename("paper.pdf") == "paper.md"
    assert get_output_filename("research-paper.docx") == "research-paper.md"
    assert get_output_filename("archive.tar.gz") == "archive.tar.md"
    assert get_output_filename("") == "converted.md"


def test_human_readable_size():
    assert human_readable_size(0) == "0 B"
    assert "KB" in human_readable_size(2048)
    assert "MB" in human_readable_size(5 * 1024 * 1024)


def test_conversion_txt_success():
    _, c = make_services()
    res = c.convert_bytes(b"# Hello\n\nWorld", "notes.txt")
    assert res.succeeded, res.error_message
    assert "Hello" in res.markdown
    assert res.output_filename == "notes.md"


def test_conversion_failure_isolated():
    _, c = make_services()
    res = c.convert_bytes(b"%PDF-1.4 corrupted \x00\xff", "broken.pdf")
    # Either MarkItDown extracts something or fails gracefully — never raises.
    assert res.source_filename == "broken.pdf"
    assert res.status in ("SUCCESS", "FAILED")


def test_create_zip():
    data = create_zip([("a.md", "# A"), ("b.md", "# B")])
    assert data[:2] == b"PK"  # ZIP magic bytes
