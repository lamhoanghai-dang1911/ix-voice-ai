import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_health_check():
    response = client.get("/api/v1/ai/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "service" in data


def test_transcribe_mock():
    # In mock mode, should return canonical transcript fixture
    payload = {
        "jobId": "f47ac10b-58cc-4372-a567-0e02b2c3d479",
        "audioPath": "dummy_path.wav"
    }
    response = client.post("/api/v1/ai/transcribe", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["jobId"] == "f47ac10b-58cc-4372-a567-0e02b2c3d479"
    assert "segments" in data
    assert len(data["segments"]) > 0
