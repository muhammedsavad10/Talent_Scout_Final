"""
Regression Test Suite for Certification Engine v5.1 Validation & Quality Gate.
Verifies:
1. Rejection of summary sentences ('and ML engineering, optimizing workflows...').
2. Rejection of emails, phone numbers, LinkedIn, GitHub links.
3. Provider extraction (Simplilearn, Coursera, NPTEL, Udemy, etc.).
4. Canonical title cleaning (separating issuer/provider/date).
5. Issuer preservation without 'Industry Accredited' fallback when issuer exists.
6. Partial date extraction (Dec 2023, May 2024, 2023).
7. Quality score calculation & threshold gating.
"""
import pytest
from app.core.cert_quality_gate import is_valid_certification_text, clean_canonical_name, validate_and_gate_certification

def test_summary_sentence_rejection():
    text1 = "and ML engineering, optimizing workflows..."
    valid1, reason1 = is_valid_certification_text(text1)
    assert not valid1
    assert "optimizing" in reason1

    obj1 = validate_and_gate_certification(text1)
    assert obj1 is None

def test_contact_and_social_rejection():
    text_email = "Certification - contact user@example.com for details"
    text_linkedin = "Certified Developer linkedin.com/in/test"
    text_phone = "Certified Engineer Call +91 9876543210"

    assert not is_valid_certification_text(text_email)[0]
    assert not is_valid_certification_text(text_linkedin)[0]
    assert not is_valid_certification_text(text_phone)[0]

def test_provider_and_date_extraction():
    raw = "Certified Data Scientist, IBM, Simplilearn, (Dec 2023)"
    obj = validate_and_gate_certification(raw)

    assert obj is not None
    assert obj["canonical_name"] == "Certified Data Scientist"
    assert obj["issuing_organization"] == "IBM"
    assert obj["training_provider"] == "Simplilearn"
    assert obj["issue_date"] == "Dec 2023"
    assert obj["quality_score"] >= 0.80

def test_canonical_title_cleaning():
    raw = "Google Cloud Computing Foundations: Infrastructure in Google Cloud, Google, Coursera, (May 2024)"
    obj = validate_and_gate_certification(raw)

    assert obj is not None
    assert obj["canonical_name"] == "Google Cloud Computing Foundations: Infrastructure in Google Cloud"
    assert obj["issuing_organization"] == "Google"
    assert obj["training_provider"] == "Coursera"
    assert obj["issue_date"] == "May 2024"
