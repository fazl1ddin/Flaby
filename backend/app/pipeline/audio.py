"""Audio helpers: probe duration and normalise to 16 kHz mono WAV for WhisperX."""
from __future__ import annotations

import json
import os
import subprocess


def probe_duration(path: str) -> float:
    """Return duration in seconds via ffprobe, or 0 if unavailable."""
    try:
        out = subprocess.run(
            ["ffprobe", "-v", "quiet", "-print_format", "json",
             "-show_format", path],
            capture_output=True, text=True, timeout=60,
        )
        if out.returncode == 0:
            data = json.loads(out.stdout or "{}")
            return float(data.get("format", {}).get("duration", 0) or 0)
    except (FileNotFoundError, subprocess.SubprocessError, ValueError):
        pass
    return 0.0


def to_wav_16k_mono(src: str, dst: str) -> bool:
    """Transcode `src` to a 16 kHz mono WAV at `dst`. Returns True on success."""
    try:
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        out = subprocess.run(
            ["ffmpeg", "-y", "-i", src, "-ac", "1", "-ar", "16000",
             "-vn", "-f", "wav", dst],
            capture_output=True, text=True, timeout=1800,
        )
        return out.returncode == 0 and os.path.exists(dst)
    except (FileNotFoundError, subprocess.SubprocessError):
        return False
