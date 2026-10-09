"""Batch orchestration: validate + convert many files with per-file isolation.

One failed file never stops the batch (PRD FR-008/FR-009). The Streamlit UI
calls convert_one() per file so it can show per-file progress; summarize()
aggregates the outcome.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from src.models.conversion_result import ConversionResult
from src.services.conversion_service import ConversionService
from src.services.validation_service import ValidationService


@dataclass
class BatchResult:
    results: list[ConversionResult] = field(default_factory=list)

    @property
    def successes(self) -> list[ConversionResult]:
        return [r for r in self.results if r.succeeded]

    @property
    def failures(self) -> list[ConversionResult]:
        return [r for r in self.results if not r.succeeded]


class BatchService:
    def __init__(
        self,
        validator: ValidationService,
        converter: ConversionService,
    ) -> None:
        self._validator = validator
        self._converter = converter

    def convert_one(
        self,
        filename: str,
        content: bytes,
        enable_plugins: bool | None = None,
    ) -> ConversionResult:
        """Validate then convert a single file. Never raises."""
        check = self._validator.validate(filename, len(content or b""), content)
        if not check.valid:
            return ConversionResult.failed(
                source_filename=filename,
                error_message=check.error,
                input_size_bytes=len(content or b""),
                error_category=check.category,
            )
        return self._converter.convert_bytes(content, filename, enable_plugins)

    def convert_batch(
        self,
        items: list[tuple[str, bytes]],
        enable_plugins: bool | None = None,
    ) -> BatchResult:
        return BatchResult(
            results=[
                self.convert_one(name, data, enable_plugins) for name, data in items
            ]
        )
