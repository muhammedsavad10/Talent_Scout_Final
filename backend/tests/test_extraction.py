import pytest
from app.agents.deterministic_extractor import extract_contact_info, extract_known_skills

def test_deterministic_contact_extraction():
    text = "Contact me at candidate@example.com or call +1-800-555-0199. Check my github: https://github.com/candidate"
    
    contacts = extract_contact_info(text)
    assert contacts["email"] == "candidate@example.com"
    assert contacts["phone"] == "+1-800-555-0199"
    assert "https://github.com/candidate" in contacts["links"]

def test_deterministic_skill_extraction():
    ontology = ["Python", "Machine Learning", "FastAPI"]
    text = "I am a Python developer with experience in machine learning and FastAPI."
    
    extracted = extract_known_skills(text, ontology)
    assert "Python" in extracted
    assert "Machine Learning" in extracted
    assert "FastAPI" in extracted

def test_no_partial_matches():
    ontology = ["Java", "C"]
    # 'Javascript' should not match 'Java' and 'Machine' should not match 'C'
    text = "I write Javascript for the Mac."
    extracted = extract_known_skills(text, ontology)
    
    assert "Java" not in extracted
    assert "C" not in extracted
