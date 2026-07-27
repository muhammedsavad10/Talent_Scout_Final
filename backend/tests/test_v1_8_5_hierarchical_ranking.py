"""
TalentScout Enterprise v1.8.5 — Hierarchical Lexicographic Ranking Test Suite.
Validates:
1. User Request Example: Candidate A (Stage1=83, Stage2=62) outranks Candidate B (Stage1=77, Stage2=70)
2. Stage 2 Tie-Breaking within Margin: Candidate D (Stage1=82.0, Stage2=88) outranks Candidate C (Stage1=83.5, Stage2=70)
3. Configurable Technical Dominance Margin
4. Recruiter Narrative Rationale
"""
import pytest
from app.agents.comparator import compare_candidates

def test_v1_8_5_technical_dominance_overrides_stage2():
    # User Request Example: Candidate A (Stage1=83, Stage2=62) vs Candidate B (Stage1=77, Stage2=70)
    eval_a = {
        "evaluation_id": "cand_a",
        "personal_info": {"name": "Candidate A"},
        "overall_score": 83.0,
        "hiring_priority": {"hiring_priority_score": 62}
    }
    eval_b = {
        "evaluation_id": "cand_b",
        "personal_info": {"name": "Candidate B"},
        "overall_score": 77.0,
        "hiring_priority": {"hiring_priority_score": 70}
    }

    ranked = compare_candidates([eval_a, eval_b], technical_margin=3.0)

    # Candidate A MUST rank #1 because Stage1 diff = 6.0 > 3.0 (Technical Dominance)
    assert ranked[0]["candidate_name"] == "Candidate A"
    assert ranked[0]["rank"] == 1
    assert ranked[1]["candidate_name"] == "Candidate B"
    assert ranked[1]["rank"] == 2
    assert "Technical Dominance" in ranked[1]["ranking_explanation"]

def test_v1_8_5_stage2_tiebreaker_within_margin():
    # Candidate C (Stage1=83.5, Stage2=70) vs Candidate D (Stage1=82.0, Stage2=88)
    eval_c = {
        "evaluation_id": "cand_c",
        "personal_info": {"name": "Candidate C"},
        "overall_score": 83.5,
        "hiring_priority": {"hiring_priority_score": 70}
    }
    eval_d = {
        "evaluation_id": "cand_d",
        "personal_info": {"name": "Candidate D"},
        "overall_score": 82.0,
        "hiring_priority": {"hiring_priority_score": 88}
    }

    ranked = compare_candidates([eval_c, eval_d], technical_margin=3.0)

    # Candidate D MUST rank #1 because Stage1 diff = 1.5 <= 3.0, Stage 2 tiebreaker takes effect!
    assert ranked[0]["candidate_name"] == "Candidate D"
    assert ranked[0]["rank"] == 1
    assert ranked[1]["candidate_name"] == "Candidate C"
    assert ranked[1]["rank"] == 2
    assert "Stage 2 Hiring Priority" in ranked[1]["ranking_explanation"]
