"""
Regression Test Suite for TalentScout Enterprise Priority 1 Production Validation Fixes.
"""
import pytest
from app.agents.comparator import compare_candidates, candidate_comparator_key
from app.core.resume_validator import validate_is_resume
from app.agents.stage1_evaluation import _generate_career_timeline

def test_two_phase_candidate_ranking_architecture():
    """
    Verifies that an experienced data scientist with high Phase 2 Recruiter Priority Score
    outranks a fresher who has slightly higher raw text keyword density.
    """
    fresher_candidate = {
        "candidate_id": "cand_fresher",
        "personal_info": {"name": "Fresher Candidate"},
        "overall_score": 85.0,  # High keyword match score
        "hiring_priority_score": 60.0,
        "hiring_priority": {"hiring_priority_score": 60.0},
        "evidence_confidence": 0.90,
        "experience_quality": 30.0
    }

    experienced_candidate = {
        "candidate_id": "cand_senior",
        "personal_info": {"name": "Experienced Data Scientist"},
        "overall_score": 80.0,  # Slightly lower keyword density
        "hiring_priority_score": 90.0,
        "hiring_priority": {"hiring_priority_score": 90.0},
        "evidence_confidence": 0.98,
        "experience_quality": 95.0
    }

    # Comparator key returns -1 if candidate_a should precede candidate_b
    comp_result = candidate_comparator_key(experienced_candidate, fresher_candidate)
    assert comp_result == -1, "Experienced candidate must outrank fresher candidate."

    ranked = compare_candidates([fresher_candidate, experienced_candidate])
    assert ranked[0]["candidate_name"] == "Experienced Data Scientist"
    assert ranked[1]["candidate_name"] == "Fresher Candidate"


def test_resume_document_validator_gate():
    """
    Verifies pre-parsing document validation:
    Genuine resumes pass; Invoices and Research papers are rejected.
    """
    genuine_resume_text = """
    John Doe
    Email: john.doe@example.com | Phone: +1-555-0192 | LinkedIn: linkedin.com/in/johndoe
    
    Professional Experience:
    Senior Software Engineer — TechCorp (Jan 2021 – Present)
    - Built FastAPI microservices serving 10M daily requests.
    - Managed PostgreSQL and Redis clusters.
    
    Education:
    Bachelor of Science in Computer Science, State University (2016 – 2020)
    
    Skills:
    Python, FastAPI, Docker, Kubernetes, PostgreSQL, AWS
    """

    invoice_text = """
    INVOICE #98214
    Bill To: Acme Corporation
    Date: 2026-07-01
    Total Amount Due: $4,500.00
    Subtotal: $4,000.00
    Tax Rate: 12.5%
    Terms and conditions apply. Payment due upon receipt.
    """

    is_valid_resume, score_resume, msg_resume = validate_is_resume(genuine_resume_text)
    assert is_valid_resume is True
    assert score_resume >= 40.0
    assert "Valid" in msg_resume

    is_valid_invoice, score_invoice, msg_invoice = validate_is_resume(invoice_text)
    assert is_valid_invoice is False
    assert score_invoice < 40.0
    assert "does not appear to be a valid résumé" in msg_invoice


def test_timeline_date_range_preservation():
    """
    Verifies that career timeline generation preserves complete date ranges.
    """
    parsed_resume = {
        "work_history": [
            {
                "company": "Enterprise Corp",
                "role": "Lead Data Scientist",
                "dates": "Jan 2019 – Mar 2021",
                "description": "Led recommendation systems engineering team."
            },
            {
                "company": "Innovate AI",
                "role": "Staff ML Architect",
                "dates": "Apr 2021 – Present",
                "description": "Architected LLM serving platform."
            }
        ]
    }

    timeline = _generate_career_timeline(parsed_resume)
    assert len(timeline) == 2
    assert timeline[0]["period"] == "Jan 2019 – Mar 2021"
    assert timeline[0]["year"] == "Jan 2019 – Mar 2021"
    assert timeline[1]["period"] == "Apr 2021 – Present"
    assert timeline[1]["year"] == "Apr 2021 – Present"
