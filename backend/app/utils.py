from __future__ import annotations


def fmt_ts(seconds: float) -> str:
    """Format seconds as M:SS (e.g. 6:10)."""
    seconds = max(0, int(round(seconds)))
    return f"{seconds // 60}:{seconds % 60:02d}"
