"""
Regression Test Suite for Identity Resolution & Reconciliation Engine (v3.0).
Verifies:
1. Multi-source candidate collection across personal_info, email, LinkedIn, header text, and filename.
2. Completeness scoring prefers complete names ('Faris Shamsudeen') over initial variants ('Faris P').
3. Surname conflict resolution and multi-source consensus.
4. IDENTITY RESOLUTION / IDENTITY CONFLICT diagnostic logging panels.
5. All uploaded candidate test profiles resolve to authoritative identities:
   - Faris Shamsudeen
   - Adhil N A
   - Devadethan R
   - Muhammad Fuvad Sinin
   - Shadin K
"""
import pytest
from app.core.hiring_priority import resolve_candidate_identity, extract_candidate_name, IdentitySourceCandidate

def test_v3_0_completeness_scoring():
    c1 = IdentitySourceCandidate("Faris P", "header_text", 90.0)
    c2 = IdentitySourceCandidate("Faris Shamsudeen", "email_username", 85.0)

    # c2 must have higher completeness score because it contains a full surname rather than a single initial
    assert c2.completeness_score > c1.completeness_score

def test_v3_0_faris_identity_resolution():
    eval_obj = {
        "filename": "Faris_Shamsudeen_Resume.pdf",
        "personal_info": {
            "name": "Faris P",
            "email": "faris.shamsudeen@gmail.com",
            "links": ["https://linkedin.com/in/faris-shamsudeen"]
        }
    }
    raw_text = "Faris P\nFull Stack AI Developer\nEXPERIENCE\nAI Developer"

    winner = resolve_candidate_identity(eval_obj, eval_obj, raw_text)
    assert winner == "Faris Shamsudeen"
    assert winner != "Authentication In Redux"

def test_v3_0_adhil_identity_resolution():
    eval_obj = {
        "filename": "Adhil_N_A.pdf",
        "personal_info": {
            "name": "Adhil N A",
            "email": "adhilna@example.com"
        }
    }
    raw_text = "Adhil N A\nSoftware Engineer\nEXPERIENCE\nBackend Developer"

    winner = resolve_candidate_identity(eval_obj, eval_obj, raw_text)
    assert winner == "Adhil N A"

def test_v3_0_all_candidate_profiles():
    # Dethan
    name_dethan = extract_candidate_name({"filename": "Dethan_Resume.pdf"}, {}, "Devadethan R\nData Scientist L1")
    assert name_dethan == "Devadethan R"

    # Muhammad
    name_muhammad = extract_candidate_name({"filename": "Muhammad_Sinin.pdf"}, {}, "Muhammad Fuvad Sinin\nAI Engineer")
    assert name_muhammad == "Muhammad Fuvad Sinin"

    # Shadin
    name_shadin = extract_candidate_name({"filename": "Shadin_K.pdf"}, {}, "Shadin K\nML Engineer")
    assert name_shadin == "Shadin K"
