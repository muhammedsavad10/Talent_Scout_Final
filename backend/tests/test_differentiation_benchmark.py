"""
Stage 2 Candidate Ranking Intelligence Differentiation Benchmark Test.
Verifies that 5 distinct candidate profiles produce distinct Stage 2 evidence scores and that Stage 2
ranks Candidate B (strong professional evidence) above Candidate A (highest technical match),
while gating Candidate E due to unmatched prerequisites.
"""
import pytest
from app.core.hiring_priority import compute_hiring_priority_score
from app.agents.comparator import compare_candidates

def test_stage2_differentiation_5_candidate_benchmark():
    # Candidate A (Muhammad): Highest Stage 1 Technical Match (94%), 2 years experience
    eval_a = {
        "evaluation_id": "eval_muhammad_a",
        "personal_info": {"name": "Muhammad"},
        "filename": "muhammad.pdf",
        "overall_score": 94.0,
        "parsed_resume": {
            "work_history": [
                {"role": "Software Developer", "dates": "2022 - 2024", "description": "Developed Python web applications."}
            ]
        }
    }

    # Candidate B (Dethan): Lower Technical Match (83%), 7.5 years experience, Senior Architect, AWS, Microservices, AWS Cert, Leadership
    eval_b = {
        "evaluation_id": "eval_dethan_b",
        "personal_info": {"name": "Dethan"},
        "filename": "dethan.pdf",
        "overall_score": 83.0,
        "parsed_resume": {
            "work_history": [
                {
                    "role": "Senior Backend Architect",
                    "dates": "2020 - Present",
                    "description": "Architected high-throughput microservices on AWS, Docker, Kubernetes at enterprise scale. Lead engineer mentoring 6 developers."
                },
                {
                    "role": "Software Engineer",
                    "dates": "2016 - 2020",
                    "description": "Built cloud backend systems."
                }
            ],
            "certifications": [{"title": "AWS Certified Solutions Architect"}, {"title": "CKA Certified Kubernetes Administrator"}]
        }
    }

    # Candidate C: Mid-level match (78%), 3.5 years experience, Software Engineer
    eval_c = {
        "evaluation_id": "eval_cand_c",
        "personal_info": {"name": "Candidate C"},
        "filename": "cand_c.pdf",
        "overall_score": 78.0,
        "parsed_resume": {
            "work_history": [
                {"role": "Software Engineer", "dates": "2020 - 2024", "description": "Built Docker microservices and cloud APIs."}
            ]
        }
    }

    # Candidate D: Low-moderate match (65%), 1 year junior experience
    eval_d = {
        "evaluation_id": "eval_cand_d",
        "personal_info": {"name": "Candidate D"},
        "filename": "cand_d.pdf",
        "overall_score": 65.0,
        "parsed_resume": {
            "work_history": [
                {"role": "Junior Developer", "dates": "2023 - 2024", "description": "Maintained internal web forms."}
            ]
        }
    }

    # Candidate E: Unmatched Stage 1 score (35%) - Fails prerequisite threshold
    eval_e = {
        "evaluation_id": "eval_cand_e",
        "personal_info": {"name": "Candidate E"},
        "filename": "cand_e.pdf",
        "overall_score": 35.0,
        "parsed_resume": {
            "work_history": [
                {"role": "Senior Accountant", "dates": "2008 - 2024", "description": "Managed corporate financial accounting."}
            ]
        }
    }

    # 1. Compute Stage 2 Priority Scores
    res_a = compute_hiring_priority_score(eval_a)
    res_b = compute_hiring_priority_score(eval_b)
    res_c = compute_hiring_priority_score(eval_c)
    res_d = compute_hiring_priority_score(eval_d)
    res_e = compute_hiring_priority_score(eval_e)

    # Verify that different resumes produce DIFFERENT Stage 2 career evidence scores
    raw_scores = [
        res_a["priority_factors"]["raw_career_priority_score"],
        res_b["priority_factors"]["raw_career_priority_score"],
        res_c["priority_factors"]["raw_career_priority_score"],
        res_d["priority_factors"]["raw_career_priority_score"],
        res_e["priority_factors"]["raw_career_priority_score"]
    ]
    assert len(set(raw_scores)) == 5, f"Expected 5 distinct career scores, got: {raw_scores}"

    # Verify Candidate B has significantly higher career priority evidence than Candidate A
    assert res_b["priority_factors"]["raw_career_priority_score"] > res_a["priority_factors"]["raw_career_priority_score"]
    assert res_b["hiring_priority_score"] > res_a["hiring_priority_score"]

    # Verify Fine-Grained Evidence structure
    assert "professional_experience" in res_b["fine_grained_evidence"]
    assert "seniority_alignment" in res_b["fine_grained_evidence"]
    assert "production_engineering" in res_b["fine_grained_evidence"]
    assert "points" in res_b["fine_grained_evidence"]["production_engineering"]
    assert "reason" in res_b["fine_grained_evidence"]["production_engineering"]

    # Verify Candidate E prerequisite threshold gating
    assert res_e["prerequisite_met"] is False
    assert res_e["hiring_priority_score"] <= 20

    # 2. Verify Final Batch Candidate Ranking
    evals_batch = [eval_a, eval_b, eval_c, eval_d, eval_e]
    ranked = compare_candidates(evals_batch)

    # Under 2-Phase Recruiter Architecture, Candidate B (Dethan, 7.5 yrs exp) ranks #1
    assert ranked[0]["candidate_name"] == "Dethan"
    assert ranked[1]["candidate_name"] == "Muhammad"
    assert ranked[0]["rank"] == 1

    # Candidate E must be bottom ranked
    assert ranked[-1]["candidate_name"] == "Candidate E"
