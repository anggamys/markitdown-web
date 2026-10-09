"""Post-conversion Markdown cleaning (PRD FR-017).

Runs after MarkItDown conversion, before preview/download:

    Document -> MarkItDown -> Markdown -> Cleaning -> Final Markdown
"""

from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass


@dataclass
class CleaningOptions:
    normalize_unicode: bool = True
    strip_trailing_whitespace: bool = True
    collapse_blank_lines: bool = True
    remove_empty_lines: bool = False


def clean_markdown(text: str, options: CleaningOptions) -> str:
    """Apply selected cleaning steps. Pure function (easy to test)."""
    if not text:
        return ""
    if options.normalize_unicode:
        text = unicodedata.normalize("NFKC", text)
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    lines = text.split("\n")
    if options.strip_trailing_whitespace:
        lines = [line.rstrip() for line in lines]
    text = "\n".join(lines)
    if options.remove_empty_lines:
        text = "\n".join(line for line in text.split("\n") if line.strip())
    elif options.collapse_blank_lines:
        text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip() + "\n" if text.strip() else ""
