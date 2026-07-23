import pytest
from app.agents.scorer import run_scorer, collect_evidence, score_dimension

def test_scorer_perfect_candidate():
    parsed_resume = {
        "skills": {"languages": ["Python", "JavaScript"]},
        "hard_skills": ["FastAPI", "React"],
        "work_history": [
            {"role": "Senior Engineer", "description": "Developed backend APIs using FastAPI and Python for three years in a production environment."},
            {"role": "Backend Engineer", "description": "Built reactive web applications and microservices using React and JavaScript technologies."},
            {"role": "Software Developer", "description": "Deployed cloud native services on AWS using Docker containers and Kubernetes orchestrators."}
        ] # 6 years approx
    }
    required = ["Python", "FastAPI"]
    
    result = run_scorer(parsed_resume, required)
    assert result["overall_score"] > 80
    assert "Python" in result["evidence_states"]["MATCHED"]
    assert "FastAPI" in result["evidence_states"]["MATCHED"]
    assert result["dimension_scores"]["skill_match"].score == 100

def test_scorer_partial_match():
    parsed_resume = {
        "skills": {"languages": ["Python"]},
        "work_history": [{}]
    }
    required = ["Python", "FastAPI"]
    
    result = run_scorer(parsed_resume, required)
    assert "Python" in result["evidence_states"]["MATCHED"]
    assert "FastAPI" in result["evidence_states"]["MISSING"]
    # 1 matched, 1 missing -> 50%
    assert result["dimension_scores"]["skill_match"].score == 50

def test_scorer_zero_match():
    parsed_resume = {
        "skills": {"languages": ["Java"]},
        "work_history": []
    }
    required = ["Python", "FastAPI"]
    
    result = run_scorer(parsed_resume, required)
    assert len(result["evidence_states"]["MATCHED"]) == 0
    assert len(result["evidence_states"]["MISSING"]) == 2
    assert result["dimension_scores"]["skill_match"].score == 0
    assert result["dimension_scores"]["experience_quantity"].score == 0

def test_scorer_missing_optional_skills():
    # If no required skills are passed, skill match is 100
    parsed_resume = {"skills": {}, "work_history": []}
    required = []
    
    result = run_scorer(parsed_resume, required)
    assert result["dimension_scores"]["skill_match"].score == 100

def test_scorer_duplicate_skills():
    parsed_resume = {
        "hard_skills": ["Python", "python", "PYTHON"]
    }
    required = ["Python"]
    
    evidence = collect_evidence(parsed_resume, required)
    assert "Python" in evidence["MATCHED"]
    assert len(evidence["MATCHED"]) == 1

def test_scorer_contradictory_evidence():
    # Deterministic stub doesn't do deep contradiction inference without LLM,
    # but we test the explicit states are maintained and passed through.
    parsed_resume = {}
    required = ["Python"]
    result = run_scorer(parsed_resume, required)
    
    states = result["evidence_states"]
    assert "MATCHED" in states
    assert "INFERRED" in states
    assert "MISSING" in states
    assert "CONTRADICTED" in states
