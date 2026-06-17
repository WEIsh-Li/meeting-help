import pytest

from app.domain.meeting_service import MeetingService


def test_generate_reply_marks_only_pending_segments_after_success():
    service = MeetingService()
    meeting = service.create_meeting("Demo")
    first = service.add_segment(meeting.id, "What is your suggestion?", "Other")
    second = service.add_segment(meeting.id, "The client is worried about onboarding.", "Other")

    pending = service.get_pending_segments(meeting.id)
    assert [segment.id for segment in pending] == [first.id, second.id]

    service.mark_submitted(meeting.id, [segment.id for segment in pending])

    assert service.get_pending_segments(meeting.id) == []
    stored = service.get_meeting(meeting.id)
    assert [segment.submitted for segment in stored.segments] == [True, True]


def test_failed_reply_keeps_segments_pending():
    service = MeetingService()
    meeting = service.create_meeting("Demo")
    segment = service.add_segment(meeting.id, "Can we reduce release risk?", "Other")

    pending = service.get_pending_segments(meeting.id)
    assert [item.id for item in pending] == [segment.id]

    stored = service.get_meeting(meeting.id)
    assert stored.segments[0].submitted is False


def test_no_pending_segments_raises_clear_error():
    service = MeetingService()
    meeting = service.create_meeting("Demo")

    with pytest.raises(ValueError, match="No pending transcript segments"):
        service.require_pending_segments(meeting.id)

