"""
Unit tests for Deterministic Foundational Skill Inference Engine.
"""
from app.core.prerequisite_engine import infer_foundational_skills, get_prerequisites_for_skill
from app.agents.scorer import run_scorer, collect_evidence

def test_prerequisite_lookup():
    assert "Python" in get_prerequisites_for_skill("PyTorch")
    assert "Python" in get_prerequisites_for_skill("TensorFlow")
    assert "Docker" in get_prerequisites_for_skill("Kubernetes")
    assert "JavaScript" in get_prerequisites_for_skill("React")

def test_inference_engine_gives_credit_for_foundations():
    # Resume explicitly has PyTorch and FastAPI, but omits Python
    candidate_skills = {"PyTorch", "FastAPI", "SQL"}
    required_skills = ["Python", "PyTorch", "SQL"]

    res = infer_foundational_skills(candidate_skills, required_skills)

    assert "PyTorch" in res["MATCHED"]
    assert "SQL" in res["MATCHED"]
    assert "Python" in res["INFERRED"]
    assert "Python" in res["inferred_details"]
    assert res["inferred_details"]["Python"]["status"] == "INFERRED"
    assert "PyTorch" in res["inferred_details"]["Python"]["triggered_by"] or "FastAPI" in res["inferred_details"]["Python"]["triggered_by"]

def test_scorer_applies_inference_credit_weight():
    parsed_resume = {
        "hard_skills": ["PyTorch", "FastAPI", "SQL"],
        "raw_resume_text": "Experienced ML Engineer working with PyTorch models and FastAPI microservices."
    }
    required = ["Python", "PyTorch", "SQL"]

    evidence = collect_evidence(parsed_resume, required)
    assert "Python" in evidence["INFERRED"]

    result = run_scorer(parsed_resume, required, jd_text="Looking for ML Engineer with Python, PyTorch, SQL")
    
    # Stage 1A: Literal ATS Explicit score = 67% (2/3 skills: PyTorch, SQL)
    explicit_score = result["dimension_scores"]["explicit_keyword_match"].score
    assert explicit_score == 67
    
    # Stage 1B: Section-Aware AI Semantic Similarity Score >= 60% due to Python prerequisite inference
    semantic_score = result["dimension_scores"]["semantic_similarity"].score
    assert semantic_score >= 60

def test_safeguard_no_unrelated_inference():
    # TensorFlow should NOT infer unrelated skills like AWS or React
    candidate_skills = {"TensorFlow"}
    required_skills = ["AWS", "React", "Kafka"]

    res = infer_foundational_skills(candidate_skills, required_skills)

    assert len(res["INFERRED"]) == 0
    assert "AWS" in res["MISSING"]
    assert "React" in res["MISSING"]
    assert "Kafka" in res["MISSING"]
