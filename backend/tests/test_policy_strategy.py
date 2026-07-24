import pytest
from app.agents.policy_engine import evaluate_policy
from app.agents.strategy import generate_strategy
from app.agents.decision_engine import run_decision_engine

# --- Policy Engine Tests ---
def test_policy_mandatory_skill_pass():
    scorer_out = {
        "overall_score": 85,
        "dimension_scores": {"skill_match": type("MockDim", (), {"score": 80})()},
        "evidence_states": {"MATCHED": ["Python"], "MISSING": []}
    }
    res = evaluate_policy(scorer_out, required_skills=["Python"])
    assert res["is_eligible"] is True
    assert len(res["critical_missing"]) == 0

def test_policy_mandatory_skill_fail():
    scorer_out = {
        "overall_score": 85,
        "dimension_scores": {"skill_match": type("MockDim", (), {"score": 80})()},
        "evidence_states": {"MATCHED": [], "MISSING": ["Python"]}
    }
    res = evaluate_policy(scorer_out, required_skills=["Python"])
    assert res["is_eligible"] is False
    assert "Python" in res["critical_missing"]

def test_policy_experience_gate():
    # Overall score passes, but experience is 0
    scorer_out = {
        "overall_score": 85,
        "dimension_scores": {
            "skill_match": type("MockDim", (), {"score": 80})(),
            "experience_quantity": type("MockDim", (), {"score": 0})()
        }
    }
    config = {"min_overall_score": 60, "min_skill_score": 50, "require_experience": True}
    res = evaluate_policy(scorer_out, config=config)
    assert res["is_eligible"] is False

def test_policy_threshold_override_bypass():
    scorer_out = {"overall_score": 20, "dimension_scores": {}}
    res = evaluate_policy(scorer_out, bypass_policy=True)
    assert res["is_eligible"] is True
    assert len(res["policy_overrides"]) > 0

# --- Strategy Tests ---
def test_strategy_strong_hire():
    res = generate_strategy({"overall_score": 95}, {"is_eligible": True})
    assert res["hiring_recommendation"] == "Strong Hire"

def test_strategy_hire():
    res = generate_strategy({"overall_score": 80}, {"is_eligible": True})
    assert res["hiring_recommendation"] == "Hire"

def test_strategy_reject_policy_failed():
    res = generate_strategy({"overall_score": 95}, {"is_eligible": False})
    assert res["hiring_recommendation"] == "Reject"

def test_strategy_review_and_reject_tiers():
    res_review = generate_strategy({"overall_score": 50}, {"is_eligible": True})
    assert res_review["hiring_recommendation"] == "Review"

    res_reject = generate_strategy({"overall_score": 30}, {"is_eligible": True})
    assert res_reject["hiring_recommendation"] == "Reject"

# --- Decision Engine Tests ---
def test_decision_engine_happy_path():
    parsed_resume = {
        "skills": {"languages": ["Python", "JavaScript"]},
        "hard_skills": ["Python", "FastAPI"],
        "work_history": [{"role": "Senior Backend Engineer", "description": "Python FastAPI APIs."}],
        "raw_resume_text": "Senior Backend Engineer with Python and FastAPI."
    }
    required = ["Python"]
    decision = run_decision_engine(parsed_resume, required)
    
    # Asserting pipeline flow without mutating inner scorers
    assert decision["policy_eligible"] is True
    assert decision["overall_score"] > 60
    assert decision["recommendation"]["hiring_recommendation"] in ["Strong Hire", "Hire", "Interview"]

def test_decision_engine_critical_skill_failure():
    parsed_resume = {
        "skills": {"languages": ["Java"]},
    }
    required = ["Python"]
    decision = run_decision_engine(parsed_resume, required)
    
    assert decision["policy_eligible"] is False
    assert decision["recommendation"]["hiring_recommendation"] == "Reject"
    assert "Python" in decision["recommendation_basis"]["critical_missing_skills"]
