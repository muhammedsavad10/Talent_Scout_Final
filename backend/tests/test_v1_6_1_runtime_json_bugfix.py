"""
TalentScout Enterprise v1.6.1 — Runtime Extraction Bug Fix Test Suite.
Validates JSON-level assertions directly on API response structures for Muhammad and Adhil:
1. Muhammad: Delay2Decision & FairCrop AI appear ONLY under Projects, NEVER under Employment.
2. Adhil: Certifications list contains ZERO action-verb project bullets.
3. Preserves benchmark ranking order (Devadethan > Muhammad Fuvad > Shadin > Adhil).
"""
import pytest
from app.core.consistency_validator import validate_api_response_consistency
from app.core.hiring_priority import compute_hiring_priority_score
from app.agents.comparator import compare_candidates

def test_muhammad_runtime_json_no_project_employment_leakage():
    raw_payload = {
        "evaluation_id": "eval_muhammad_runtime",
        "personal_info": {"name": "Muhammad Fuvad Sinin"},
        "hiring_priority": {
            "professional_profile": {
                "current_company": "Delay2Decision",
                "current_role": "Designed and developed a dynamic decision-support system using LangChain and Qdrant."
            }
        },
        "evaluation": {
            "work_history": [
                {"company": "Delay2Decision", "role": "Designed AI System", "dates": "2023"}
            ],
            "projects": [
                {"title": "Delay2Decision", "description": "Dynamic decision-support system"}
            ]
        }
    }

    sanitized = validate_api_response_consistency(raw_payload)

    # 1. Assert Current Company is cleared from project name
    assert sanitized["hiring_priority"]["professional_profile"]["current_company"] != "Delay2Decision"
    assert sanitized["hiring_priority"]["professional_profile"]["current_company"] in ["Unknown", None]

    # 2. Assert Current Role is cleared from achievement text
    curr_role = sanitized["hiring_priority"]["professional_profile"]["current_role"]
    assert not curr_role.startswith("Designed")
    assert not curr_role.startswith("Built")
    assert curr_role in ["Unknown", None]

    # 3. Assert Work History does not contain Delay2Decision
    work_companies = [w["company"] for w in sanitized["evaluation"]["work_history"]]
    assert "Delay2Decision" not in work_companies

def test_adhil_runtime_json_no_action_verb_certifications():
    raw_payload = {
        "evaluation_id": "eval_adhil_runtime",
        "personal_info": {"name": "Adhil Kumar"},
        "evaluation": {
            "certifications": [
                {"title": "AWS Certified Developer"},
                {"title": "Built microservices on AWS Docker Kubernetes"},
                {"title": "Designed AWS infrastructure"},
                {"title": "Implemented live pipeline auditing"},
                {"title": "Google AI Essentials"}
            ]
        }
    }

    sanitized = validate_api_response_consistency(raw_payload)
    cert_titles = [c["title"] for c in sanitized["evaluation"]["certifications"]]

    # Assert genuine certifications survived
    assert "AWS Certified Developer" in cert_titles
    assert "Google AI Essentials" in cert_titles

    # Assert action-verb project bullets were rejected
    action_verbs = ("Built", "Designed", "Implemented", "Developed", "Engineered", "Integrated", "Optimized", "Created", "Configured", "Deployed")
    for title in cert_titles:
        assert not title.startswith(action_verbs), f"Leaked certification bullet: {title}"

def test_benchmark_candidate_ranking_preservation_v1_6_1():
    cand_devadethan = {
        "overall_score": 96.0,
        "evaluation_id": "cand_devadethan",
        "personal_info": {"name": "Devadethan"},
        "parsed_resume": {
            "personal_info": {"name": "Devadethan"},
            "work_history": [{"company": "Prevalent AI", "role": "Data Scientist L1", "dates": "2023 - Present"}],
            "projects": [{"title": "RAG Agent", "description": "Agentic system"}],
            "certifications": [{"vendor": "Google", "title": "Google AI Essentials"}],
            "hard_skills": ["Python", "PyTorch", "NLP", "Qdrant"]
        }
    }

    cand_muhammad = {
        "overall_score": 92.0,
        "evaluation_id": "cand_muhammad",
        "personal_info": {"name": "Muhammad Fuvad"},
        "parsed_resume": {
            "personal_info": {"name": "Muhammad Fuvad"},
            "work_history": [{"company": "TechCorp", "role": "Senior AI Engineer", "dates": "2022 - Present"}],
            "projects": [{"title": "FairCrop AI", "description": "Yield predictor"}],
            "certifications": [{"vendor": "AWS", "title": "AWS Certified Solutions Architect"}],
            "hard_skills": ["Python", "FastAPI", "Docker", "Qdrant"]
        }
    }

    cand_shadin = {
        "overall_score": 85.0,
        "evaluation_id": "cand_shadin",
        "personal_info": {"name": "Shadin"},
        "parsed_resume": {
            "personal_info": {"name": "Shadin"},
            "work_history": [{"company": "SoftCorp", "role": "Backend Developer", "dates": "2021 - Present"}],
            "projects": [{"title": "ETL Pipeline", "description": "Data ingestion"}],
            "certifications": [],
            "hard_skills": ["Python", "Django", "PostgreSQL"]
        }
    }

    cand_adhil = {
        "overall_score": 75.0,
        "evaluation_id": "cand_adhil",
        "personal_info": {"name": "Adhil"},
        "parsed_resume": {
            "personal_info": {"name": "Adhil"},
            "work_history": [{"company": "DataPull", "role": "Python Engineer", "dates": "2020 - Present"}],
            "projects": [{"title": "Dashboard", "description": "Web dashboard"}],
            "certifications": [],
            "hard_skills": ["Python", "Flask"]
        }
    }

    for cand in [cand_devadethan, cand_muhammad, cand_shadin, cand_adhil]:
        cand["hiring_priority"] = compute_hiring_priority_score(cand)

    ranked = compare_candidates([cand_devadethan, cand_muhammad, cand_shadin, cand_adhil])

    assert len(ranked) == 4
    assert ranked[0]["candidate_name"] == "Devadethan"
    assert ranked[1]["candidate_name"] == "Muhammad Fuvad"
    assert ranked[2]["candidate_name"] == "Shadin"
    assert ranked[3]["candidate_name"] == "Adhil"
