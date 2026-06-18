from __future__ import annotations

from pathlib import Path
from tempfile import NamedTemporaryFile

from fastapi import APIRouter, File, Form, HTTPException, UploadFile

from app.api.schemas import (
    AddSegmentRequest,
    CreateMeetingRequest,
    GenerateReplyRequest,
    GenerateReplyResponse,
    KnowledgeChunkResponse,
    MeetingResponse,
    ReplyResponse,
    SegmentResponse,
    TranscriptionResponse,
    UploadKnowledgeRequest,
)
from app.domain.knowledge_service import KnowledgeService
from app.domain.meeting_service import MeetingService
from app.domain.models import KnowledgeUse, Meeting, Reply, Segment
from app.domain.reply_service import ReplyService
from app.domain.speech_service import SpeechService, SpeechUnavailableError


router = APIRouter(prefix="/api")
meeting_service = MeetingService()
knowledge_service = KnowledgeService()
reply_service = ReplyService()
speech_service = SpeechService()


@router.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@router.get("/meeting/current", response_model=MeetingResponse)
def current_meeting() -> MeetingResponse:
    return meeting_to_response(meeting_service.current_or_create())


@router.post("/meeting/create", response_model=MeetingResponse)
def create_meeting(request: CreateMeetingRequest) -> MeetingResponse:
    return meeting_to_response(meeting_service.create_meeting(request.title))


@router.post("/meeting/pause/{meeting_id}", response_model=MeetingResponse)
def pause_meeting(meeting_id: str) -> MeetingResponse:
    return _meeting_action(lambda: meeting_service.pause(meeting_id))


@router.post("/meeting/resume/{meeting_id}", response_model=MeetingResponse)
def resume_meeting(meeting_id: str) -> MeetingResponse:
    return _meeting_action(lambda: meeting_service.resume(meeting_id))


@router.post("/meeting/end/{meeting_id}", response_model=MeetingResponse)
def end_meeting(meeting_id: str) -> MeetingResponse:
    return _meeting_action(lambda: meeting_service.end(meeting_id))


@router.post("/meeting/clear/{meeting_id}", response_model=MeetingResponse)
def clear_meeting(meeting_id: str) -> MeetingResponse:
    return _meeting_action(lambda: meeting_service.clear(meeting_id))


@router.post("/segments", response_model=SegmentResponse)
def add_segment(request: AddSegmentRequest) -> SegmentResponse:
    try:
        segment = meeting_service.add_segment(request.meeting_id, request.text_en, request.speaker)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return segment_to_response(segment)


@router.post("/speech/transcribe", response_model=TranscriptionResponse)
async def transcribe_audio(meeting_id: str = Form(...), file: UploadFile = File(...)) -> TranscriptionResponse:
    return await _transcribe_audio_file(meeting_id, file)


@router.post("/speech/transcribe-chunk", response_model=TranscriptionResponse)
async def transcribe_audio_chunk(meeting_id: str = Form(...), file: UploadFile = File(...)) -> TranscriptionResponse:
    return await _transcribe_audio_file(meeting_id, file)


async def _transcribe_audio_file(meeting_id: str, file: UploadFile) -> TranscriptionResponse:
    suffix = Path(file.filename or "audio").suffix or ".wav"
    temp_path: Path | None = None
    try:
        with NamedTemporaryFile(delete=False, suffix=suffix) as temp_file:
            temp_path = Path(temp_file.name)
            temp_file.write(await file.read())

        transcript = speech_service.transcribe(temp_path)
        segment = meeting_service.add_segment(meeting_id, transcript, "Audio", source="system_audio")
        return TranscriptionResponse(
            transcript_en=transcript,
            segment=segment_to_response(segment),
            meeting=meeting_to_response(meeting_service.get_meeting(meeting_id)),
        )
    except SpeechUnavailableError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    finally:
        if temp_path:
            temp_path.unlink(missing_ok=True)


@router.post("/kb/upload", response_model=list[KnowledgeChunkResponse])
def upload_knowledge(request: UploadKnowledgeRequest) -> list[KnowledgeChunkResponse]:
    try:
        chunks = knowledge_service.add_text_file(request.filename, request.content)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return [chunk_to_response(chunk) for chunk in chunks]


@router.get("/kb/chunks", response_model=list[KnowledgeChunkResponse])
def list_knowledge_chunks() -> list[KnowledgeChunkResponse]:
    return [chunk_to_response(chunk) for chunk in knowledge_service.list_chunks()]


@router.post("/ai/generate-reply", response_model=GenerateReplyResponse)
def generate_reply(request: GenerateReplyRequest) -> GenerateReplyResponse:
    try:
        pending = meeting_service.require_pending_segments(request.meeting_id)
        transcript_en = "\n".join(segment.text_en for segment in pending)
        transcript_cn = "\n".join(segment.text_cn_local for segment in pending)
        retrieved = knowledge_service.search(f"{transcript_en}\n{transcript_cn}", limit=5)
        meeting = meeting_service.get_meeting(request.meeting_id)
        reply = reply_service.generate(
            transcript_en=transcript_en,
            transcript_cn=transcript_cn,
            retrieved_knowledge=retrieved,
            meeting_summary=meeting.summary,
        )
        submitted_ids = [segment.id for segment in pending]
        meeting_service.mark_submitted(request.meeting_id, submitted_ids)
        meeting.summary = reply.summary_cn
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    return GenerateReplyResponse(
        reply=reply_to_response(reply),
        submitted_segment_ids=submitted_ids,
        meeting=meeting_to_response(meeting_service.get_meeting(request.meeting_id)),
    )


def _meeting_action(action) -> MeetingResponse:
    try:
        meeting = action()
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return meeting_to_response(meeting)


def meeting_to_response(meeting: Meeting) -> MeetingResponse:
    return MeetingResponse(
        id=meeting.id,
        title=meeting.title,
        status=meeting.status,
        summary=meeting.summary,
        segments=[segment_to_response(segment) for segment in meeting.segments],
        created_at=meeting.created_at,
        ended_at=meeting.ended_at,
    )


def segment_to_response(segment: Segment) -> SegmentResponse:
    return SegmentResponse(
        id=segment.id,
        meeting_id=segment.meeting_id,
        source=segment.source,
        speaker=segment.speaker,
        text_en=segment.text_en,
        text_cn_local=segment.text_cn_local,
        start_time=segment.start_time,
        end_time=segment.end_time,
        submitted=segment.submitted,
        created_at=segment.created_at,
    )


def reply_to_response(reply: Reply) -> ReplyResponse:
    return ReplyResponse(
        intent=reply.intent,
        need_response=reply.need_response,
        summary_cn=reply.summary_cn,
        strategy_cn=reply.strategy_cn,
        answer_cn=reply.answer_cn,
        answer_en=reply.answer_en,
        short_answer_en=reply.short_answer_en,
        follow_up_question_en=reply.follow_up_question_en,
        knowledge_used=[knowledge_use_to_response(item) for item in reply.knowledge_used],
        confidence=reply.confidence,
    )


def knowledge_use_to_response(item: KnowledgeUse):
    return {"source": item.source, "reason": item.reason}


def chunk_to_response(chunk) -> KnowledgeChunkResponse:
    return KnowledgeChunkResponse(
        id=chunk.id,
        source=chunk.source,
        content=chunk.content,
        chunk_index=chunk.chunk_index,
        score=chunk.score,
    )
