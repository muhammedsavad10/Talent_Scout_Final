"""
Production Readiness Audit Unit Tests.
Verifies that the resume extraction pipeline:
1. Never fabricates candidate profiles, companies, projects, emails, or phone numbers.
2. Returns empty arrays for absent evidence instead of inventing synthetic data.
3. Contains no candidate-specific hardcoded rules or company special cases.
"""
import pytest
import json
from app.services.ai_gateway import _extract_deterministic_fallback_resume

def test_parser_never_invents_companies_or_projects():
    empty_resume_text = "Jane Doe\nSummary: Passionate software professional."
    result_str = _extract_deterministic_fallback_resume(empty_resume_text)
    data = json.loads(result_str)
    
    assert data["personal_info"]["name"] == "Jane Doe"
    assert data["personal_info"]["email"] is None
    assert data["personal_info"]["phone"] is None
    assert data["work_history"] == []
    assert data["projects"] == []
    assert data["education"] == []
    assert data["certifications"] == []

def test_parser_extracts_only_factual_evidence_present_in_text():
    resume_text = """
    Alice Walker
    Email: alice.walker@domain.com | Phone: +1 555-0123
    
    Experience
    Senior Backend Engineer at CloudCorp (2021 - Present)
    
    Certifications
    AWS Certified Solutions Architect
    """
    result_str = _extract_deterministic_fallback_resume(resume_text)
    data = json.loads(result_str)
    
    assert data["personal_info"]["name"] == "Alice Walker"
    assert data["personal_info"]["email"] == "alice.walker@domain.com"
    assert data["personal_info"]["phone"] == "+1 555-0123"
    assert len(data["work_history"]) == 1
    assert data["work_history"][0]["company"] == "CloudCorp"
    assert data["work_history"][0]["role"] == "Senior Backend Engineer"
    assert len(data["certifications"]) == 1
    assert data["certifications"][0]["vendor"] == "AWS"
    assert data["projects"] == []

def test_codebase_ai_gateway_contains_no_hardcoded_synthetic_companies():
    import inspect
    import app.services.ai_gateway as gateway_module
    
    source = inspect.getsource(gateway_module)
    forbidden_terms = ["Prevalent AI", "DifferentByte", "DataPull", "Nullclass", "Riss Technologies", "555-0199", "BS Computer Science"]
    for term in forbidden_terms:
        assert term not in source, f"Forbidden synthetic term '{term}' found in ai_gateway.py source code!"
