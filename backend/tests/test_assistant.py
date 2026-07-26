"""
Regression unit and endpoint integration tests for Recruiter AI Copilot Assistant, Task Routing, and Schema Validation.
Verifies robust handling of calculate_years_experience, task-type routing, fallback contracts, and ask_assistant endpoint.
"""
import json
import pytest
from unittest.mock import patch, AsyncMock
from fastapi.testclient import TestClient
from main import app
from app.core.config import call_llm
from app.services.ai_gateway import ai_gateway
from app.api.evaluate import (
    calculate_years_experience,
    extract_candidate_deterministic_metadata,
    extract_salary_information,
    extract_notice_period,
    extract_current_role_and_company,
    extract_education,
    extract_certifications
)

client = TestClient(app)

def test_calculate_years_experience_variants():
    # 1. Normal multi-year entries
    work_history = [
        {"role": "Senior Engineer", "dates": "2020 - 2024"},
        {"role": "Engineer", "dates": "2018 - 2020"}
    ]
    assert calculate_years_experience(work_history) == "6.0 Years"

    # 2. Present / Current ongoing entry
    work_present = [
        {"role": "Lead", "dates": "2022 - Present"}
    ]
    assert calculate_years_experience(work_present) == "4.0 Years"

    # 3. Invalid/None/Malformed inputs
    assert calculate_years_experience(None) == "Experience duration cannot be determined from the available information."
    assert calculate_years_experience([]) == "Experience duration cannot be determined from the available information."
    assert calculate_years_experience("invalid_type") == "Experience duration cannot be determined from the available information."
    assert calculate_years_experience([{"role": "Dev", "dates": None}]) == "Experience duration cannot be determined from the available information."

def test_extract_candidate_deterministic_metadata_edge_cases():
    # 1. Malformed / Empty eval data
    meta_empty = extract_candidate_deterministic_metadata({})
    assert meta_empty["candidate_name"] == "Unknown"
    assert "cannot be determined" in meta_empty["experience_duration"]

    # 2. Full eval data
    eval_data = {
        "result": {
            "personal_info": {"name": "Jane Doe"},
            "work_history": [
                {"role": "Senior Backend Developer", "company": "TechCorp", "dates": "2019 - Present"}
            ],
            "raw_resume_text": "Salary: 12 LPA. Serving 30 days notice period. Education: BS Computer Science.",
            "education": ["BS Computer Science"],
            "certifications": [{"title": "AWS Certified Solutions Architect", "issuer": "Amazon"}]
        }
    }
    meta_full = extract_candidate_deterministic_metadata(eval_data)
    assert meta_full["candidate_name"] == "Jane Doe"
    assert "Senior Backend Developer at TechCorp" in meta_full["current_role_company"]
    assert "BS Computer Science" in meta_full["education"]
    assert "AWS Certified" in meta_full["certifications"]

def test_ai_gateway_task_type_schema_routing():
    # 1. Assistant task fallback contract
    assistant_resp = call_llm(
        messages=[{"role": "user", "content": "Does candidate know Python?"}],
        response_format={"type": "json_object"},
        stage="assistant_ask"
    )
    parsed_ast = json.loads(assistant_resp)
    assert isinstance(parsed_ast, dict)

    # 2. Extraction task fallback contract
    extraction_resp = call_llm(
        messages=[{"role": "user", "content": "Extract resume text"}],
        response_format={"type": "json_object"},
        stage="resume_extraction"
    )
    parsed_ext = json.loads(extraction_resp)
    assert isinstance(parsed_ext, dict)

    # 3. Interview generation task fallback contract
    interview_resp = call_llm(
        messages=[{"role": "user", "content": "Generate interview questions"}],
        response_format={"type": "json_object"},
        stage="interview_generation"
    )
    parsed_int = json.loads(interview_resp)
    assert isinstance(parsed_int, dict)

@pytest.mark.asyncio
async def test_recruiter_assistant_endpoint_questions(mocker):
    mock_eval = {
        "evaluation_id": "eval_test123",
        "result": {
            "personal_info": {"name": "Alice Smith"},
            "overall_score": 88,
            "matched_skills": ["Python", "FastAPI", "Agile", "Docker"],
            "missing_skills": ["Kubernetes"],
            "recommendation": {"hiring_recommendation": "Hire", "confidence_score": 90},
            "recommendation_basis": {
                "strengths": ["Strong Python FastAPI experience", "Agile team lead"],
                "weaknesses": ["Missing Kubernetes production experience"]
            },
            "work_history": [
                {"role": "Senior Python Engineer", "company": "DataCorp", "dates": "2020 - Present"}
            ],
            "raw_resume_text": "Alice Smith Senior Python Engineer at DataCorp 2020-Present. Worked in Agile sprint team. Proficient in Python, FastAPI, Docker."
        }
    }
    
    mocker.patch("app.services.evaluation_store.evaluation_store.get_evaluation", return_value=mock_eval)

    queries = [
        "Does this candidate have Agile experience?",
        "How many years of experience does this candidate have?",
        "What programming languages does this candidate know?"
    ]

    for q in queries:
        response = client.post("/api/v1/evaluation/assistant/ask", json={
            "candidate_id": "eval_test123",
            "query": q
        })
        assert response.status_code == 200, f"Query '{q}' failed with status {response.status_code}: {response.text}"
        res_json = response.json()
        assert "answer" in res_json
        assert "citations" in res_json
        assert "confidence" in res_json
        assert "match_type" in res_json
        assert "interview_verification" in res_json

@pytest.mark.asyncio
async def test_assistant_graceful_metadata_failure(mocker):
    mock_eval = {
        "evaluation_id": "eval_fail_meta",
        "result": {"overall_score": 75}
    }
    mocker.patch("app.services.evaluation_store.evaluation_store.get_evaluation", return_value=mock_eval)
    mocker.patch("app.api.evaluate.extract_candidate_deterministic_metadata", side_effect=Exception("Simulated metadata extraction crash"))

    response = client.post("/api/v1/evaluation/assistant/ask", json={
        "candidate_id": "eval_fail_meta",
        "query": "Does candidate have Python experience?"
    })
    
    assert response.status_code == 200
    res_json = response.json()
    assert "answer" in res_json
