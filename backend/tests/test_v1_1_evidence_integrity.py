"""
TalentScout Enterprise v1.1 — Evidence Extraction & Integrity Test Suite.
Verifies section-aware extraction, evidence classification, certification isolation,
project/employer separation, concise job titles, and confidence scoring.
"""
import pytest
import json
from app.core.section_detector import detect_resume_sections
from app.agents.evidence_classifier import classify_and_score_evidence
from app.services.ai_gateway import _extract_deterministic_fallback_resume

def test_project_bullets_never_classified_as_certifications():
    text_bullet = "Deployed microservices on Google Cloud Run with Kubernetes"
    cat, conf, status = classify_and_score_evidence(text_bullet, "projects", "Certification")
    assert status == "REJECT"

def test_accredited_cert_in_certifications_section_has_high_confidence():
    text_cert = "AWS Certified Solutions Architect"
    cat, conf, status = classify_and_score_evidence(text_cert, "certifications", "Certification")
    assert status == "VALID"
    assert conf == 0.95

def test_projects_never_classified_as_employers():
    resume_with_projects = """
    Alice Smith
    
    EXPERIENCE
    Senior AI Engineer at TechCorp (2022 - Present)
    
    PROJECTS
    Delay2Decision
    Built real-time decision support system.
    
    FairCrop AI
    Built agricultural yield prediction models.
    """
    sections = detect_resume_sections(resume_with_projects)
    assert "TechCorp" in sections["experience"]
    assert "Delay2Decision" in sections["projects"]
    
    parsed_json = json.loads(_extract_deterministic_fallback_resume(resume_with_projects))
    companies = [w["company"] for w in parsed_json["work_history"]]
    assert "TechCorp" in companies
    assert "Delay2Decision" not in companies
    assert "FairCrop AI" not in companies

def test_responsibility_sentences_rejected_for_role_titles():
    sentence = "Designed and developed a dynamic decision-support system using Python"
    cat, conf, status = classify_and_score_evidence(sentence, "experience", "Employment")
    assert conf <= 0.30
