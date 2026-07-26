"""
TalentScout Enterprise v1.6.2 — Final Production Runtime Integrity Test Suite (Hosting Freeze).
Validates absolute single source of truth and runtime integrity on the final API JSON dictionary.
"""
import pytest
from app.core.consistency_validator import validate_final_api_response
from app.core.hiring_priority import compute_hiring_priority_score
from app.agents.comparator import compare_candidates

def test_v1_6_2_muhammad_final_api_json_integrity():
    raw_api_payload = {
        "evaluation_id": "eval_muhammad_v162",
        "status": "COMPLETED",
        "result": {
            "candidate_id": "eval_muhammad_v162",
            "personal_info": {"name": "Muhammad Fuvad Sinin"},
            "hiring_priority": {
                "professional_profile": {
                    "current_company": "Delay2Decision",
                    "current_role": "Designed and developed a dynamic decision-support system"
                }
            },
            "employment_history": [
                {"company": "Delay2Decision", "role": "Designed AI System", "dates": "2023"}
            ],
            "work_history": [
                {"company": "FairCrop AI", "role": "Built Crop Predictor", "dates": "2022"}
            ],
            "projects": [
                {"title": "Delay2Decision", "description": "Decision support system"},
                {"title": "FairCrop AI", "description": "Crop yield prediction system"}
            ]
        }
    }

    final_json = validate_final_api_response(raw_api_payload)
    res = final_json["result"]

    # 1. Single Source of Truth assertions for Muhammad
    assert final_json["current_company"] == "Unknown"
    assert final_json["current_role"] == "Unknown"
    assert res["hiring_priority"]["professional_profile"]["current_company"] == "Unknown"
    assert res["hiring_priority"]["professional_profile"]["current_role"] == "Unknown"

    # 2. Employment History must contain zero project entries
    assert res.get("employment_history") == []
    assert res.get("work_history") == []

    # 3. Delay2Decision and FairCrop AI exist ONLY under projects
    project_titles = [p["title"] for p in res["projects"]]
    assert "Delay2Decision" in project_titles
    assert "FairCrop AI" in project_titles

def test_v1_6_2_adhil_final_api_json_integrity():
    raw_api_payload = {
        "evaluation_id": "eval_adhil_v162",
        "status": "COMPLETED",
        "result": {
            "candidate_id": "eval_adhil_v162",
            "personal_info": {"name": "Adhil Kumar"},
            "certifications": [
                {"title": "AWS Certified Developer"},
                {"title": "Built microservices using Docker Kubernetes"},
                {"title": "Implemented live pipeline auditing"},
                {"title": "Designed AWS infrastructure"},
                {"title": "Google Professional ML Engineer"}
            ]
        }
    }

    final_json = validate_final_api_response(raw_api_payload)
    cert_titles = [c["title"] for c in final_json["result"]["certifications"]]

    # Assert genuine certifications survived
    assert "AWS Certified Developer" in cert_titles
    assert "Google Professional ML Engineer" in cert_titles
    assert len(cert_titles) == 2

    # Assert zero action-verb project bullets or 'using' implementation details survived
    action_verbs = ("Built", "Designed", "Implemented", "Developed", "Created", "Engineered", "Integrated", "Configured", "Optimized", "Deployed")
    for title in cert_titles:
        assert not title.startswith(action_verbs)
        assert " using " not in title.lower()

def test_v1_6_2_hosting_freeze_benchmark_ranking_preservation():
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
