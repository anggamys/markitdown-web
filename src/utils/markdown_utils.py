"""Markdown helpers: document statistics (PRD FR-012) and preview."""

from __future__ import annotations

import re

_HEADING_RE = re.compile(r"^#{1,6}\s+\S", re.MULTILINE)
_IMAGE_RE = re.compile(r"!\[[^\]]*\]\([^)]+\)")
_LINK_RE = re.compile(r"(?<!!)\[[^\]]+\]\([^)]+\)")
_TABLE_SEPARATOR_RE = re.compile(r"^\s*\|?[\s:\-|]+\|?\s*$")


def _count_tables(lines: list[str]) -> int:
    """Count Markdown tables: a `|...|` header line followed by a separator row."""
    count = 0
    i = 0
    while i < len(lines) - 1:
        if "|" in lines[i] and _TABLE_SEPARATOR_RE.match(lines[i + 1]):
            count += 1
            i += 2
            while i < len(lines) and "|" in lines[i]:
                i += 1
        else:
            i += 1
    return count


def markdown_stats(markdown: str) -> dict[str, int]:
    """Return document statistics: characters, words, lines, paragraphs,
    headings, links, tables, images (PRD FR-012)."""
    text = markdown or ""
    lines = text.splitlines()
    paragraphs = [b for b in re.split(r"\n\s*\n", text) if b.strip()]
    return {
        "characters": len(text),
        "words": len(text.split()),
        "lines": len(lines),
        "paragraphs": len(paragraphs),
        "headings": len(_HEADING_RE.findall(text)),
        "links": len(_LINK_RE.findall(text)),
        "tables": _count_tables(lines),
        "images": len(_IMAGE_RE.findall(text)),
    }
