"""
Regression Test Suite for TalentScout Enterprise Critical Architecture Fix:
Two-Phase Candidate Ranking & Score Synchronization.
"""
import pytest
from app.agents.comparator import compare_candidates
from app.core.hiring_priority import compute_hiring_priority_score
from app.core.consistency_validator import validate_final_api_response

def test_two_phase_ranking_architecture_fresher_vs_senior():
    """
    Verifies that the candidate ranking pipeline evaluates BOTH Phase 1 (Technical Screening)
    and Phase 2 (Recruiter & Experience Intelligence), ranking an experienced Senior Data Scientist
    higher than a fresher candidate who has only a higher keyword match density.
    """
    # Candidate A: Fresher with 95% Phase 1 Technical Match, 0 years experience
    eval_fresher = {
        "evaluation_id": "eval_fresher_95",
        "candidate_id": "eval_fresher_95",
        "personal_info": {"name": "Candidate A (Fresher)"},
        "filename": "fresher_resume.pdf",
        "overall_score": 95.0,  # High Phase 1 keyword match
        "parsed_resume": {
            "work_history": [],
            "certifications": [],
            "hard_skills": ["Python", "Machine Learning", "FastAPI"]
        },
        "work_history": [],
        "raw_resume_text": "Recent Computer Science Graduate with strong knowledge in Python, FastAPI, and Machine Learning."
    }

    # Candidate B: Senior Data Scientist with 88% Phase 1 Technical Match, 8 years experience, Production ML, Leadership
    eval_senior = {
        "evaluation_id": "eval_senior_88",
        "candidate_id": "eval_senior_88",
        "personal_info": {"name": "Candidate B (Senior Data Scientist)"},
        "filename": "senior_resume.pdf",
        "overall_score": 88.0,  # Slightly lower Phase 1 keyword match
        "parsed_resume": {
            "work_history": [
                {
                    "role": "Senior Data Scientist & ML Lead",
                    "company": "Enterprise AI Systems",
                    "dates": "2020 - Present",
                    "description": "Architected production recommendation systems and distributed ML pipelines on AWS. Led team of 8 ML engineers."
                },
                {
                    "role": "Data Scientist",
                    "company": "Cloud Data Labs",
                    "dates": "2016 - 2020",
                    "description": "Built scalable predictive models and PyTorch deep learning microservices."
                }
            ],
            "certifications": [{"title": "AWS Certified Machine Learning - Specialty"}],
            "hard_skills": ["Python", "PyTorch", "AWS", "FastAPI", "Docker", "Kubernetes"]
        },
        "work_history": [
            {
                "role": "Senior Data Scientist & ML Lead",
                "company": "Enterprise AI Systems",
                "dates": "2020 - Present",
                "description": "Architected production recommendation systems and distributed ML pipelines on AWS. Led team of 8 ML engineers."
            },
            {
                "role": "Data Scientist",
                "company": "Cloud Data Labs",
                "dates": "2016 - 2020",
                "description": "Built scalable predictive models and PyTorch deep learning microservices."
            }
        ],
        "certifications": [{"title": "AWS Certified Machine Learning - Specialty"}],
        "raw_resume_text": "Senior Data Scientist with 8 years industry experience leading production ML deployments and cloud architecture."
    }

    # 1. Compute Phase 2 Hiring Priority Scores
    hp_fresher = compute_hiring_priority_score(eval_fresher)
    hp_senior = compute_hiring_priority_score(eval_senior)

    eval_fresher["hiring_priority"] = hp_fresher
    eval_senior["hiring_priority"] = hp_senior

    # Senior Candidate B must have a higher Hiring Priority Score than Fresher Candidate A
    assert hp_senior["hiring_priority_score"] > hp_fresher["hiring_priority_score"]
    assert hp_senior["hiring_priority_score"] >= 80

    # 2. Run Candidate Comparator Engine
    ranked = compare_candidates([eval_fresher, eval_senior])
    assert len(ranked) == 2

    # Candidate B (Senior Data Scientist) MUST rank #1
    assert ranked[0]["candidate_name"] == "Candidate B (Senior Data Scientist)"
    assert ranked[0]["rank"] == 1
    assert ranked[1]["candidate_name"] == "Candidate A (Fresher)"
    assert ranked[1]["rank"] == 2

    # 3. Verify Serialized API Payload Consistency
    api_response_fresher = validate_final_api_response({
        "status": "COMPLETED",
        "result": eval_fresher
    })
    api_response_senior = validate_final_api_response({
        "status": "COMPLETED",
        "result": eval_senior
    })

    # Root overall_score must reflect the unified 2-Phase Recruiter Final Score
    assert api_response_senior["overall_score"] > api_response_fresher["overall_score"]
    assert api_response_senior["overall_score"] == hp_senior["hiring_priority_score"]
