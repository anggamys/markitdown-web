"""Validation service: extension + size checks for uploaded files."""

from __future__ import annotations

from dataclasses import dataclass

from src.config.settings import MVP_SUPPORTED_EXTENSIONS, Settings
from src.utils.file_utils import get_extension


@dataclass
class ValidationResult:
    valid: bool
    error: str = ""


class ValidationService:
    def __init__(self, settings: Settings) -> None:
        self._settings = settings

    @property
    def supported_extensions(self) -> frozenset[str]:
        return MVP_SUPPORTED_EXTENSIONS

    def validate(self, filename: str, size_bytes: int) -> ValidationResult:
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
        return ValidationResult(valid=True)
