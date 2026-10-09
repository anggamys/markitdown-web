"""Validation service: extension, size, and content-integrity checks (PRD FR-002)."""

from __future__ import annotations

from dataclasses import dataclass

from src.config.settings import MVP_SUPPORTED_EXTENSIONS, Settings
from src.utils.file_utils import get_extension


@dataclass
class ValidationResult:
    valid: bool
    error: str = ""
    category: str = "user"  # PRD FR-007 tier: user | file


def _check_signature(ext: str, content: bytes) -> str:
    """Return an error message if content clearly mismatches the extension.

    Only formats with reliable magic numbers / markers are enforced; plain
    text formats (.csv, .txt) only reject binary content. Empty string = OK.
    """
    head = content.lstrip(b"\xef\xbb\xbf \t\r\n")[:8]
    if ext == ".pdf":
        if not head.startswith(b"%PDF"):
            return (
                "File content does not look like a PDF document. "
                "The file may be corrupted or misnamed."
            )
    elif ext in (".docx", ".pptx", ".xlsx", ".epub"):
        if not head.startswith(b"PK\x03\x04"):
            return (
                "File content does not match its extension "
                f"('{ext}' should be a ZIP-based document). "
                "The file may be corrupted or misnamed."
            )
    elif ext == ".json":
        if not head.startswith((b"{", b"[")):
            return "File content is not valid JSON."
    elif ext in (".xml", ".html", ".htm"):
        if not head.startswith(b"<"):
            return "File content does not look like markup (expected '<...>')."
    elif ext in (".csv", ".txt"):
        sample = content[:4096]
        if b"\x00" in sample:
            return "File looks like binary data, not plain text."
        try:
            sample.decode("utf-8")
        except UnicodeDecodeError:
            try:
                sample.decode("latin-1")
            except UnicodeDecodeError:
                return "File content is not decodable text."
    return ""


class ValidationService:
    def __init__(self, settings: Settings) -> None:
        self._settings = settings

    @property
    def supported_extensions(self) -> frozenset[str]:
        return MVP_SUPPORTED_EXTENSIONS

    def validate(
        self,
        filename: str,
        size_bytes: int,
        content: bytes | None = None,
    ) -> ValidationResult:
        ext = get_extension(filename)
        if not ext or ext not in MVP_SUPPORTED_EXTENSIONS:
            supported = ", ".join(sorted(MVP_SUPPORTED_EXTENSIONS))
            return ValidationResult(
                valid=False,
                error=(
                    f"Unsupported file type '{ext or '(none)'}'. "
                    f"Supported formats: {supported}."
                ),
            )
        if size_bytes <= 0:
            return ValidationResult(valid=False, error="File is empty.")
        if size_bytes > self._settings.max_file_size_bytes:
            return ValidationResult(
                valid=False,
                error=(
                    f"File is too large ({size_bytes / (1024 * 1024):.1f} MB). "
                    f"Maximum allowed size is {self._settings.max_file_size_mb} MB."
                ),
            )
        if content:
            sig_error = _check_signature(ext, content)
            if sig_error:
                return ValidationResult(valid=False, error=sig_error, category="file")
        return ValidationResult(valid=True)
