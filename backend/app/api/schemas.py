from __future__ import annotations

from pydantic import BaseModel, Field


class KnowledgeUseResponse(BaseModel):
    source: str
    reason: str


class ReplyResponse(BaseModel):
    intent: str
    need_response: bool
    summary_cn: str
    strategy_cn: str
    answer_cn: str
    answer_en: str
    short_answer_en: str
    follow_up_question_en: str
    knowledge_used: list[KnowledgeUseResponse]
    confidence: str


class SegmentResponse(BaseModel):
    id: str
    meeting_id: str
    source: str
    speaker: str
    text_en: str
    text_cn_local: str
    start_time: float
    end_time: float
    submitted: bool
    created_at: str


class MeetingResponse(BaseModel):
    id: str
    title: str
    status: str
    summary: str
    segments: list[SegmentResponse]
    created_at: str
    ended_at: str | None


class TranscriptionResponse(BaseModel):
    transcript_en: str
    segment: SegmentResponse
    meeting: MeetingResponse


class CreateMeetingRequest(BaseModel):
    title: str = Field(default="Demo Meeting", max_length=120)


class AddSegmentRequest(BaseModel):
    meeting_id: str
    text_en: str = Field(min_length=1, max_length=4000)
    speaker: str = Field(default="Other", max_length=80)


class UploadKnowledgeRequest(BaseModel):
    filename: str = Field(min_length=1, max_length=240)
    content: str = Field(min_length=1, max_length=200_000)


class KnowledgeChunkResponse(BaseModel):
    id: str
    source: str
    content: str
    chunk_index: int
    score: float


class GenerateReplyRequest(BaseModel):
    meeting_id: str


class GenerateReplyResponse(BaseModel):
    reply: ReplyResponse
    submitted_segment_ids: list[str]
    meeting: MeetingResponse


class ErrorResponse(BaseModel):
    detail: str
