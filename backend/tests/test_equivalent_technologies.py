"""
Unit tests for Equivalent Technology & Concept Inference Engine.
Verifies conservative transferable skill matching and concept inferences.
"""
import pytest
from app.core.prerequisite_engine import (
    find_equivalent_technology,
    check_concept_support,
    infer_foundational_skills
)
from app.agents.stage1_evaluation import run_stage1_evaluation
from app.agents.stage2_intelligence import run_stage2_intelligence

def test_equivalent_vector_databases():
    candidate_skills = {"pinecone", "faiss", "pytorch", "fastapi"}
    equivalent_matches = find_equivalent_technology("Qdrant", candidate_skills)
    assert len(equivalent_matches) > 0
    assert "pinecone" in equivalent_matches or "faiss" in equivalent_matches

def test_conservative_safeguard_bi_tools_not_equivalent():
    candidate_skills = {"power bi", "sql", "excel"}
    equivalent_matches = find_equivalent_technology("Tableau", candidate_skills)
    # Power BI and Tableau are intentionally NOT mapped as equivalents
    assert len(equivalent_matches) == 0

def test_concept_support_feature_engineering_and_nlp():
    cand_skills = {"scikit-learn", "xgboost", "transformers", "bert", "llms"}
    
    fe_support = check_concept_support("Feature Engineering", cand_skills)
    assert len(fe_support) >= 2
    assert any("scikit-learn" in s.lower() for s in fe_support)
    
    nlp_support = check_concept_support("NLP", cand_skills)
    assert len(nlp_support) >= 2
    assert any("transformers" in s.lower() for s in nlp_support)

@pytest.mark.asyncio
async def test_candidate_eval_with_equivalent_vector_db_and_concepts():
    resume_text = """
    Alice Smith
    Senior Data Scientist & Machine Learning Engineer (5+ years experience)
    Built production recommendation systems using PyTorch, Scikit-Learn, and XGBoost.
    Engineered vector search pipelines using Pinecone and FAISS.
    Trained BERT and LLM models for text classification and RAG.
    """

    required_skills = ["Python", "PyTorch", "Feature Engineering", "NLP", "Qdrant"]

    stage1_res = await run_stage1_evaluation(
        text=resume_text,
        candidate_id="cand_equiv_123",
        required_skills=required_skills,
        jd_text="Senior ML Engineer needing Python, PyTorch, Feature Engineering, NLP, Qdrant"
    )

    assert stage1_res["status"] == "success"
    evidence_states = stage1_res["evidence_states"]
    
    # Python -> Inferred foundation via PyTorch
    # Feature Engineering & NLP -> Inferred concepts via Scikit-Learn/XGBoost/BERT/LLMs
    # Qdrant -> Equivalent technology match via Pinecone/FAISS
    assert "Python" in evidence_states.get("INFERRED", [])
    assert "Feature Engineering" in evidence_states.get("INFERRED", [])
    assert "NLP" in evidence_states.get("INFERRED", [])
    assert "Qdrant" in evidence_states.get("EQUIVALENT", [])

    # Stage 1A: Literal ATS Explicit Match Score (1/5 skills = 20%)
    assert stage1_res["explicit_keyword_score"] == 20
    assert stage1_res["explicitly_matched_skills"] == ["PyTorch"]
    
    # Stage 1B: AI Semantic Similarity Score (Inferred concepts & equivalent vector DB)
    assert stage1_res["semantic_similarity_score"] >= 85
    assert stage1_res["policy_validation"]["policy_eligible"] is True

    stage2_res = run_stage2_intelligence(stage1_res)
    hiring_rec = stage2_res["recommendation"]["hiring_recommendation"]
    assert hiring_rec != "Reject"
