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

| Variable           | Default     | Description                   |
| ------------------ | ----------- | ----------------------------- |
| `MAX_FILE_SIZE_MB` | `50`        | Max upload size per file      |
| `TEMP_DIR`         | system temp | Temp dir for conversion       |
| `ENABLE_PLUGINS`   | `false`     | MarkItDown plugins (advanced) |

## MVP formats

`.pdf` `.docx` `.pptx` `.xlsx` `.csv` `.json` `.xml` `.html` `.txt` `.epub`

## Layout

```text
app.py                  # Streamlit UI only
src/services/           # conversion_service.py, validation_service.py
src/models/             # conversion_result.py
src/utils/              # file_utils.py, markdown_utils.py
src/config/             # settings.py
tests/                  # unit tests
```

## Tests

```bash
pytest
```
