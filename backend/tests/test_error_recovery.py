import pytest
from fastapi.testclient import TestClient
import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from main import app
from app.core.config import settings
import httpx

client = TestClient(app)

def test_groq_failure_structured_error(monkeypatch):
    # Simulate a bad API key to trigger a Groq 401/403
    monkeypatch.setattr(settings, "GROQ_API_KEY", "gsk_invalid_mock_key")
    files = {"file": ("resume.pdf", b"%PDF-1.4\nSample", "application/pdf")}
    data = {"jd_text": "Sample", "jd_skills": "Python"}
    response = client.post(
        "/api/v1/evaluation/evaluate", 
        files=files, data=data
    )
    # The app should catch this and return a 500 or 422 with a structured error
    assert response.status_code >= 400
    data = response.json()
    
    # Verify structured error
    assert "detail" in data or "error" in data, "Response body must include a structured error"
    
    # Ensure sensitive information is not exposed
    res_str = str(data).lower()
    assert "gsk_" not in res_str
    assert "traceback" not in res_str
    print("[SUCCESS] Groq Failure: Structured error returned, no sensitive info.")

def test_supabase_unavailable(monkeypatch):
    # Invalidate URL
    monkeypatch.setattr(settings, "SUPABASE_URL", "https://invalid-supabase.co")
    response = client.post(
        "/api/evaluate", 
        json={"job_id": "test_err_2", "resume_text": "Sample text", "candidate_name": "Test 2"}
    )
    assert response.status_code >= 400
    data = response.json()
    assert "detail" in data or "error" in data
    assert "traceback" not in str(data).lower()
    print("[SUCCESS] Supabase Failure: Structured error returned, no sensitive info.")

def test_qdrant_unavailable(monkeypatch):
    monkeypatch.setattr(settings, "QDRANT_URL", "https://invalid-qdrant.io")
    response = client.post(
        "/api/evaluate", 
        json={"job_id": "test_err_3", "resume_text": "Sample text", "candidate_name": "Test 3"}
    )
    assert response.status_code >= 400
    data = response.json()
    assert "detail" in data or "error" in data
    assert "traceback" not in str(data).lower()
    print("[SUCCESS] Qdrant Failure: Structured error returned, no sensitive info.")

if __name__ == "__main__":
    print("Running Error Recovery Validation...")
    # We can run these tests directly
    pytest.main(["-s", __file__])
