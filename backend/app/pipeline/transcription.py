"""Transcription + diarization.

Real path: WhisperX (faster-whisper backend) for transcription, then
pyannote-based diarization to split Speaker A / Speaker B. Falls back to
deterministic demo data when WhisperX isn't installed / configured, or when
FLABY_MOCK is set.
"""
from __future__ import annotations

import logging
from typing import Callable, List, Tuple

from ..config import settings
from ..schemas import Turn
from . import mockdata

log = logging.getLogger("flaby.transcription")

# Progress callback: (step_key, percent 0-100, detail or None)
Progress = Callable[[str, int, str | None], None]


def whisperx_available() -> bool:
    if settings.force_mock:
        return False
    try:
        import whisperx  # noqa: F401
        return True
    except Exception:  # pragma: no cover - import side effects vary
        return False


def _resolve_device() -> Tuple[str, str]:
    """Return (device, compute_type)."""
    device = settings.whisper_device
    if device == "auto":
        try:
            import torch
            device = "cuda" if torch.cuda.is_available() else "cpu"
        except Exception:
            device = "cpu"
    compute = settings.whisper_compute_type
    if not compute:
        compute = "float16" if device == "cuda" else "int8"
    return device, compute


def _map_speakers(segments: List[dict]) -> dict:
    """Map raw diarization labels (SPEAKER_00, …) to A/B.

    Heuristic: the first person to speak is treated as the manager (A) —
    salespeople usually open the call. The next distinct speaker becomes the
    client (B). Any further speakers fold into whichever of A/B they most
    resemble by order of appearance.
    """
    order: List[str] = []
    for seg in segments:
        spk = seg.get("speaker")
        if spk and spk not in order:
            order.append(spk)
    mapping: dict = {}
    labels = ["A", "B"]
    for i, spk in enumerate(order):
        mapping[spk] = labels[min(i, 1)]
    return mapping


def transcribe_and_diarize(
    audio_path: str, on_progress: Progress
) -> Tuple[List[Turn], str, float, bool]:
    """Return (turns, language, duration_seconds, used_mock)."""
    if not whisperx_available():
        log.info("WhisperX unavailable -> using demo transcript")
        on_progress("transcribe", 100, "демо-режим (WhisperX не настроен)")
        on_progress("diarize", 100, "демо-режим")
        turns = mockdata.MOCK_TURNS
        return list(turns), "ru", mockdata.MOCK_DURATION, True

    try:
        import whisperx

        device, compute_type = _resolve_device()
        on_progress("transcribe", 5, f"загрузка модели {settings.whisper_model} ({device})")

        model = whisperx.load_model(
            settings.whisper_model, device, compute_type=compute_type
        )
        audio = whisperx.load_audio(audio_path)
        on_progress("transcribe", 30, "распознавание речи")
        result = model.transcribe(
            audio, batch_size=16, language=settings.whisper_language
        )
        language = result.get("language", settings.whisper_language or "ru")

        # Word-level alignment (improves timestamps used for diarization).
        on_progress("transcribe", 70, "выравнивание таймкодов")
        try:
            align_model, metadata = whisperx.load_align_model(
                language_code=language, device=device
            )
            result = whisperx.align(
                result["segments"], align_model, metadata, audio, device,
                return_char_alignments=False,
            )
        except Exception as exc:  # alignment is best-effort
            log.warning("alignment skipped: %s", exc)
        on_progress("transcribe", 100, None)

        # Diarization (requires a HuggingFace token for pyannote).
        on_progress("diarize", 10, "определение спикеров")
        try:
            try:
                from whisperx.diarize import DiarizationPipeline
            except Exception:  # older WhisperX layout
                from whisperx import DiarizationPipeline  # type: ignore

            diarizer = DiarizationPipeline(
                use_auth_token=settings.hf_token or None, device=device
            )
            diarize_segments = diarizer(audio)
            result = whisperx.assign_word_speakers(diarize_segments, result)
        except Exception as exc:
            log.warning("diarization skipped (%s) — single speaker fallback", exc)
        on_progress("diarize", 100, None)

        segments = result.get("segments", [])
        speaker_map = _map_speakers(segments)
        labels = {"A": "Менеджер", "B": "Клиент"}

        turns: List[Turn] = []
        for seg in segments:
            text = (seg.get("text") or "").strip()
            if not text:
                continue
            raw_spk = seg.get("speaker", "SPEAKER_00")
            code = speaker_map.get(raw_spk, "A")
            turns.append(
                Turn(
                    speaker=code,
                    speaker_label=labels[code],
                    start=float(seg.get("start", 0) or 0),
                    end=float(seg.get("end", 0) or 0),
                    text=text,
                )
            )

        duration = turns[-1].end if turns else 0.0
        if not turns:
            raise RuntimeError("WhisperX returned no segments")
        return turns, language, duration, False

    except Exception as exc:
        log.exception("WhisperX pipeline failed, falling back to demo data")
        on_progress("transcribe", 100, f"ошибка WhisperX, демо-режим: {exc}")
        on_progress("diarize", 100, "демо-режим")
        return list(mockdata.MOCK_TURNS), "ru", mockdata.MOCK_DURATION, True
