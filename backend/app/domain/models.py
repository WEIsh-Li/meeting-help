from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Literal
from uuid import uuid4


def new_id(prefix: str) -> str:
    return f"{prefix}_{uuid4().hex[:12]}"


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


MeetingStatus = Literal["active", "paused", "ended"]
SegmentSource = Literal["system_audio", "microphone", "manual"]
Intent = Literal[
    "question",
    "request_opinion",
    "description",
    "decision_discussion",
    "task_assignment",
    "risk_or_issue",
    "clarification",
    "unclear",
]
Confidence = Literal["low", "medium", "high"]


@dataclass
class Segment:
    id: str
    meeting_id: str
    source: SegmentSource
    speaker: str
    text_en: str
    text_cn_local: str
    start_time: float
    end_time: float
    submitted: bool = False
    created_at: str = field(default_factory=utc_now)


@dataclass
class Meeting:
    id: str
    title: str
    status: MeetingStatus
    summary: str = ""
    segments: list[Segment] = field(default_factory=list)
    created_at: str = field(default_factory=utc_now)
    ended_at: str | None = None


@dataclass
class KnowledgeChunk:
    id: str
    source: str
    content: str
    chunk_index: int
    score: float = 0.0


@dataclass
class KnowledgeUse:
    source: str
    reason: str


@dataclass
class Reply:
    intent: Intent
    need_response: bool
    summary_cn: str
    strategy_cn: str
    answer_cn: str
    answer_en: str
    short_answer_en: str
    follow_up_question_en: str
    knowledge_used: list[KnowledgeUse]
    confidence: Confidence

