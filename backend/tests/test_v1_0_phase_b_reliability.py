"""
TalentScout Enterprise Version 1.0 — Phase B Reliability Test Suite.
Validates code hygiene, type safety, text processing helpers, and zero regression across core evaluations.
"""
import pytest
from app.core.text_utils import (
    clean_text_string,
    normalize_candidate_name,
    extract_lowercase_keywords
)

def test_phase_b_clean_text_string():
    assert clean_text_string(None) == ""
    assert clean_text_string("  hello world  ") == "hello world"
    assert clean_text_string("test\0null") == "testnull"

def test_phase_b_normalize_candidate_name():
    assert normalize_candidate_name(None) == "Unknown Candidate"
    assert normalize_candidate_name("unknown") == "Unknown Candidate"
    assert normalize_candidate_name("john doe.") == "John Doe"

def test_phase_b_extract_lowercase_keywords():
    tokens = extract_lowercase_keywords("React, Node.js, and MongoDB 123")
    assert "react" in tokens
    assert "node.js" in tokens
    assert "mongodb" in tokens
