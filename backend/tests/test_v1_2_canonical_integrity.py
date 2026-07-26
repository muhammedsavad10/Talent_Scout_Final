"""
TalentScout Enterprise v1.2 — Canonical Pipeline Integrity & Single Source of Truth Test Suite.
Verifies CanonicalResume single source of truth, non-zero evidence_confidence,
dynamic project_complexity calculation, and automatic consistency validation.
"""
import pytest
from app.models.canonical_resume import CanonicalResume
from app.core.consistency_validator import calculate_project_complexity, validate_canonical_resume_consistency
from app.core.hiring_priority import compute_hiring_priority_score

def test_canonical_resume_creation_and_fields():
    data = {
        "personal_info": {"name": "Alice Smith", "email": "alice@domain.com"},
        "work_history": [{"company": "TechCorp", "role": "Senior AI Engineer", "dates": "2021 - Present"}],
        "projects": [{"title": "Delay2Decision", "description": "Built LangGraph and Kubernetes AI Orchestrator"}],
        "certifications": [{"vendor": "AWS", "title": "AWS Certified Solutions Architect"}]
    }
    canonical = CanonicalResume.from_dict(data)
    assert canonical.candidate_name == "Alice Smith"
    assert len(canonical.work_history) == 1
    assert len(canonical.projects) == 1
    assert len(canonical.certifications) == 1

def test_project_complexity_calculation_is_dynamic_and_nonzero():
    projects = [{"title": "Agentic AI Orchestrator", "description": "Built multi-agent AI system using LangGraph, Kubernetes, PySpark, FastAPI, and Qdrant RAG."}]
    complexity = calculate_project_complexity(projects, "Built multi-agent AI system using LangGraph, Kubernetes, PySpark, FastAPI, and Qdrant RAG.")
    assert complexity >= 75.0

def test_consistency_validator_purges_project_from_work_history():
    data = {
        "personal_info": {"name": "Bob Jones"},
        "work_history": [
            {"company": "RealCorp", "role": "Senior Engineer"},
            {"company": "Delay2Decision", "role": "Designed real-time decision support system"}
        ],
        "projects": [{"title": "Delay2Decision", "description": "Decision support project"}]
    }
    canonical = CanonicalResume.from_dict(data)
    validated = validate_canonical_resume_consistency(canonical)
    
    companies = [w.company for w in validated.work_history]
    assert "RealCorp" in companies
    assert "Delay2Decision" not in companies
    assert validated.evidence_confidence >= 0.85
    assert validated.project_complexity > 0.0

def test_compute_hiring_priority_returns_nonzero_confidence_and_complexity():
    eval_payload = {
        "overall_score": 85.0,
        "parsed_resume": {
            "personal_info": {"name": "Charlie Brown"},
            "work_history": [{"company": "DataCorp", "role": "Data Scientist", "dates": "2020 - Present"}],
            "projects": [{"title": "ETL RAG Pipeline", "description": "High-throughput vector search pipeline using Qdrant, Docker, FastAPI."}],
            "certifications": [{"vendor": "Google", "title": "Google AI Essentials"}]
        }
    }
    res = compute_hiring_priority_score(eval_payload)
    assert res["evidence_confidence"] >= 0.85
    assert res["project_complexity"] > 0.0
    assert res["professional_profile"]["evidence_confidence"] >= 0.85
    assert res["professional_profile"]["project_complexity"] > 0.0
