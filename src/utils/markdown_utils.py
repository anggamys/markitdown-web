"""Markdown helpers for stats/preview."""

from __future__ import annotations


def markdown_stats(markdown: str) -> dict[str, int]:
    text = markdown or ""
    return {
        "characters": len(text),
        "words": len(text.split()),
        "lines": text.count("\n") + (1 if text else 0),
    }
