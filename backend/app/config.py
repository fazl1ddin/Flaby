"""Runtime configuration, read from environment variables.

Nothing here is secret in itself — real secrets (ANTHROPIC_API_KEY, HF_TOKEN)
are read from the environment / .env and never hard-coded.
"""
from __future__ import annotations

import os


def _bool(name: str, default: bool = False) -> bool:
    return os.getenv(name, str(default)).strip().lower() in ("1", "true", "yes", "on")


class Settings:
    def __init__(self) -> None:
        # --- Claude (analysis) ---
        self.anthropic_api_key: str = os.getenv("ANTHROPIC_API_KEY", "").strip()
        # Default model per Anthropic guidance; override via env if desired.
        self.anthropic_model: str = os.getenv("ANTHROPIC_MODEL", "claude-opus-4-8").strip()

        # --- WhisperX (transcription + diarization) ---
        self.hf_token: str = os.getenv("HF_TOKEN", "").strip()
        self.whisper_model: str = os.getenv("WHISPER_MODEL", "large-v3").strip()
        self.whisper_device: str = os.getenv("WHISPER_DEVICE", "auto").strip()  # auto|cpu|cuda
        self.whisper_compute_type: str = os.getenv("WHISPER_COMPUTE_TYPE", "").strip()
        lang = os.getenv("WHISPER_LANGUAGE", "").strip()
        self.whisper_language: str | None = lang or None  # None => auto-detect

        # --- Storage / behaviour ---
        base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # backend/
        self.data_dir: str = os.getenv("FLABY_DATA_DIR", os.path.join(base, "data"))
        self.upload_dir: str = os.path.join(self.data_dir, "uploads")
        self.max_upload_mb: int = int(os.getenv("FLABY_MAX_UPLOAD_MB", "500"))

        # Force demo mode regardless of whether keys/models are present.
        self.force_mock: bool = _bool("FLABY_MOCK", False)

        # CORS origins for the frontend dev server / deployment.
        origins = os.getenv("FLABY_CORS_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173")
        self.cors_origins: list[str] = [o.strip() for o in origins.split(",") if o.strip()]

        os.makedirs(self.upload_dir, exist_ok=True)

    @property
    def analysis_available(self) -> bool:
        """True when a real Claude analysis can run."""
        return bool(self.anthropic_api_key) and not self.force_mock


settings = Settings()
