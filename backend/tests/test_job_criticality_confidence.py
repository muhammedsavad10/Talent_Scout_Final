"""
Unit tests for Job Criticality Calibration, Recommendation Confidence Engine, and Natural Recruiter Phrasing.
"""
import pytest
from app.core.criticality_engine import determine_job_criticality
from app.agents.policy_engine import evaluate_policy
from app.agents.strategy import generate_strategy, evaluate_recommendation_confidence

def test_job_criticality_resolution():
    junior_jd = "Looking for Junior Python Developer with 0-1 years experience in Django."
    senior_jd = "Principal AI Scientist needing 8+ years experience leading LLM and Deep Learning architecture."
    
    crit_jr = determine_job_criticality(junior_jd, "Junior Developer")
    assert crit_jr["criticality_level"] == "Junior"
    assert crit_jr["thresholds"]["hire"] == 70

    crit_sr = determine_job_criticality(senior_jd, "Principal AI Scientist")
    assert crit_sr["criticality_level"] == "Senior"
    assert crit_sr["thresholds"]["hire"] == 80

def test_recommendation_differing_by_job_criticality():
    scorer_out = {
        "overall_score": 78,
        "dimension_scores": {
            "explicit_keyword_match": type("MockDim", (), {"score": 60})(),
            "semantic_similarity": type("MockDim", (), {"score": 90})()
        },
        "evidence_states": {"EXPLICITLY_MATCHED": ["Python"], "EXPLICITLY_MISSING": ["Power BI"]}
    }

    # Junior Role evaluation for overall_score 78% -> Hire (>= 70%)
    policy_jr = evaluate_policy(scorer_out, jd_text="Junior Developer requiring Python and Power BI")
    strat_jr = generate_strategy(scorer_out, policy_jr)
    assert strat_jr["hiring_recommendation"] == "Hire"

    # Senior Role evaluation for overall_score 78% -> Interview (>= 65%, but < 80% for Senior Hire)
    policy_sr = evaluate_policy(scorer_out, jd_text="Senior Architect requiring Python and Power BI")
    strat_sr = generate_strategy(scorer_out, policy_sr)
    assert strat_sr["hiring_recommendation"] == "Interview"

def test_recommendation_confidence_engine():
    conf_high = evaluate_recommendation_confidence(
        overall_score=85,
        semantic_score=92,
        explicit_score=70,
        is_eligible=True,
        critical_missing=[]
    )
    assert conf_high["level"] == "High"

    conf_med = evaluate_recommendation_confidence(
        overall_score=68,
        semantic_score=75,
        explicit_score=50,
        is_eligible=True,
        critical_missing=[]
    )
    assert conf_med["level"] == "Medium"

def test_natural_recruiter_phrasing():
    scorer_out = {
        "overall_score": 82,
        "dimension_scores": {
            "explicit_keyword_match": type("MockDim", (), {"score": 50})(),
            "semantic_similarity": type("MockDim", (), {"score": 95})()
        },
        "evidence_states": {"EXPLICITLY_MATCHED": ["Python"], "MISSING": ["Power BI", "Agile"]}
    }
    policy_res = evaluate_policy(scorer_out, required_skills=["Python", "Power BI", "Agile"])
    strat_res = generate_strategy(scorer_out, policy_res)

    reasoning_text = strat_res["recommendation_basis"]["reasoning"]
    # Verify robotic negative phrasing is absent
    assert "did not trigger policy rejection" not in reasoning_text
    # Verify clean recruiter phrasing is present
    assert "factored into the weighted score but do not disqualify" in reasoning_text or "satisfies core technical requirements" in reasoning_text
