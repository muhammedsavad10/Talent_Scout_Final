"""
Unit tests for Independent Explicit Keyword Matching (40% ATS) and Semantic Similarity (60% AI).
Verifies that explicit score is strictly literal while semantic score evaluates transferable competence.
"""
import pytest
from app.agents.stage1_evaluation import run_stage1_evaluation
from app.agents.stage2_intelligence import run_stage2_intelligence
from app.agents.scorer import run_scorer, collect_evidence

def test_collect_evidence_strict_literal_ats():
    parsed_resume = {
        "raw_resume_text": "John Doe - Python Developer with Tableau and Pinecone.",
        "skills": {"languages": ["Python"], "tools": ["Tableau", "Pinecone"]},
        "hard_skills": ["Python", "Tableau", "Pinecone"]
    }
    required_skills = ["Python", "Power BI", "Qdrant", "NLP"]

    evidence = collect_evidence(parsed_resume, required_skills)
    assert evidence["EXPLICITLY_MATCHED"] == ["Python"]
    assert set(evidence["EXPLICITLY_MISSING"]) == {"Power BI", "Qdrant", "NLP"}

@pytest.mark.asyncio
async def test_explicit_semantic_score_independence():
    resume_text = """
    Alice Smith
    Senior AI Engineer (5+ years experience)
    Engineered production vector search pipelines using Pinecone and FAISS.
    Trained BERT and LLM models for text classification and RAG.
    Proficient in Python and PyTorch.
    """

    required_skills = ["Python", "Power BI", "Qdrant", "NLP"]

    stage1_res = await run_stage1_evaluation(
        text=resume_text,
        candidate_id="cand_sep_001",
        required_skills=required_skills,
        jd_text="AI Engineer requiring Python, Power BI, Qdrant, NLP"
    )

    assert stage1_res["status"] == "success"

    # Explicit score must be strictly literal ATS matching (1/4 skills = 25%)
    assert stage1_res["explicit_keyword_score"] == 25
    assert stage1_res["explicitly_matched_skills"] == ["Python"]
    assert set(stage1_res["explicitly_missing_skills"]) == {"Power BI", "Qdrant", "NLP"}

    # Semantic similarity score must be high (>= 85%) due to Pinecone (Qdrant equiv) and BERT/LLM (NLP concept)
    assert stage1_res["semantic_similarity_score"] >= 85

    # Overall score calculation: round(25 * 0.40 + semantic * 0.60)
    expected_overall = int(round((25 * 0.40) + (stage1_res["semantic_similarity_score"] * 0.60)))
    assert stage1_res["overall_score"] == expected_overall

    # Policy validation must be eligible
    assert stage1_res["policy_validation"]["policy_eligible"] is True

    # Semantic evidence must be present
    assert len(stage1_res.get("semantic_evidence", [])) > 0

    # Stage 2 Intelligence check
    stage2_res = run_stage2_intelligence(stage1_res)
    assert stage2_res["recommendation"]["hiring_recommendation"] not in ["Reject", "Disqualified"]
