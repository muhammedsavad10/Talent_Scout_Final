"""
TalentScout Enterprise v1.9.0 — Intelligent Recruiter Test Suite.
Validates:
1. Evidence Quality Intelligence: Keyword presence vs demonstrated engineering depth with measurable impact
2. Project Intelligence: Project type & maturity classification (CRUD Portfolio vs Production SaaS vs Enterprise Platform)
3. Employment Intelligence: Career progression, stability, and organizational context
4. Recruiter Reasoning Audit: 6 recruiter questions (Interview pitch, hiring risk, rejection factors)
5. Score Calibration: Realistic recruiter score distributions (preventing score inflation)
"""
import pytest
from app.core.evidence_quality import evaluate_evidence_quality
from app.core.project_intelligence import analyze_project_intelligence
from app.core.employment_intelligence import analyze_employment_intelligence
from app.core.recruiter_reasoning import generate_recruiter_reasoning
from app.core.score_calibration import calibrate_recruiter_score
from app.core.hiring_priority import compute_hiring_priority_score

def test_v1_9_0_evidence_quality_measurable_impact():
    # Keyword list resume text
    text_keyword = "React, Node.js, MongoDB, JavaScript"
    quality_kw = evaluate_evidence_quality(text_keyword)
    assert quality_kw.quality_multiplier == 1.00

    # High quality implementation text with measurable metrics
    text_impact = "Built scalable React dashboard serving 50,000 active users. Optimized MongoDB indexes reducing latency by 60% on AWS."
    quality_impact = evaluate_evidence_quality(text_impact)
    assert quality_impact.quality_multiplier > 1.20
    assert len(quality_impact.measurable_metrics) > 0

def test_v1_9_0_project_intelligence_classification():
    proj_crud = {"title": "Todo App", "description": "Basic CRUD app tutorial."}
    intel_crud = analyze_project_intelligence(proj_crud)
    assert intel_crud.project_type in ["CRUD Portfolio Project", "Technical Project"]

    proj_enterprise = {
        "title": "Delay2Decision",
        "description": "Enterprise microservices layover optimization agent using LangChain, Qdrant, and PyTorch.",
        "technologies": ["LangChain", "Qdrant", "PyTorch"]
    }
    intel_ent = analyze_project_intelligence(proj_enterprise)
    assert intel_ent.project_type == "Enterprise Platform"
    assert intel_ent.complexity_tier == "Enterprise Grade"
    assert intel_ent.maturity_score >= 90.0

def test_v1_9_0_employment_intelligence_trajectory():
    work_history = [
        {"role": "Senior Backend Architect", "company": "Tech Corp", "dates": "2020 - Present"},
        {"role": "Software Developer", "company": "Tech Corp", "dates": "2018 - 2020"}
    ]
    emp_intel = analyze_employment_intelligence(work_history)
    assert emp_intel.seniority_level == "Senior / Lead Architect"
    assert emp_intel.promotion_evidence is True

def test_v1_9_0_recruiter_reasoning_generation():
    reasoning = generate_recruiter_reasoning(
        candidate_name="Devadethan",
        stage1_score=93.2,
        hiring_priority_tier="Top Priority Interview",
        work_history=[{"role": "Senior Data Scientist", "company": "AI Corp"}],
        projects=[{"canonical_title": "Delay2Decision"}],
        skills=["Python", "PyTorch", "NLP"]
    )
    assert "93.2%" in reasoning.interview_pitch
    assert len(reasoning.supporting_evidence) > 0
    assert reasoning.uncertainty_reduction != ""

def test_v1_9_0_score_calibration():
    # Unearned >90 score without measurable evidence is calibrated down
    calibrated_unearned = calibrate_recruiter_score(raw_score=95.0, quality_multiplier=1.00, has_measurable_impact=False)
    assert calibrated_unearned < 90.0

    # Exceptional candidate with measurable evidence retains high score
    calibrated_earned = calibrate_recruiter_score(raw_score=95.0, quality_multiplier=1.35, has_measurable_impact=True, is_exceptional_evidence=True)
    assert calibrated_earned == 95.0
