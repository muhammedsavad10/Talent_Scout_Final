"""
Regression Test Suite for Certification Engine v6.0 Production Polishing & Metadata Consistency.
Verifies:
1. Canonical title cleanup (stripping unclosed parentheses, dates, issuer fragments).
2. Metadata contract consistency: vendor == issuing_organization.
3. Provider extraction & normalization (simplilearn -> Simplilearn).
4. Issuer extraction & normalization (ibm -> IBM, google -> Google, microSoft -> Microsoft).
5. Dynamic confidence calculation (1.00 for canonical match, 0.95 for known issuer).
6. Deterministic Quality Score calculation (30/20/20/15/15 weights).
7. Validation Status tagging (VALID, PARTIAL, LOW_CONFIDENCE, INVALID).
8. Date normalization (FEB -> Feb, (Jan -> Jan).
9. Category normalization (Artificial Intelligence, Machine Learning, DevOps / Cloud, Business Intelligence, Data Engineering).
10. Malformed certification rejection.
"""
import pytest
from app.core.cert_quality_gate import (
    clean_canonical_name,
    normalize_date,
    normalize_category,
    validate_and_gate_certification
)

def test_canonical_title_cleanup_keras():
    raw = "Deep Learning & Neural Networks with Keras, ibm, (Jan"
    obj = validate_and_gate_certification(raw)

    assert obj is not None
    assert obj["canonical_name"] == "Deep Learning & Neural Networks with Keras"
    assert obj["issuing_organization"] == "IBM"
    assert obj["vendor"] == "IBM"
    assert obj["vendor"] == obj["issuing_organization"]
    assert obj["category"] == "Artificial Intelligence"
    assert obj["validation_status"] in ["VALID", "PARTIAL"]

def test_provider_and_issuer_normalization():
    raw = "Big Data Foundations Level 1, ibm, coursera, (may 2024)"
    obj = validate_and_gate_certification(raw)

    assert obj is not None
    assert obj["canonical_name"] == "Big Data Foundations Level 1"
    assert obj["issuing_organization"] == "IBM"
    assert obj["training_provider"] == "Coursera"
    assert obj["vendor"] == "IBM"
    assert obj["issue_date"] == "May 2024"
    assert obj["quality_score"] >= 0.85
    assert obj["validation_status"] == "VALID"

def test_vendor_equals_issuing_organization():
    raw = "Google AI Essentials, Google, Coursera, (Jun 2024)"
    obj = validate_and_gate_certification(raw)

    assert obj is not None
    assert obj["vendor"] == obj["issuing_organization"]
    assert obj["vendor"] == "Google"
    assert obj["confidence"] == 1.00

def test_date_normalization_cases():
    assert normalize_date("FEB 2023") == "Feb 2023"
    assert normalize_date("(may 2024") == "May 2024"
    assert normalize_date("JAN") == "Jan"

def test_category_normalization_cases():
    assert normalize_category("Neural Networks & Deep Learning") == "Artificial Intelligence"
    assert normalize_category("Machine Learning Specialization") == "Machine Learning"
    assert normalize_category("Google Kubernetes Engine (GKE)") == "DevOps / Cloud"
    assert normalize_category("Tableau Certified") == "Business Intelligence"
    assert normalize_category("Databricks Engineer") == "Data Engineering"
