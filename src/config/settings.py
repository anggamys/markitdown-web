"""Application settings loaded from environment variables."""

import os
import tempfile
from dataclasses import dataclass, field


def _get_int(name: str, default: int) -> int:
    try:
        return int(os.getenv(name, str(default)))
    except ValueError:
        return default


def _get_bool(name: str, default: bool) -> bool:
    val = os.getenv(name, str(default)).strip().lower()
    return val in ("1", "true", "yes", "on")


@dataclass(frozen=True)
class Settings:
    app_env: str = field(default_factory=lambda: os.getenv("APP_ENV", "development"))
    max_file_size_mb: int = field(
        default_factory=lambda: _get_int("MAX_FILE_SIZE_MB", 50)
    )
    temp_dir: str = field(
        default_factory=lambda: os.getenv("TEMP_DIR", tempfile.gettempdir())
    )
    enable_plugins: bool = field(
        default_factory=lambda: _get_bool("ENABLE_PLUGINS", False)
    )

    @property
    def max_file_size_bytes(self) -> int:
        return self.max_file_size_mb * 1024 * 1024


#: MVP input formats (PRD section 9). Extension set includes leading dot, lowercase.
MVP_SUPPORTED_EXTENSIONS: frozenset[str] = frozenset(
    {
        ".pdf",
        ".docx",
        ".pptx",
        ".xlsx",
        ".csv",
        ".json",
        ".xml",
        ".html",
        ".htm",
        ".txt",
        ".epub",
    }
)

#: Phase-2 formats (accepted only if explicitly enabled later; listed for UI info).
PHASE2_EXTENSIONS: frozenset[str] = frozenset(
    {
        ".jpg",
        ".jpeg",
        ".png",
        ".mp3",
        ".wav",
        ".zip",
    }
)


def get_settings() -> Settings:
    return Settings()
