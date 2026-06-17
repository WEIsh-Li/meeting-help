from __future__ import annotations

from .models import Meeting, Segment, new_id, utc_now
from .translation_service import TranslationService


class MeetingService:
    def __init__(self, translator: TranslationService | None = None) -> None:
        self._meetings: dict[str, Meeting] = {}
        self._translator = translator or TranslationService()

    def create_meeting(self, title: str) -> Meeting:
        meeting = Meeting(id=new_id("meeting"), title=title.strip() or "Demo Meeting", status="active")
        self._meetings[meeting.id] = meeting
        return meeting

    def get_meeting(self, meeting_id: str) -> Meeting:
        try:
            return self._meetings[meeting_id]
        except KeyError as exc:
            raise ValueError("Meeting not found") from exc

    def current_or_create(self) -> Meeting:
        active = [meeting for meeting in self._meetings.values() if meeting.status != "ended"]
        if active:
            return active[-1]
        return self.create_meeting("Demo Meeting")

    def pause(self, meeting_id: str) -> Meeting:
        meeting = self.get_meeting(meeting_id)
        meeting.status = "paused"
        return meeting

    def resume(self, meeting_id: str) -> Meeting:
        meeting = self.get_meeting(meeting_id)
        meeting.status = "active"
        return meeting

    def end(self, meeting_id: str) -> Meeting:
        meeting = self.get_meeting(meeting_id)
        meeting.status = "ended"
        meeting.ended_at = utc_now()
        return meeting

    def clear(self, meeting_id: str) -> Meeting:
        meeting = self.get_meeting(meeting_id)
        meeting.segments.clear()
        meeting.summary = ""
        return meeting

    def add_segment(self, meeting_id: str, text_en: str, speaker: str, source: str = "manual") -> Segment:
        meeting = self.get_meeting(meeting_id)
        cleaned = " ".join(text_en.split())
        if not cleaned:
            raise ValueError("Transcript text cannot be empty")
        offset = float(len(meeting.segments) * 8)
        segment = Segment(
            id=new_id("segment"),
            meeting_id=meeting_id,
            source="manual" if source not in {"system_audio", "microphone"} else source,
            speaker=speaker.strip() or "Other",
            text_en=cleaned,
            text_cn_local=self._translator.translate(cleaned),
            start_time=offset,
            end_time=offset + 5.0,
        )
        meeting.segments.append(segment)
        return segment

    def get_pending_segments(self, meeting_id: str) -> list[Segment]:
        return [segment for segment in self.get_meeting(meeting_id).segments if not segment.submitted]

    def require_pending_segments(self, meeting_id: str) -> list[Segment]:
        pending = self.get_pending_segments(meeting_id)
        if not pending:
            raise ValueError("No pending transcript segments")
        return pending

    def mark_submitted(self, meeting_id: str, segment_ids: list[str]) -> None:
        target_ids = set(segment_ids)
        for segment in self.get_meeting(meeting_id).segments:
            if segment.id in target_ids:
                segment.submitted = True

