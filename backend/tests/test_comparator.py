import pytest
from app.agents.comparator import compare_candidates
from pydantic import BaseModel

# Mock objects to represent Pydantic Models for defensive extraction test
class MockDimension(BaseModel):
    score: int
    
class MockDecisionEngine(BaseModel):
    dimension_scores: dict
    
class MockEval(BaseModel):
    overall_score: int
    evaluation_id: str
    personal_info: dict
    decision_engine: MockDecisionEngine

def test_comparator_one_candidate():
    evals = [{"overall_score": 85, "evaluation_id": "cand1"}]
    ranked = compare_candidates(evals)
    assert len(ranked) == 1
    assert ranked[0]["rank"] == 1
    assert ranked[0]["evaluation_id"] == "cand1"

def test_comparator_two_candidates():
    evals = [
        {"overall_score": 75, "evaluation_id": "cand1"},
        {"overall_score": 90, "evaluation_id": "cand2"}
    ]
    ranked = compare_candidates(evals)
    assert ranked[0]["evaluation_id"] == "cand2"
    assert ranked[0]["rank"] == 1
    assert ranked[1]["evaluation_id"] == "cand1"
    assert ranked[1]["rank"] == 2

def test_comparator_equal_scores():
    evals = [
        {"overall_score": 85, "evaluation_id": "cand1"},
        {"overall_score": 85, "evaluation_id": "cand2"}
    ]
    ranked = compare_candidates(evals)
    assert ranked[0]["overall_score"] == 85
    assert ranked[1]["overall_score"] == 85

def test_comparator_failed_candidate():
    evals = [
        {"overall_score": 90, "evaluation_id": "cand1"},
        {"overall_score": None, "evaluation_id": "cand2"} # Failed
    ]
    ranked = compare_candidates(evals)
    assert ranked[0]["evaluation_id"] == "cand1"
    assert ranked[1]["evaluation_id"] == "cand2"
    assert ranked[1]["rank"] == 999
    assert ranked[1]["recommendation_tier"] == "Failed"

def test_comparator_missing_dimensions():
    evals = [{"overall_score": 80, "evaluation_id": "cand1", "decision_engine": {}}]
    ranked = compare_candidates(evals)
    assert ranked[0]["skill_match"] == 0.0

def test_comparator_legacy_dictionary_input():
    evals = [
        {
            "overall_score": 85, 
            "evaluation_id": "dict_cand",
            "dimension_scores": {"skill_match": {"score": 90}}
        }
    ]
    ranked = compare_candidates(evals)
    assert ranked[0]["skill_match"] == 90.0

def test_comparator_reconstructed_model_input():
    dim = MockDimension(score=88)
    de = MockDecisionEngine(dimension_scores={"skill_match": dim})
    model = MockEval(
        overall_score=95, 
        evaluation_id="model_cand", 
        personal_info={"name": "Alice"},
        decision_engine=de
    )
    
    ranked = compare_candidates([model])
    assert ranked[0]["skill_match"] == 88.0
    assert ranked[0]["candidate_name"] == "Alice"
