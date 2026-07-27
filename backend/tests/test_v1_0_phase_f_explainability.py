"""
TalentScout Enterprise Version 1.0 — Phase F Explainability & Operational Diagnostics Test Suite.
Validates structured recruiter reasoning payload generation, evidence lineage tracking, and operational diagnostics.
Does NOT modify or alter AI scoring formulas or ranking order.
"""
import pytest
from app.core.recruiter_reasoning import generate_recruiter_reasoning, RecruiterReasoningAudit

def test_phase_f_recruiter_reasoning_payload_structure():
    """Verify recruiter reasoning simulator produces clean structured diagnostic audit payload."""
    audit = generate_recruiter_reasoning(
        candidate_name="Muhammad",
        stage1_score=92.5,
        hiring_priority_tier="FAST_TRACK",
        work_history=[{"role": "Senior Data Scientist", "company": "Prevalent AI"}],
        projects=[{"canonical_title": "Delay2Decision"}],
        skills=["Python", "PyTorch", "NLP", "Qdrant"],
        missing_skills=[]
    )
    
    payload = audit.to_dict()
    assert payload["candidate_name"] == "Muhammad"
    assert "92.5%" in payload["interview_pitch"]
    assert "Prevalent AI" in payload["supporting_evidence"][0]
    assert "Delay2Decision" in payload["supporting_evidence"][1]
    assert len(payload["biggest_hiring_risk"]) > 0

def test_phase_f_recruiter_reasoning_missing_skill_diagnostics():
    """Verify missing required skills trigger clear contradictory evidence diagnostics."""
    audit = generate_recruiter_reasoning(
        candidate_name="Alice",
        stage1_score=65.0,
        hiring_priority_tier="EXAMINE",
        work_history=[{"role": "Frontend Developer", "company": "TechCorp"}],
        projects=[],
        skills=["JavaScript", "React"],
        missing_skills=["Kubernetes", "Go"]
    )
    
    payload = audit.to_dict()
    assert "Missing explicit evidence" in payload["rejection_risk"]
    assert "Kubernetes" in payload["contradictory_evidence"][0]
