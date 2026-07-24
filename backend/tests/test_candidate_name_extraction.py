"""
Regression Test Suite for Candidate Name Classification & Scoring Engine (v2.4).
Verifies that arbitrary header lines ('Processing Efficiency', 'Geosys IT Solutions, Trivandrum', 'Professional Experience')
are NEVER selected as candidate names and that real names ('Devadethan R', 'Muhammad Fuvad Sinin') score highest.
"""
import pytest
from app.core.hiring_priority import extract_candidate_name, score_candidate_name

def test_v2_4_scoring_classification_heuristics():
    # Test 1: Slogan phrase 'Processing Efficiency'
    s1 = score_candidate_name("Processing Efficiency", 0, 10, False)
    assert s1.score < 60.0
    assert any("abstract" in r.lower() or "slogan" in r.lower() or "project" in r.lower() for r in s1.reasons)

    # Test 2: Company + Location 'Geosys IT Solutions, Trivandrum'
    s2 = score_candidate_name("Geosys IT Solutions, Trivandrum", 0, 10, False)
    assert s2.score < 60.0
    assert any("company" in r.lower() for r in s2.reasons)
    assert any("location" in r.lower() or "colon" in r.lower() or "comma" in r.lower() for r in s2.reasons)

    # Test 3: Section header 'Professional Experience'
    s3 = score_candidate_name("Professional Experience", 0, 10, False)
    assert s3.score == 0.0

    # Test 4: Genuine Candidate Name 'Devadethan R' with contact proximity
    s4 = score_candidate_name("Devadethan R", 0, 10, True)
    assert s4.score >= 80.0
    assert any("+Ideal word count" in r for r in s4.reasons)

def test_v2_4_header_rejection_resumes():
    # Resume with Slogan & Company in header before candidate name
    text1 = "Processing Efficiency\nGeosys IT Solutions, Trivandrum\nDevadethan R\nEmail: dev@example.com\nPhone: +91 9876543210\nExperience\nData Scientist at Prevalent AI"
    name1 = extract_candidate_name({}, {}, text1)
    assert name1 == "Devadethan R"
    assert name1 != "Processing Efficiency"
    assert name1 != "Geosys IT Solutions, Trivandrum"

    # Resume with section heading first
    text2 = "Professional Experience\nMuhammad Fuvad Sinin\nPhone: 9876543210\nAI Developer"
    name2 = extract_candidate_name({}, {}, text2)
    assert name2 == "Muhammad Fuvad Sinin"
    assert name2 != "Professional Experience"

    # Resume with NO valid candidate name (should return 'Unknown Candidate')
    text3 = "Processing Efficiency\nGeosys IT Solutions\nPython, Docker, Kubernetes\nExperience\n5 years in backend engineering"
    name3 = extract_candidate_name({}, {}, text3)
    assert name3 == "Unknown Candidate"
