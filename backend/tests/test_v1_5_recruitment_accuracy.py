"""
TalentScout Enterprise v1.5 — Recruitment Intelligence Accuracy Test Suite.
Verifies that Data Scientist / AI Engineer (High Technical Match) correctly outranks
Full Stack Developer (Lower Technical Match) for a Data Scientist opening.
"""
import pytest
from app.core.role_relevance import calculate_role_and_domain_relevance
from app.core.hiring_priority import compute_hiring_priority_score
from app.agents.comparator import compare_candidates

def test_role_relevance_calculation():
    ds_history = [{"role": "Senior Data Scientist", "company": "AI Labs"}]
    ds_skills = ["Python", "PyTorch", "NLP", "Qdrant"]
    ds_relevance = calculate_role_and_domain_relevance(ds_history, ds_skills, jd_title="Data Scientist")
    assert ds_relevance >= 85.0

    fs_history = [{"role": "Python Full Stack Developer", "company": "WebCorp"}]
    fs_skills = ["Python", "JavaScript", "HTML", "CSS"]
    fs_relevance = calculate_role_and_domain_relevance(fs_history, fs_skills, jd_title="Data Scientist")
    assert fs_relevance <= 65.0
    assert ds_relevance > fs_relevance

def test_benchmark_data_scientist_outranks_full_stack_dev():
    # Candidate A: Data Scientist (High Stage 1 Match = 96)
    cand_a_payload = {
        "overall_score": 96.0,
        "evaluation_id": "cand_a_ds",
        "personal_info": {"name": "Candidate A (Data Scientist)"},
        "parsed_resume": {
            "personal_info": {"name": "Candidate A (Data Scientist)"},
            "work_history": [{"company": "AI Labs", "role": "Senior Data Scientist", "dates": "2022 - Present"}],
            "projects": [{"title": "RAG AI Agent", "description": "Built multi-agent RAG using PyTorch and Qdrant."}],
            "certifications": [{"vendor": "Google", "title": "Google AI Essentials"}],
            "hard_skills": ["Python", "PyTorch", "NLP", "Qdrant", "FastAPI"]
        }
    }
    
    # Candidate B: Full Stack Dev (Lower Stage 1 Match = 59, but high tenure/companies)
    cand_b_payload = {
        "overall_score": 59.0,
        "evaluation_id": "cand_b_fs",
        "personal_info": {"name": "Candidate B (Full Stack Dev)"},
        "parsed_resume": {
            "personal_info": {"name": "Candidate B (Full Stack Dev)"},
            "work_history": [
                {"company": "WebCorp 1", "role": "Full Stack Developer", "dates": "2018 - 2020"},
                {"company": "WebCorp 2", "role": "Senior Python Developer", "dates": "2020 - Present"}
            ],
            "projects": [{"title": "Company Dashboard", "description": "Built Web UI and REST API."}],
            "certifications": [{"vendor": "Udemy", "title": "Web Development Bootcamp"}],
            "hard_skills": ["Python", "JavaScript", "HTML", "CSS"]
        }
    }

    eval_a = compute_hiring_priority_score(cand_a_payload)
    eval_b = compute_hiring_priority_score(cand_b_payload)

    cand_a_payload["hiring_priority"] = eval_a
    cand_b_payload["hiring_priority"] = eval_b

    ranked = compare_candidates([cand_a_payload, cand_b_payload])

    assert len(ranked) == 2
    # Candidate A MUST be Rank 1
    assert ranked[0]["candidate_name"] == "Candidate A (Data Scientist)"
    assert ranked[0]["rank"] == 1
    assert ranked[1]["candidate_name"] == "Candidate B (Full Stack Dev)"
    assert ranked[1]["rank"] == 2
    assert ranked[0]["hiring_priority_score"] > ranked[1]["hiring_priority_score"]
