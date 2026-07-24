"""Pydantic models shared across the API and the analysis pipeline.

The *Analysis* models double as Claude structured-output schemas
(`client.messages.parse(output_format=...)`), so keep them flat and simple:
plain types, arrays, and Literal enums only.
"""
from __future__ import annotations

from typing import List, Literal, Optional

from pydantic import BaseModel, Field

Speaker = Literal["A", "B"]
MomentType = Literal["good", "warn", "bad"]
Status = Literal["queued", "processing", "done", "error"]
StepStatus = Literal["wait", "active", "done", "error"]


# --------------------------------------------------------------------------- #
# Transcript
# --------------------------------------------------------------------------- #
class Turn(BaseModel):
    speaker: Speaker                 # A = manager, B = client
    speaker_label: str               # human label, e.g. "Менеджер"
    start: float                     # seconds
    end: float                       # seconds
    text: str


# --------------------------------------------------------------------------- #
# Analysis — engagement / sentiment (produced by Claude, call #1)
# --------------------------------------------------------------------------- #
class EngagementPoint(BaseModel):
    t: float = Field(description="Time offset in seconds from the call start")
    value: float = Field(description="Client engagement 0-100 at this moment")


class Moment(BaseModel):
    t: float = Field(description="Time offset in seconds")
    label: str = Field(description="Short label for the moment (Russian)")
    type: MomentType = Field(description="good | warn | bad")


class EngagementAnalysis(BaseModel):
    """Claude structured output for the engagement / sentiment step."""
    score: int = Field(description="Overall call score 0-100")
    score_label: str = Field(description="Short verdict, e.g. 'Хороший звонок'")
    summary: str = Field(description="One-sentence dynamic summary, e.g. 'спад к финалу'")
    engagement: List[EngagementPoint] = Field(description="15-25 points across the whole call")
    moments: List[Moment] = Field(description="4-8 key moments on the timeline")
    objections_total: int = Field(default=0, description="Number of objections raised by the client")
    objections_handled: int = Field(default=0, description="How many were handled well")


# --------------------------------------------------------------------------- #
# Analysis — coaching card (produced by Claude, call #2)
# --------------------------------------------------------------------------- #
class CoachingItem(BaseModel):
    title: str = Field(description="Bold headline of the point (Russian)")
    detail: str = Field(description="One-sentence explanation (Russian)")
    timestamp: str = Field(default="", description="Time range like '06:10 – 08:30' or a short tag")


class CoachingCard(BaseModel):
    strengths: List[CoachingItem] = Field(description="Exactly 3 things done well")
    missed: List[CoachingItem] = Field(description="Exactly 3 missed opportunities")
    next_steps: List[str] = Field(description="2-4 recommended next actions")


# --------------------------------------------------------------------------- #
# Derived / merged metrics (mostly computed in Python)
# --------------------------------------------------------------------------- #
class Metrics(BaseModel):
    talk_ratio_manager: int = 0        # % of talk time
    talk_ratio_client: int = 0
    questions_asked: int = 0
    open_questions: int = 0
    longest_monologue_sec: float = 0
    longest_monologue_at: float = 0
    objections_total: int = 0
    objections_handled: int = 0
    engagement_avg: int = 0
    engagement_peak_at: float = 0
    engagement_low_at: float = 0


class Analysis(BaseModel):
    score: int
    score_label: str
    summary: str
    engagement: List[EngagementPoint]
    moments: List[Moment]
    coaching: CoachingCard
    metrics: Metrics


# --------------------------------------------------------------------------- #
# Job / Call
# --------------------------------------------------------------------------- #
class Step(BaseModel):
    key: str
    title: str
    tool: Optional[str] = None          # e.g. "WhisperX", "Claude"
    status: StepStatus = "wait"
    detail: Optional[str] = None
    percent: Optional[int] = None


class Call(BaseModel):
    id: str
    filename: str
    created_at: str                     # ISO 8601
    status: Status = "queued"
    mock: bool = False                  # true if demo data was used anywhere
    duration: float = 0
    language: Optional[str] = None
    manager: str = "Азиз Р."
    error: Optional[str] = None
    steps: List[Step] = Field(default_factory=list)
    transcript: List[Turn] = Field(default_factory=list)
    analysis: Optional[Analysis] = None


class CallSummary(BaseModel):
    id: str
    filename: str
    created_at: str
    status: Status
    duration: float
    score: Optional[int] = None
    score_label: Optional[str] = None
    manager: str = "Азиз Р."


def initial_steps() -> List[Step]:
    return [
        Step(key="convert", title="Загрузка и конвертация аудио"),
        Step(key="transcribe", title="Транскрипция речи", tool="WhisperX"),
        Step(key="diarize", title="Диаризация спикеров — кто говорит"),
        Step(key="engagement", title="Анализ вовлечённости и тональности", tool="Claude"),
        Step(key="coaching", title="Карточка коуча: сильные стороны и упущения", tool="Claude"),
    ]
