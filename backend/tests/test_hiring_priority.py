"""
Unit and Integration Tests for Stage 2 Hiring Priority Engine and Candidate Ranking Intelligence.
Verifies that candidate priority ranking ranks experienced senior candidates above freshers for interview
while preserving Stage 1 ATS/Semantic Match Scores untouched.
Includes prerequisite match thresholding, textual rationale, and CandidateEvidence extraction pipeline tests.
"""
import pytest
from app.core.hiring_priority import compute_hiring_priority_score, extract_candidate_evidence
from app.agents.comparator import compare_candidates

def test_fresher_vs_senior_ranking_priority():
    # Candidate 1 (Fresher): High 90% Stage 1 match, but 0 years experience
    eval_fresher = {
        "evaluation_id": "eval_fresher_01",
        "personal_info": {"name": "Fresher Candidate"},
        "filename": "fresher_resume.pdf",
        "overall_score": 90.0,
        "recommendation": {"hiring_recommendation": "Strong Hire"},
        "parsed_resume": {
            "work_history": [],
            "certifications": []
        },
        "work_history": [],
        "raw_resume_text": "Recent CS Graduate with top projects in Python and PyTorch. No formal industry experience."
    }

    # Candidate 2 (Senior Professional): 83% Stage 1 match, 7 years experience, Senior Developer, Production scale & AWS
    eval_senior = {
        "evaluation_id": "eval_senior_02",
        "personal_info": {"name": "Senior Professional"},
        "filename": "senior_resume.pdf",
        "overall_score": 83.0,
        "recommendation": {"hiring_recommendation": "Hire"},
        "parsed_resume": {
            "work_history": [
                {
                    "role": "Senior Backend Architect",
                    "company": "Tech Enterprises",
                    "dates": "2020 - Present",
                    "description": "Architected high-throughput microservices on AWS, Docker, Kubernetes at enterprise scale. Lead engineer mentoring 6 developers."
                },
                {
                    "role": "Software Developer",
                    "company": "Cloud Systems",
                    "dates": "2017 - 2020",
                    "description": "Built distributed data pipelines and cloud backend APIs."
                }
            ],
            "certifications": [{"title": "AWS Certified Solutions Architect"}]
        },
        "work_history": [
            {
                "role": "Senior Backend Architect",
                "company": "Tech Enterprises",
                "dates": "2020 - Present",
                "description": "Architected high-throughput microservices on AWS, Docker, Kubernetes at enterprise scale. Lead engineer mentoring 6 developers."
            },
            {
                "role": "Software Developer",
                "company": "Cloud Systems",
                "dates": "2017 - 2020",
                "description": "Built distributed data pipelines and cloud backend APIs."
            }
        ],
        "certifications": [{"title": "AWS Certified Solutions Architect"}],
        "raw_resume_text": "Senior Backend Architect with 7 years industry experience leading AWS microservices."
    }

    # 1. Verify Stage 2 Hiring Priority Scores
    res_fresher = compute_hiring_priority_score(eval_fresher)
    res_senior = compute_hiring_priority_score(eval_senior)

    assert res_fresher["stage1_match_score"] == 90.0
    assert res_senior["stage1_match_score"] == 83.0

    # Senior candidate should have a significantly higher Hiring Priority Score
    assert res_senior["hiring_priority_score"] > res_fresher["hiring_priority_score"]
    assert res_senior["hiring_priority_score"] >= 70
    assert len(res_senior["priority_reasons"]) > 0

    # 2. Verify Candidate Comparator Ranking (v1.8.5 Hierarchical Technical Dominance)
    ranked = compare_candidates([eval_fresher, eval_senior])
    
    assert len(ranked) == 2
    # Candidate 1 (Fresher) ranks #1 due to dominant Stage 1 Technical Match (90.0% vs 83.0%)
    assert ranked[0]["candidate_name"] == "Fresher Candidate"
    assert ranked[0]["rank"] == 1
    assert ranked[0]["overall_score"] == 90.0

    # Candidate 2 (Senior) ranks #2 with Technical Dominance explanation
    assert ranked[1]["candidate_name"] == "Senior Professional"
    assert ranked[1]["rank"] == 2
    assert ranked[1]["overall_score"] == 83.0

def test_salary_not_in_ranking_calculation():
    base_eval = {
        "evaluation_id": "eval_sal_01",
        "personal_info": {"name": "Candidate A"},
        "overall_score": 80.0,
        "work_history": [{"role": "Developer", "dates": "2021 - Present", "description": "Built Python APIs"}]
    }

    eval_high_sal = dict(base_eval)
    eval_high_sal["raw_resume_text"] = "Current CTC: 30 LPA (2.5L/month)"

    eval_low_sal = dict(base_eval)
    eval_low_sal["raw_resume_text"] = "Current CTC: 5 LPA"

    score_high = compute_hiring_priority_score(eval_high_sal)["hiring_priority_score"]
    score_low = compute_hiring_priority_score(eval_low_sal)["hiring_priority_score"]

    # Salary does not alter priority score
    assert score_high == score_low

def test_stage1_prerequisite_threshold_gating():
    # Candidate with 20 years experience but 35% Stage 1 match score (irrelevant candidate)
    eval_unmatched_senior = {
        "evaluation_id": "eval_unmatched_01",
        "personal_info": {"name": "Senior Java Architect"},
        "overall_score": 35.0, # Below 45% minimum prerequisite threshold
        "work_history": [
            {"role": "Senior Java Architect", "dates": "2005 - Present", "description": "Built Java Enterprise applications."}
        ]
    }

    res = compute_hiring_priority_score(eval_unmatched_senior)
    
    assert res["prerequisite_met"] is False
    assert res["hiring_priority_score"] <= 20  # Capped due to unmatched Stage 1 prerequisites
    assert "Unmatched Prerequisites" in res["hiring_priority_tier"]
    assert "below the minimum prerequisite threshold" in res["priority_reasons"][0]

def test_employed_professional_evidence_pipeline():
    # Test candidate with 'experience' key in parsed_resume and certifications
    eval_employed = {
        "evaluation_id": "eval_emp_01",
        "overall_score": 82.0,
        "parsed_resume": {
            "experience": [
                {
                    "role": "Senior Software Engineer",
                    "company": "Innovate Tech",
                    "dates": "2019 - Present",
                    "description": "Led backend microservices deployment on AWS with Docker."
                }
            ],
            "certifications": [
                {"title": "AWS Certified Solutions Architect"}
            ]
        }
    }

    evidence = extract_candidate_evidence(eval_employed)
    assert len(evidence.professional_experience) == 1
    assert len(evidence.certifications) == 1

    res = compute_hiring_priority_score(eval_employed)
    
    # 1. Candidate must NOT be classified as entry level
    assert "Entry-level candidate profile" not in " ".join(res["priority_reasons"])
    
    # 2. Certifications must be recognized
    assert res["priority_factors"]["certifications_pts"] == 5.0
    assert any("certification" in r.lower() for r in res["priority_reasons"])
    
    # 3. Work experience must contribute to priority
    assert res["priority_factors"]["professional_experience_pts"] > 0
    assert res["hiring_priority_score"] >= 60
    assert res["hiring_priority_tier"] in ["Top Priority Interview", "Priority Interview", "Standard Review"]
