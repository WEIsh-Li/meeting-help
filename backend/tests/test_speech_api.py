from fastapi.testclient import TestClient

from app.main import create_app


def test_audio_upload_returns_503_when_faster_whisper_is_not_available():
    client = TestClient(create_app())
    meeting = client.post("/api/meeting/create", json={"title": "Speech Demo"}).json()

    response = client.post(
        "/api/speech/transcribe",
        data={"meeting_id": meeting["id"]},
        files={"file": ("sample.wav", b"not a real wav", "audio/wav")},
    )

    assert response.status_code == 503
    assert "faster-whisper" in response.json()["detail"]
