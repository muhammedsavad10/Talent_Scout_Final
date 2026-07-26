"""
TalentScout Enterprise v1.3 — Final Canonical API Integrity Test Suite.
Verifies single source of truth API serialization, elimination of dual metrics,
and non-contamination in candidate resumes (Muhammad & Adhil benchmarks).
"""
import pytest
import json
from app.agents.orchestrator import run_evaluation_pipeline
from app.core.consistency_validator import validate_api_response_consistency
from app.agents.comparator import compare_candidates

@pytest.mark.asyncio
async def test_end_to_end_single_source_of_truth_serialization():
    resume_text = """
    Muhammad Savad
    AI Engineer | Email: muhammad@domain.com
    
    EXPERIENCE
    Senior AI Engineer at TechCorp (2022 - Present)
    
    PROJECTS
    Delay2Decision
    Designed and developed real-time decision-support system using LangGraph, Qdrant, and FastAPI.
    
    CERTIFICATIONS
    AWS Certified Solutions Architect
    """
    
    res = await run_evaluation_pipeline(
        text=resume_text,
        candidate_id="eval_muhammad_v13",
        required_skills=["Python", "FastAPI", "Qdrant"],
        jd_text="Senior AI Engineer requiring Python, FastAPI, Qdrant"
    )
    
    assert res["status"] == "success"
    
    # 1. Dual Metric Verification: Root level MUST match hiring_priority level exactly
    hp_data = res["hiring_priority"]
    assert res["project_complexity"] == hp_data["project_complexity"]
    assert res["evidence_confidence"] == hp_data["evidence_confidence"]
    assert res["project_complexity"] > 0.0
    assert res["evidence_confidence"] >= 0.85
    
    # 2. Muhammad Resume Verification: Delay2Decision MUST NOT appear in work_history
    parsed_res = res["parsed_resume"]
    work_companies = [w["company"] for w in parsed_res.get("work_history", [])]
    assert "TechCorp" in work_companies
    assert "Delay2Decision" not in work_companies
    
    project_titles = [p["title"] for p in parsed_res.get("projects", [])]
    assert "Delay2Decision" in project_titles

@pytest.mark.asyncio
async def test_adhil_resume_project_bullets_never_become_certifications():
    adhil_resume = """
    Adhil Kumar
    Backend Engineer
    
    EXPERIENCE
    Backend Developer at SoftCorp (2021 - Present)
    Built microservices architecture using FastAPI and Docker.
    Designed AWS infrastructure and integrated Gemini AI pipelines.
    
    CERTIFICATIONS
    Google Cloud Foundations
    """
    
    res = await run_evaluation_pipeline(
        text=adhil_resume,
        candidate_id="eval_adhil_v13",
        required_skills=["Python", "FastAPI", "Docker"],
        jd_text="Backend Engineer needing Python, FastAPI, Docker"
    )
    
    assert res["status"] == "success"
    certs = res["certifications"]
    cert_names = [c["title"] if isinstance(c, dict) else str(c) for c in certs]
    
    assert any("google cloud" in c.lower() for c in cert_names)
    assert not any("microservices" in c.lower() for c in cert_names)
    assert not any("aws infrastructure" in c.lower() for c in cert_names)

def test_comparator_reads_canonical_metrics_with_zero_dual_metric_gap():
    eval_dict = {
        "overall_score": 88.0,
        "evaluation_id": "eval_comp_001",
        "personal_info": {"name": "David Miller"},
        "hiring_priority": {
            "hiring_priority_score": 90,
            "hiring_priority_tier": "Top Priority Interview",
            "project_complexity": 85.0,
            "evidence_confidence": 0.96
        }
    }
    
    ranked = compare_candidates([eval_dict])
    assert len(ranked) == 1
    assert ranked[0]["project_complexity"] == 85.0
    assert ranked[0]["evidence_confidence"] == 0.96
