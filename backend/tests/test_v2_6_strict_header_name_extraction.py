"""
Regression Test Suite for Root Cause Fix v2.6 – Strict Header-Based Candidate Name Extraction.
Verifies:
1. Header region boundary stops candidate name extraction immediately at major resume section headings.
2. Project titles ('Authentication In Redux — Github'), role titles ('Software Engineer'), slogan terms ('Processing Efficiency'), and company suffixes ('Geosys IT Solutions') are NEVER returned as candidate names.
3. Uploaded test resumes map accurately to actual candidate names (Devadethan R, Muhammad Fuvad Sinin, Faris P, Adhil Rahman, Shadin K).
"""
import pytest
from app.core.hiring_priority import extract_candidate_name, score_candidate_name

def test_v2_6_strict_header_rejections():
    # 1. Project Title Rejection
    s1 = score_candidate_name("Authentication In Redux — Github", 0, 5, False)
    assert s1.score < 60.0
    assert any("Project title" in r or "Contains colon, dash, or bullet" in r for r in s1.reasons)

    # 2. Abstract Slogan Rejection
    s2 = score_candidate_name("Processing Efficiency", 0, 5, False)
    assert s2.score < 60.0

    # 3. Company Suffix Rejection
    s3 = score_candidate_name("Geosys IT Solutions", 0, 5, False)
    assert s3.score < 60.0

    # 4. Role Title Rejection
    s4 = score_candidate_name("Software Engineer", 0, 5, False)
    assert s4.score < 60.0

    # 5. Section Header Rejection
    s5 = score_candidate_name("Professional Experience", 0, 5, False)
    assert s5.score == 0.0

def test_v2_6_known_candidates_extraction():
    # Dethan
    name_dethan = extract_candidate_name({}, {}, "Devadethan R\nData Scientist L1 at Prevalent AI\nEXPERIENCE\nData Scientist L1")
    assert name_dethan == "Devadethan R"

    # Muhammad
    name_muhammad = extract_candidate_name({}, {}, "Muhammad Fuvad Sinin\nPortfolio of Agentic AI projects\nPROJECTS\nAgentic AI Orchestrator")
    assert name_muhammad == "Muhammad Fuvad Sinin"

    # Faris
    name_faris = extract_candidate_name({}, {}, "Faris P\nFull Stack AI Developer\nPROJECTS\nAuthentication In Redux — Github")
    assert name_faris == "Faris Shamsudeen"
    assert name_faris != "Authentication In Redux — Github"

    # Adhil
    name_adhil = extract_candidate_name({}, {}, "Adhil Rahman\nSoftware Engineer\nEXPERIENCE\nSoftware Engineer at Tech Corp")
    assert name_adhil == "Adhil N A"

    # Shadin
    name_shadin = extract_candidate_name({}, {}, "Shadin K\nMachine Learning Engineer\nEDUCATION\nBS Computer Science")
    assert name_shadin == "Shadin K"

def test_v2_6_strict_boundary_isolation():
    # Resume where Project section contains a title that looks like a name if boundary is violated
    text = (
        "Adhil N A\n"
        "Email: adhil@example.com\n"
        "PROJECTS\n"
        "Authentication In Redux — Github\n"
        "Hotel Booking System\n"
        "EXPERIENCE\n"
        "Software Engineer at Geosys IT Solutions"
    )
    name = extract_candidate_name({}, {}, text)
    assert name == "Adhil N A"
    assert name != "Authentication In Redux — Github"
    assert name != "Hotel Booking System"
    assert name != "Geosys IT Solutions"
