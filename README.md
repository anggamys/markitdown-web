# MarkItDown Web Converter

Web UI (Streamlit) wrapping [Microsoft MarkItDown](https://github.com/microsoft/markitdown):
upload documents → convert to Markdown → preview → download.

## Quickstart

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

## Docker

```bash
docker build -t markitdown-web .
docker run -p 8501:8501 markitdown-web
```

## Configuration

Copy `.env.example` to `.env` and adjust as needed.

| Variable | Default | Description |
|---|---|---|
| `APP_ENV` | `development` | Environment name |
| `MAX_FILE_SIZE_MB` | `50` | Max upload size per file |
| `TEMP_DIR` | system temp | Temp dir for conversion |
| `ENABLE_PLUGINS` | `false` | MarkItDown plugins (advanced) |
| `OPENAI_API_KEY` | — | Phase-3 OCR/AI only, never commit |

## MVP formats

`.pdf` `.docx` `.pptx` `.xlsx` `.csv` `.json` `.xml` `.html` `.txt` `.epub`

## Features

- Single + batch conversion with per-file status and ZIP download
- Rendered / raw Markdown preview (wide tables scroll horizontally)
- Document statistics: words, characters, headings, tables, images, links
- Post-conversion cleaning: unicode normalization, whitespace, blank lines
- Tiered errors (user / file / conversion / system) — no stack traces to users
- Content-integrity check: file signature must match its extension

## Layout

```text
app.py                  # Streamlit UI only
src/services/           # conversion_service.py, validation_service.py, batch_service.py
src/models/             # conversion_result.py, file_metadata.py
src/utils/              # file_utils.py, markdown_utils.py, cleaning.py
src/config/             # settings.py
tests/                  # test_validation.py, test_conversion.py, ...
```

## Tests

```bash
pytest
```
