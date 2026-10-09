"""File-related helpers: naming, sizes, temp files, ZIP output."""

from __future__ import annotations

import io
import os
import zipfile
from pathlib import Path


def get_extension(filename: str) -> str:
    """Return lowercase extension with leading dot, e.g. '.pdf'. Empty if none."""
    return Path(filename or "").suffix.lower()


def get_output_filename(source_filename: str) -> str:
    """Map 'paper.pdf' -> 'paper.md' (never 'paper.pdf.md').

    Falls back to 'converted.md' for empty/odd inputs.
    """
    name = (source_filename or "").strip()
    if not name:
        return "converted.md"
    # Strip directories to avoid path traversal in download names.
    name = os.path.basename(name)
    stem = Path(name).stem or "converted"
    return f"{stem}.md"


def human_readable_size(num_bytes: int) -> str:
    size = float(max(0, num_bytes))
    for unit in ("B", "KB", "MB", "GB"):
        if size < 1024.0 or unit == "GB":
            if unit == "B":
                return f"{int(size)} B"
            return f"{size:.1f} {unit}"
        size /= 1024.0
    return f"{size:.1f} GB"


def create_zip(results: list[tuple[str, str]]) -> bytes:
    """Build an in-memory ZIP from (output_filename, markdown) pairs."""
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
        for filename, markdown in results:
            safe_name = os.path.basename(filename) or "converted.md"
            zf.writestr(safe_name, markdown or "")
    buf.seek(0)
    return buf.read()
