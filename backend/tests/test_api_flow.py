from fastapi.testclient import TestClient

from app.main import create_app


def test_api_demo_flow_generates_reply_and_marks_segments_submitted():
    client = TestClient(create_app())

    meeting = client.post("/api/meeting/create", json={"title": "Demo"}).json()
    segment_response = client.post(
        "/api/segments",
        json={
            "meeting_id": meeting["id"],
            "speaker": "Other",
            "text_en": "The client is concerned that onboarding is too complex.",
        },
    )
    assert segment_response.status_code == 200
    assert segment_response.json()["submitted"] is False

    upload_response = client.post(
        "/api/kb/upload",
        json={
            "filename": "prd.md",
            "content": "The MVP should simplify onboarding and reduce first-time user friction.",
        },
    )
    assert upload_response.status_code == 200
    assert upload_response.json()[0]["source"] == "prd.md"

    reply_response = client.post("/api/ai/generate-reply", json={"meeting_id": meeting["id"]})
    assert reply_response.status_code == 200
    body = reply_response.json()
    assert body["reply"]["intent"] == "risk_or_issue"
    assert body["reply"]["answer_en"]
    assert body["meeting"]["segments"][0]["submitted"] is True

