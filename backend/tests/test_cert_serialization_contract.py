"""
Regression Test Suite for Phase 1-9 Certification Normalization, Serialization & Duplicate Detection Engine.
Verifies:
1. Merge raw + canonical into ONE unique object per certification.
2. Alias deduplication (Tableau Certified / Tableau Data Analyst -> 1 object).
3. certification_count == len(serialized_certifications).
4. Complete 10-key Serialization Contract + backward-compatibility keys (original_name, canonical_name, issuing_organization, training_provider, issue_date, category, confidence, evidence, line_number, section_heading, name, title, vendor).
5. Issuer preservation without 'Industry Accredited' fallback when issuer is known.
6. Verification against Dethan candidate profile.
"""
import pytest
from app.core.hiring_priority import canonicalize_certification, extract_structured_certifications, compute_hiring_priority_score

def test_phase1_and_phase5_contract_fields():
    raw_str = "Google AI Essentials, Google, Coursera, (Jun 2024)"
    cert_obj = canonicalize_certification(raw_str, line_index=1)

    required_keys = [
        "original_name", "canonical_name", "issuing_organization",
        "training_provider", "issue_date", "category", "confidence",
        "evidence", "line_number", "section_heading", "name", "title", "vendor"
    ]

    for k in required_keys:
        assert k in cert_obj, f"Missing key '{k}' in serialized certification object"

    assert cert_obj["original_name"] == raw_str
    assert cert_obj["canonical_name"] == "Google AI Essentials"
    assert cert_obj["issuing_organization"] == "Google"
    assert cert_obj["training_provider"] == "Coursera"
    assert cert_obj["issue_date"] == "Jun 2024"
    assert cert_obj["category"] == "Artificial Intelligence"
    assert cert_obj["name"] == "Google AI Essentials"
    assert cert_obj["title"] == "Google AI Essentials"
    assert cert_obj["vendor"] == "Google"

def test_phase2_3_8_alias_and_duplicate_deduplication():
    eval_obj = {}
    parsed_res = {
        "certifications": [
            "Tableau Certified",
            "Tableau Data Analyst",
            "Google AI Essentials",
            "IBM AI Engineering Professional Certificate",
            "Google Kubernetes Engine (GKE)",
            "Certified Data Scientist"
        ]
    }
    raw_text = """CERTIFICATIONS
- Tableau Certified
- Tableau Data Analyst
- Google AI Essentials
- IBM AI Engineering Professional Certificate
- Google Kubernetes Engine (GKE)
- Certified Data Scientist
"""
    certs = extract_structured_certifications(eval_obj, parsed_res, raw_text)

    # Tableau Certified and Tableau Data Analyst must be merged into ONE object
    tableau_objs = [c for c in certs if "tableau" in c["canonical_name"].lower()]
    assert len(tableau_objs) == 1, "Duplicate Tableau alias objects found!"
    assert tableau_objs[0]["issuing_organization"] == "Tableau / Salesforce"

    # Total unique certifications must be 5
    assert len(certs) == 5

def test_phase4_certification_count_and_issuer_preservation():
    eval_obj = {
        "raw_resume_text": """Devadethan R
CERTIFICATIONS
- Google AI Essentials
- IBM AI Engineering Professional Certificate
- Google Kubernetes Engine (GKE)
- Tableau Certified
- Certified Data Scientist
""",
        "parsed_resume": {
            "personal_info": {"name": "Devadethan R"},
            "certifications": [
                "Google AI Essentials",
                "IBM AI Engineering Professional Certificate",
                "Google Kubernetes Engine (GKE)",
                "Tableau Certified",
                "Certified Data Scientist"
            ]
        }
    }
    res = compute_hiring_priority_score(eval_obj)

    certs = res["certifications"]
    profile = res["professional_profile"]

    # certification_count == len(serialized_certifications)
    assert profile["certification_count"] == len(certs)
    assert len(certs) == 5

    # Check issuer preservation (No 'Industry Accredited' fallback for known issuers)
    issuers = [c["issuing_organization"] for c in certs]
    assert "Google" in issuers
    assert "IBM" in issuers
    assert "Tableau / Salesforce" in issuers
    assert "Global Data Science Institute" in issuers
    assert not any(i == "Industry Accredited" for i in issuers)
