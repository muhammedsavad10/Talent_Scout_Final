"""
Unit tests for Recommendation and Policy Engine Decision Architecture.
Verifies that high-scoring candidates with senior experience are NEVER disqualified/rejected.
"""
import pytest
from app.agents.stage1_evaluation import run_stage1_evaluation
from app.agents.stage2_intelligence import run_stage2_intelligence
from app.agents.policy_engine import evaluate_policy
from app.agents.decision_engine import run_decision_engine

@pytest.mark.asyncio
async def test_high_scoring_senior_candidate_not_disqualified_for_preferred_skills():
    resume_text = """
    John Doe
    Senior Machine Learning Engineer & Data Scientist (6.5 years experience)
    Architected and deployed production machine learning systems, deep learning models, and LLMs using PyTorch and TensorFlow.
    Engineered high-performance vector search pipelines using Pinecone and FAISS.
    Proficient in Python, Scikit-Learn, SQL, and Docker.
    """

    required_skills = ["Python", "Machine Learning", "PyTorch", "Power BI", "Agile", "Qdrant"]

    stage1_res = await run_stage1_evaluation(
        text=resume_text,
        candidate_id="cand_high_score_001",
        required_skills=required_skills,
        jd_text="Senior ML Engineer needing Python, Machine Learning, PyTorch, Power BI, Agile, Qdrant"
    )

    assert stage1_res["status"] == "success"
    # Score should be high (>= 75%)
    assert stage1_res["overall_score"] >= 75

    # Policy validation MUST be eligible (is_eligible = True)
    policy_val = stage1_res["policy_validation"]
    assert policy_val["policy_eligible"] is True
    assert len(policy_val["critical_missing_skills"]) == 0

    # Stage 2 Intelligence check
    stage2_res = run_stage2_intelligence(stage1_res)
    hiring_rec = stage2_res["recommendation"]["hiring_recommendation"]
    assert hiring_rec in ["Strong Hire", "Hire", "Interview", "Recommended for Interview", "Unknown"]
    assert hiring_rec not in ["Reject", "Disqualified"]

    # Decision trace check
    trace = stage1_res.get("decision_trace", {})
    assert trace.get("overall_score") == stage1_res["overall_score"]
    assert trace.get("policy_decision") == "PASS"
    assert trace.get("recommendation") == hiring_rec
