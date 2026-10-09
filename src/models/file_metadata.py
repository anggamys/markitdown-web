"""File metadata model (PRD FR-011)."""

from __future__ import annotations

from dataclasses import dataclass

from src.models.conversion_result import ConversionStatus


@dataclass
class FileMetadata:
    filename: str
    extension: str
    size_bytes: int
    status: ConversionStatus = ConversionStatus.UPLOADED
    processing_time_s: float = 0.0
    output_size_bytes: int = 0
