"""
Unit tests for Experience-Aware Skill Penalty & Seniority Mitigation Engine.
Verifies that experienced candidates omitting foundational skills are NOT rejected.
"""
import pytest
from app.agents.stage1_evaluation import run_stage1_evaluation
from app.agents.stage2_intelligence import run_stage2_intelligence
from app.agents.policy_engine import evaluate_policy
from app.core.prerequisite_engine import is_senior_candidate, infer_foundational_skills, classify_skill_category

def test_senior_candidate_detection():
    senior_resume = {
        "work_history": [
            {"role": "Senior Machine Learning Engineer", "company": "Tech Corp", "description": "Developed ML systems with TensorFlow."},
            {"role": "ML Engineer", "company": "AI Labs", "description": "Built FastAPI microservices."}
        ]
    }
    assert is_senior_candidate(senior_resume) is True

def test_skill_category_classification():
    assert classify_skill_category("Python") == "Foundational"
    assert classify_skill_category("Git") == "Foundational"
    assert classify_skill_category("Docker") == "Foundational"
    assert classify_skill_category("TensorFlow") == "Critical"
    assert classify_skill_category("PyTorch") == "Critical"

@pytest.mark.asyncio
async def test_senior_ml_engineer_not_rejected_for_omitted_python():
    resume_text = """
    John Doe
    Senior Machine Learning Engineer (6+ years experience)
    Built production deep learning models using PyTorch, TensorFlow, and LLMs.
    Architected high-throughput microservices with FastAPI and Docker.
    """
    
    stage1_res = await run_stage1_evaluation(
        text=resume_text,
        candidate_id="senior_cand_001",
        required_skills=["Python", "PyTorch", "FastAPI", "Docker", "NumPy"],
        jd_text="Senior Machine Learning Engineer requiring Python, PyTorch, FastAPI, Docker, NumPy"
    )

    assert stage1_res["status"] == "success"
    # Stage 1A: Literal ATS Explicit keyword match score (4/5 skills = 80% or 67%)
    assert stage1_res["explicit_keyword_score"] >= 60
    # Stage 1B: AI Semantic similarity score >= 70%
    assert stage1_res["semantic_similarity_score"] >= 70
    assert stage1_res["overall_score"] >= 70

    # Policy validation must mark candidate as eligible (NO policy rejection)
    policy = stage1_res["policy_validation"]
    assert policy["policy_eligible"] is True
    assert len(policy["critical_missing_skills"]) == 0

    # Stage 2 Recruiter Intelligence check
    stage2_res = run_stage2_intelligence(stage1_res)
    hiring_rec = stage2_res["recommendation"]["hiring_recommendation"]
    assert hiring_rec in ["Recommended for Interview", "Hire", "Strong Hire", "Interview", "Unknown"]
    assert hiring_rec != "Reject"
