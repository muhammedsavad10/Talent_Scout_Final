"""
Unit and integration tests for the Evaluation API gateway endpoint.
"""
import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_evaluate_endpoint_success(mocker):
    # Mock PDF extraction
    mocker.patch("app.api.evaluate.extract_text_from_pdf", return_value="dummy text")
    
    # Mock the internal orchestrator execution call completely
    mock_final_state = {
        "status": "success",
        "personal_info": {"name": "Test User"},
        "overall_score": 0.85,
        "decision_engine": {"logic_trace": [{"rule": "test"}]},
        "recommendation": "Excellent profile.",
    }
    
    # We must mock it with AsyncMock since run_evaluation_pipeline is async
    mock_pipeline = mocker.patch("app.api.evaluate.run_evaluation_pipeline")
    mock_pipeline.return_value = mock_final_state
    
    # Construct a valid multipart form payload
    payload = {
        "jd_text": "Need a Python specialist.",
        "jd_skills": "Python, Docker"
    }
    files = {
        "file": ("test_resume.pdf", b"%PDF-1.4 mock content", "application/pdf")
    }
    
    response = client.post("/api/v1/evaluation/evaluate", data=payload, files=files)
    
    assert response.status_code == 200
    json_data = response.json()
    assert json_data["status"] == "COMPLETED"
    assert "result" in json_data
    assert json_data["result"]["overall_score"] == 0.85
    assert json_data["result"]["recommendation"] == "Excellent profile."

def test_evaluate_endpoint_invalid_file_type():
    payload = {"jd_text": "Looking for developers.", "jd_skills": "Go"}
    files = {"file": ("test_resume.txt", b"plain text", "text/plain")}
    
    response = client.post("/api/v1/evaluation/evaluate", data=payload, files=files)
    assert response.status_code == 400
    assert response.json()["detail"] == "Only PDF files are supported."