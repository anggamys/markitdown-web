"""Unit tests: filename/output utils, stats (FR-012), cleaning (FR-017)."""

from src.utils.cleaning import CleaningOptions, clean_markdown
from src.utils.file_utils import (
    create_zip,
    get_extension,
    get_output_filename,
    human_readable_size,
)
from src.utils.markdown_utils import markdown_stats


def test_output_filename():
    assert get_output_filename("paper.pdf") == "paper.md"
    assert get_output_filename("research-paper.docx") == "research-paper.md"
    assert get_output_filename("") == "converted.md"


def test_get_extension_case_insensitive():
    assert get_extension("PAPER.PDF") == ".pdf"


def test_human_readable_size():
    assert human_readable_size(0) == "0 B"
    assert "KB" in human_readable_size(2048)
    assert "MB" in human_readable_size(5 * 1024 * 1024)


def test_create_zip_magic_bytes():
    assert create_zip([("a.md", "# A")])[:2] == b"PK"


def test_markdown_stats_full():
    md = (
        "# Title\n\nSome words here.\n\n## Sub\n\n"
        "| a | b |\n|---|---|\n| 1 | 2 |\n\n"
        "See [docs](https://x) and ![img](pic.png).\n"
    )
    stats = markdown_stats(md)
    assert stats["headings"] == 2
    assert stats["tables"] == 1
    assert stats["links"] == 1
    assert stats["images"] == 1
    assert stats["words"] > 0
    assert stats["paragraphs"] >= 4
    assert stats["characters"] == len(md)


def test_markdown_stats_empty():
    stats = markdown_stats("")
    assert stats == {
        "characters": 0,
        "words": 0,
        "lines": 0,
        "paragraphs": 0,
        "headings": 0,
        "links": 0,
        "tables": 0,
        "images": 0,
    }


def test_cleaning_collapse_and_strip():
    dirty = "# T   \n\n\n\nbody  \n"
    out = clean_markdown(dirty, CleaningOptions())
    assert out == "# T\n\nbody\n"


def test_cleaning_remove_empty_lines():
    out = clean_markdown("a\n\nb\n", CleaningOptions(remove_empty_lines=True))
    assert out == "a\nb\n"


def test_cleaning_empty_in_empty_out():
    assert clean_markdown("", CleaningOptions()) == ""
