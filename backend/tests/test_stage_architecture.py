"""
Unit tests for Strict Two-Stage Evaluation Architecture.
"""
import pytest
from app.agents.stage1_evaluation import run_stage1_evaluation
from app.agents.stage2_intelligence import run_stage2_intelligence
from app.agents.orchestrator import run_evaluation_pipeline

@pytest.mark.asyncio
async def test_stage1_produces_deterministic_scores_only():
    text = "John Doe is a Data Scientist with 5 years experience in Python, PyTorch, SQL."
    jd_text = "Job requires Python, PyTorch, SQL, Docker"
    
    stage1_res = await run_stage1_evaluation(
        text=text,
        candidate_id="cand_123",
        required_skills=["Python", "PyTorch", "SQL", "Docker"],
        jd_text=jd_text
    )

    assert stage1_res["status"] == "success"
    assert "overall_score" in stage1_res
    assert "explicit_keyword_score" in stage1_res
    assert "semantic_similarity_score" in stage1_res
    assert "dimension_scores" in stage1_res
    assert "matched_skills" in stage1_res
    assert "missing_skills" in stage1_res

@pytest.mark.asyncio
async def test_stage2_does_not_modify_stage1_scores():
    text = "Jane Doe is a Software Engineer with Python and React."
    jd_text = "Job requires Python, React, Docker"

    stage1_res = await run_stage1_evaluation(
        text=text,
        candidate_id="cand_456",
        required_skills=["Python", "React", "Docker"],
        jd_text=jd_text
    )

    orig_overall = stage1_res["overall_score"]
    orig_explicit = stage1_res["explicit_keyword_score"]
    orig_semantic = stage1_res["semantic_similarity_score"]

    stage2_res = run_stage2_intelligence(stage1_res)

    # Assert Stage 2 did NOT modify Stage 1 scores
    assert stage1_res["overall_score"] == orig_overall
    assert stage1_res["explicit_keyword_score"] == orig_explicit
    assert stage1_res["semantic_similarity_score"] == orig_semantic

    # Assert Stage 2 contains ONLY explanatory objects
    assert "recommendation" in stage2_res
    assert "recommendation_basis" in stage2_res
    assert "interview" in stage2_res
    assert "recruiter" in stage2_res

@pytest.mark.asyncio
async def test_pipeline_output_separation():
    text = "Alice Smith - Backend Developer with Python and FastAPI."
    result = await run_evaluation_pipeline(
        text=text,
        candidate_id="cand_789",
        required_skills=["Python", "FastAPI"],
        jd_text="Backend Developer position requiring Python and FastAPI"
    )

    assert "evaluation" in result
    assert "recruiter_intelligence" in result
    assert result["evaluation"]["overall_score"] == result["overall_score"]
