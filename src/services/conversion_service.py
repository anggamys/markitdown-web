"""Conversion service: thin wrapper around Microsoft MarkItDown.

Streamlit UI must call this service instead of using MarkItDown directly,
keeping UI and conversion logic separated (PRD NFR-006).
"""

from __future__ import annotations

import logging
import os
import tempfile
import time

from src.config.settings import Settings
from src.models.conversion_result import ConversionResult, ConversionStatus
from src.utils.file_utils import get_extension, get_output_filename

logger = logging.getLogger(__name__)

#: Map technical exceptions to user-friendly messages (PRD FR-007).
_FRIENDLY_ERROR = (
    "Conversion failed. The uploaded file could not be processed. "
    "Please verify that the file is valid and not corrupted."
)


class ConversionService:
    def __init__(self, settings: Settings) -> None:
        self._settings = settings

    def _build_converter(self, enable_plugins: bool | None = None):
        from markitdown import MarkItDown

        use_plugins = (
            self._settings.enable_plugins if enable_plugins is None else enable_plugins
        )
        return MarkItDown(enable_plugins=use_plugins)

    def convert_bytes(
        self,
        file_bytes: bytes,
        source_filename: str,
        enable_plugins: bool | None = None,
    ) -> ConversionResult:
        started = time.perf_counter()
        input_size = len(file_bytes or b"")
        safe_name = os.path.basename(source_filename or "upload")
        ext = get_extension(safe_name) or ".tmp"

        tmp_path = ""
        try:
            converter = self._build_converter(enable_plugins)
            with tempfile.NamedTemporaryFile(
                delete=False,
                suffix=ext,
                dir=self._settings.temp_dir,
            ) as tmp:
                tmp.write(file_bytes or b"")
                tmp_path = tmp.name

            result = converter.convert(tmp_path)
            markdown = (result.markdown if result else "") or ""
            duration = time.perf_counter() - started
            output_filename = get_output_filename(safe_name)
            logger.info(
                "file=%s size=%d status=success duration=%.2fs",
                safe_name,
                input_size,
                duration,
            )
            return ConversionResult(
                source_filename=safe_name,
                output_filename=output_filename,
                status=ConversionStatus.SUCCESS,
                markdown=markdown,
                processing_time_s=duration,
                input_size_bytes=input_size,
                output_size_bytes=len(markdown.encode("utf-8")),
            )
        except Exception:  # per-file isolation (PRD FR-008, NFR-002)
            duration = time.perf_counter() - started
            logger.exception("Conversion failed file=%s", safe_name)
            return ConversionResult.failed(
                source_filename=safe_name,
                error_message=_FRIENDLY_ERROR,
                processing_time_s=duration,
                input_size_bytes=input_size,
            )
        finally:
            if tmp_path:
                try:
                    os.unlink(tmp_path)
                except OSError:
                    logger.warning("Could not remove temp file %s", tmp_path)
