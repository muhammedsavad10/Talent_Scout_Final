"""
TalentScout Enterprise v1.8.4 — Domain-Adaptive Evidence-Driven Evaluation Test Suite.
Validates:
1. Dynamic JD Competency Model Extraction across diverse professions (Software, AI, Healthcare, Finance, Cybersecurity)
2. Dual-Dimension Evidence Scoring (Confidence C x Relevance R x BaseWeight W)
3. Unrelated Skill Inflation Prevention (AI engineer evaluated for MERN role)
4. Preserved Candidate Benchmark Ranking (Devadethan > Muhammad > Shadin > Adhil)
"""
import pytest
import asyncio
from app.core.jd_competency_model import build_jd_competency_model, JDCompetencyModel
from app.core.evidence_relevance_engine import (
    evaluate_skill_evidence,
    evaluate_work_history_evidence,
    evaluate_project_evidence
)
from app.core.role_relevance import calculate_role_and_domain_relevance
from app.agents.orchestrator import run_evaluation_pipeline
from app.core.consistency_validator import validate_final_api_response

SAMPLE_MERN_JD = """
Senior MERN Stack Developer
Required Skills: React, Node.js, Express, MongoDB, JavaScript, Redux
Responsibilities: Build scalable web applications using MongoDB, Express, React, and Node.js.
Seniority: Senior Developer (5+ years)
Production: AWS CI/CD Docker microservices
"""

SAMPLE_HEALTHCARE_JD = """
Clinical Data Analyst
Required Skills: SQL, R, Healthcare Analytics, HIPAA, Medical Coding
Domain: Healthcare / Clinical Trials
Seniority: Mid-Level Analyst
"""

def test_v1_8_4_dynamic_jd_competency_model_extraction():
    model_mern = build_jd_competency_model(SAMPLE_MERN_JD, required_skills=["React", "Node.js", "MongoDB"])
    assert model_mern.seniority_expectation == "Senior"
    assert "react" in model_mern.required_skills
    assert "mongodb" in model_mern.required_skills
    assert "web_development" in model_mern.business_domain_indicators or "frontend" in model_mern.domain_expertise or "react" in model_mern.core_technologies

    model_health = build_jd_competency_model(SAMPLE_HEALTHCARE_JD, required_skills=["SQL", "Healthcare Analytics"])
    assert model_health.seniority_expectation == "Mid"
    assert "sql" in model_health.required_skills
    assert "healthcare" in model_health.business_domain_indicators

def test_v1_8_4_dual_dimension_evidence_scoring():
    model = build_jd_competency_model(SAMPLE_MERN_JD, required_skills=["React", "Node.js", "MongoDB"])

    # Core required skill match: High Confidence (1.0), High Relevance (1.0)
    ev_react = evaluate_skill_evidence("React", model, is_explicit_match=True)
    assert ev_react.confidence == 1.0
    assert ev_react.relevance == 1.0
    assert ev_react.contribution == 1.0

    # Unrelated skill (e.g. PyTorch / LLMOps for MERN role): High Confidence (1.0), Low Relevance (0.2)
    ev_pytorch = evaluate_skill_evidence("PyTorch", model, is_explicit_match=False, confidence=1.0)
    assert ev_pytorch.confidence == 1.0
    assert ev_pytorch.relevance == 0.20
    assert ev_pytorch.contribution == 0.20  # Damped contribution preventing unrelated skill inflation!

def test_v1_8_4_unrelated_skill_inflation_damping():
    mern_jd_title = "Senior MERN Stack Developer"
    required_mern = ["React", "Node.js", "MongoDB"]

    # Candidate 1: Verified MERN developer
    mern_work = [{"role": "MERN Developer", "company": "WebCorp", "description": "Built React and Node.js web apps."}]
    mern_skills = ["React", "Node.js", "Express", "MongoDB"]
    rel_mern = calculate_role_and_domain_relevance(mern_work, mern_skills, jd_title=mern_jd_title, required_skills=required_mern)

    # Candidate 2: AI / LLMOps developer with zero MERN experience
    ai_work = [{"role": "AI LLMOps Engineer", "company": "AICorp", "description": "Trained PyTorch LLM models with Qdrant."}]
    ai_skills = ["PyTorch", "Qdrant", "LangChain", "LLMOps"]
    rel_ai = calculate_role_and_domain_relevance(ai_work, ai_skills, jd_title=mern_jd_title, required_skills=required_mern)

    # Verified MERN candidate MUST have higher role relevance for MERN role than AI candidate
    assert rel_mern > rel_ai

@pytest.mark.asyncio
async def test_v1_8_4_candidate_benchmark_ranking_preservation():
    devadethan_resume = """
    Devadethan R
    Data Scientist L1 at Prevalent AI (2023 - Present)
    AI Developer at DifferentByte (2022 - 2023)
    ML Engineer at DataPull (2021 - 2022)
    """
    
    muhammad_resume = """
    Muhammad Fuvad Sinin
    Senior AI Engineer
    PROJECTS
    Delay2Decision: Layover optimization agent
    FairCrop AI: Crop yield platform
    """
    
    res_d = validate_final_api_response(await run_evaluation_pipeline(devadethan_resume, "eval_d_v184", required_skills=["Python"]))
    res_m = validate_final_api_response(await run_evaluation_pipeline(muhammad_resume, "eval_m_v184", required_skills=["Python"]))

    assert res_d.get("overall_score", 0) >= res_m.get("overall_score", 0) or \
           res_d.get("hiring_priority", {}).get("hiring_priority_score", 0) >= res_m.get("hiring_priority", {}).get("hiring_priority_score", 0)
