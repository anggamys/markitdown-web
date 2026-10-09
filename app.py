"""MarkItDown Web Converter — Streamlit UI.

Workflow: Upload -> Validate -> Convert -> Preview -> Download.
Conversion itself lives in src/services/ (MarkItDown engine + batch orchestration).
"""

from __future__ import annotations

import logging

import streamlit as st

from src.config.settings import MVP_SUPPORTED_EXTENSIONS, get_settings
from src.services.batch_service import BatchService
from src.services.conversion_service import ConversionService
from src.services.validation_service import ValidationService
from src.utils.cleaning import CleaningOptions, clean_markdown
from src.utils.file_utils import create_zip, get_output_filename, human_readable_size
from src.utils.markdown_utils import markdown_stats

logging.basicConfig(level=logging.INFO)

settings = get_settings()
validator = ValidationService(settings)
converter = ConversionService(settings)
batch = BatchService(validator, converter)

st.set_page_config(page_title="MarkItDown Web Converter", page_icon="📄", layout="wide")

st.title("MarkItDown Web Converter")
st.caption("Convert documents into Markdown — powered by Microsoft MarkItDown.")

# Keep wide tables readable: horizontal scroll inside the page instead of
# overflowing it, without forcing cell content to wrap.
st.markdown(
    """<style>
    [data-testid="stMarkdownContainer"] table {
        display: block;
        max-width: 100%;
        overflow-x: auto;
        white-space: nowrap;
    }
    [data-testid="stMarkdownContainer"] th,
    [data-testid="stMarkdownContainer"] td {
        white-space: nowrap;
    }
    </style>""",
    unsafe_allow_html=True,
)

with st.sidebar:
    st.header("Options")
    enable_plugins = st.checkbox(
        "Enable plugins",
        value=settings.enable_plugins,
        help="Advanced option. MarkItDown plugins are disabled by default.",
    )
    st.subheader("Cleaning")
    cleaning = CleaningOptions(
        normalize_unicode=st.checkbox("Normalize unicode", value=True),
        strip_trailing_whitespace=st.checkbox("Strip trailing whitespace", value=True),
        collapse_blank_lines=st.checkbox("Collapse blank lines", value=True),
        remove_empty_lines=st.checkbox("Remove all empty lines", value=False),
    )
    st.divider()
    st.subheader("Limits")
    st.write(f"Max file size: **{settings.max_file_size_mb} MB**")
    st.subheader("Supported formats (MVP)")
    st.write(" ".join(f"`{e}`" for e in sorted(MVP_SUPPORTED_EXTENSIONS)))

uploaded_files = st.file_uploader(
    "Drag & drop files here or browse",
    accept_multiple_files=True,
    help=f"Supported: {', '.join(sorted(MVP_SUPPORTED_EXTENSIONS))}",
)

if not uploaded_files:
    st.info("Upload one or more documents to get started.")
    st.stop()

# Validation overview
st.subheader("Files")
valid_files = []
for f in uploaded_files:
    data = f.getvalue()
    check = validator.validate(f.name, len(data), data)
    if check.valid:
        valid_files.append(f)
        st.success(f"✓ **{f.name}** — {human_readable_size(len(data))}")
    else:
        st.error(f"✗ **{f.name}** — {check.error}")

convert_clicked = st.button(
    "Convert",
    type="primary",
    disabled=not valid_files,
    help="Convert all valid files to Markdown."
    if valid_files
    else "No valid files to convert.",
)

if not convert_clicked:
    st.stop()

# Conversion (per-file isolation: one failure never stops the batch)
results = []
progress = st.progress(0, text="Converting...")
for i, f in enumerate(uploaded_files):
    data = f.getvalue()
    with st.status(f"Converting **{f.name}**...", expanded=False) as s:
        res = batch.convert_one(f.name, data, enable_plugins=enable_plugins)
        if res.succeeded:
            cleaned = clean_markdown(res.markdown, cleaning)
            res.markdown = cleaned
            res.output_size_bytes = len(cleaned.encode("utf-8"))
            s.update(label=f"✓ {f.name} converted", state="complete")
        else:
            s.update(label=f"✗ {f.name} failed", state="error")
    results.append(res)
    progress.progress((i + 1) / len(uploaded_files))
progress.empty()

successes = [r for r in results if r.succeeded]
failures = [r for r in results if not r.succeeded]

st.subheader("Conversion Result")
cols = st.columns(3)
cols[0].metric("Total", len(results))
cols[1].metric("Succeeded", len(successes))
cols[2].metric("Failed", len(failures))

if failures:
    with st.expander(f"Failed files ({len(failures)})", expanded=True):
        for res in failures:
            st.error(f"**{res.source_filename}** — {res.error_message}")

# Batch download
if len(successes) > 1:
    zip_bytes = create_zip([(r.output_filename, r.markdown) for r in successes])
    st.download_button(
        "Download All (.zip)",
        data=zip_bytes,
        file_name="converted-files.zip",
        mime="application/zip",
    )

# Per-file results
view_mode = st.radio("Preview mode", ["Rendered", "Raw Markdown"], horizontal=True)

for res in successes:
    stats = markdown_stats(res.markdown)
    with st.expander(
        f"✓ {res.source_filename} → {res.output_filename}",
        expanded=(len(successes) == 1),
    ):
        st.caption(
            f"Processing time: **{res.processing_time_s:.2f}s** · "
            f"Input: **{human_readable_size(res.input_size_bytes)}** · "
            f"Output: **{human_readable_size(res.output_size_bytes)}**"
        )
        st.caption(
            f"{stats['words']:,} words · {stats['characters']:,} characters · "
            f"{stats['headings']} headings · {stats['tables']} tables · "
            f"{stats['images']} images · {stats['links']} links · "
            f"{stats['paragraphs']} paragraphs"
        )
        if view_mode == "Rendered":
            st.markdown(res.markdown or "*Empty document.*")
        else:
            st.code(res.markdown or "", language="markdown")
        st.download_button(
            f"Download {res.output_filename}",
            data=res.markdown.encode("utf-8"),
            file_name=res.output_filename or get_output_filename(res.source_filename),
            mime="text/markdown",
            key=f"dl-{res.source_filename}",
        )

if not successes and failures:
    st.warning("All conversions failed. Check that files are valid and not corrupted.")
