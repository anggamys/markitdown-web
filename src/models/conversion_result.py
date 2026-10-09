"""Domain models for conversion results and file metadata."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class ConversionStatus(str, Enum):
    IDLE = "IDLE"
    UPLOADED = "UPLOADED"
    VALIDATING = "VALIDATING"
    PROCESSING = "PROCESSING"
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"


@dataclass
class ConversionResult:
    source_filename: str
    output_filename: str = ""
    status: ConversionStatus = ConversionStatus.IDLE
    markdown: str = ""
    error_message: str = ""
    error_category: str = ""
    processing_time_s: float = 0.0
    input_size_bytes: int = 0
    output_size_bytes: int = 0

    @property
    def succeeded(self) -> bool:
        return self.status == ConversionStatus.SUCCESS

    @classmethod
    def failed(
        cls,
        source_filename: str,
        error_message: str,
        processing_time_s: float = 0.0,
        input_size_bytes: int = 0,
        error_category: str = "conversion",
    ) -> ConversionResult:
        return cls(
            source_filename=source_filename,
            status=ConversionStatus.FAILED,
            error_message=error_message,
            error_category=error_category,
            processing_time_s=processing_time_s,
            input_size_bytes=input_size_bytes,
        )
