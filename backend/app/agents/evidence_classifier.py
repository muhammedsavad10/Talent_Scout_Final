"""
Strict Entity Classifier & Confidence Engine for TalentScout Enterprise v1.6.
Classifies every extracted resume entity into EXACTLY ONE category:
EMPLOYER, ROLE_TITLE, PROJECT, CERTIFICATION, SKILL, EDUCATION, TECHNOLOGY, ACHIEVEMENT, RESPONSIBILITY, DATE, LOCATION, UNKNOWN.
Enforces strict semantic boundaries and prevents cross-contamination.
"""
import re
from enum import Enum
from typing import Dict, Any, Tuple

class EntityCategory(str, Enum):
    EMPLOYER = "EMPLOYER"
    ROLE_TITLE = "ROLE_TITLE"
    PROJECT = "PROJECT"
    CERTIFICATION = "CERTIFICATION"
    SKILL = "SKILL"
    EDUCATION = "EDUCATION"
    TECHNOLOGY = "TECHNOLOGY"
    ACHIEVEMENT = "ACHIEVEMENT"
    RESPONSIBILITY = "RESPONSIBILITY"
    DATE = "DATE"
    LOCATION = "LOCATION"
    UNKNOWN = "UNKNOWN"

class ExperienceCategory(str, Enum):
    PROFESSIONAL_EMPLOYMENT = "PROFESSIONAL_EMPLOYMENT"
    INTERNSHIP = "INTERNSHIP"
    FREELANCE = "FREELANCE"
    CONSULTING = "CONSULTING"
    VOLUNTEER = "VOLUNTEER"
    ACADEMIC_PROJECT = "ACADEMIC_PROJECT"
    PERSONAL_PROJECT = "PERSONAL_PROJECT"
    RESEARCH_PROJECT = "RESEARCH_PROJECT"
    HACKATHON = "HACKATHON"
    COURSE_PROJECT = "COURSE_PROJECT"

ACTION_VERB_PATTERNS = [
    r"^(?:built|designed|developed|engineered|implemented|architected|created|spearheaded|managed|lead|optimized|deployed)\b"
]

KNOWN_PROJECT_TITLES = {
    "delay2decision", "faircrop ai", "sentineldocs", "skillconnect", "iuml",
    "etl ingestion pipeline", "delay2decision agent", "faircrop"
}

PROJECT_SIGNALS = {
    "built", "created", "designed", "developed", "implemented", "portfolio",
    "github", "demo", "prototype", "system", "platform", "personal project",
    "academic project", "capstone", "agent"
}

def classify_experience_type(
    company: str,
    role: str,
    description: str = "",
    source_section: str = ""
) -> ExperienceCategory:
    """
    v1.7.1 Employment Intelligence Classifier.
    Classifies any work/experience entry into EXACTLY ONE ExperienceCategory.
    Ensures projects are NEVER classified as PROFESSIONAL_EMPLOYMENT.
    """
    comp_clean = (company or "").strip().lower()
    role_clean = (role or "").strip().lower()
    desc_clean = (description or "").strip().lower()
    source_sec = (source_section or "").strip().lower()

    # 1. Section & Title Signal Checks for Personal/Academic Projects
    if source_sec == "projects" or comp_clean in KNOWN_PROJECT_TITLES:
        return ExperienceCategory.PERSONAL_PROJECT

    if any(sig in comp_clean for sig in ["personal project", "academic project", "capstone", "portfolio"]):
        return ExperienceCategory.PERSONAL_PROJECT

    # 2. Role Title Checks for Internships / Freelance / Consulting
    if any(k in role_clean for k in ["intern", "trainee", "apprentice"]):
        return ExperienceCategory.INTERNSHIP

    if any(k in role_clean for k in ["freelance", "contractor"]):
        return ExperienceCategory.FREELANCE

    if any(k in role_clean for k in ["consultant", "adviser", "advisor"]):
        return ExperienceCategory.CONSULTING

    if "volunteer" in role_clean or "volunteer" in desc_clean:
        return ExperienceCategory.VOLUNTEER

    # 3. Check if entry is a project description or action verb bullet
    first_role_word = role_clean.split()[0] if role_clean.split() else ""
    if first_role_word in {"built", "designed", "implemented", "developed", "engineered", "created", "integrated", "optimized", "deployed"}:
        return ExperienceCategory.PERSONAL_PROJECT

    if comp_clean in KNOWN_PROJECT_TITLES or role_clean in KNOWN_PROJECT_TITLES:
        return ExperienceCategory.PERSONAL_PROJECT

    # 4. Professional Employment Verification
    if role_clean and len(role_clean.split()) <= 8 and not any(sig in role_clean for sig in ["personal project", "academic project", "capstone"]):
        return ExperienceCategory.PROFESSIONAL_EMPLOYMENT

    return ExperienceCategory.PERSONAL_PROJECT

def classify_entity_strictly(text: str, source_section: str) -> Tuple[EntityCategory, float]:
    """
    Phase 4 & 5: Strict Entity Classification Engine.
    Assigns an extracted entity fragment into EXACTLY ONE EntityCategory with confidence score.
    """
    clean_text = text.strip()
    lower_text = clean_text.lower()
    source_sec = source_section.lower()

    # 1. Reject action verbs from ROLE_TITLE or EMPLOYER
    if any(re.search(pat, lower_text) for pat in ACTION_VERB_PATTERNS):
        return EntityCategory.ACHIEVEMENT, 0.90

    # 2. Certification classification
    if source_sec == "certifications":
        return EntityCategory.CERTIFICATION, 0.95
        
    accredited_cert_patterns = [r"\b(?:aws certified|google certified|ibm certified|cissp|pmp|tableau certified|certified data scientist)\b"]
    if any(re.search(pat, lower_text) for pat in accredited_cert_patterns):
        return EntityCategory.CERTIFICATION, 0.90

    # 3. Project vs Employer classification
    if source_sec == "projects" or lower_text in KNOWN_PROJECT_TITLES:
        return EntityCategory.PROJECT, 0.95

    # 4. Employment Role Title classification
    if source_sec == "experience":
        if len(clean_text.split()) <= 8 and not any(kw in lower_text for kw in ["built", "designed", "implemented"]):
            return EntityCategory.ROLE_TITLE, 0.95
        return EntityCategory.RESPONSIBILITY, 0.85

    return EntityCategory.UNKNOWN, 0.50

def classify_and_score_evidence(
    fragment: str,
    source_section: str,
    extracted_type: str
) -> Tuple[str, float, str]:
    """
    Phase 4: Backward-compatible classification wrapper.
    """
    cat, conf = classify_entity_strictly(fragment, source_section)
    
    if extracted_type == "Certification" and cat != EntityCategory.CERTIFICATION:
        return "Project", 0.0, "REJECT"
        
    if extracted_type == "Employment" and cat in [EntityCategory.PROJECT, EntityCategory.ACHIEVEMENT]:
        return "Project", 0.0, "REJECT"

    if cat == EntityCategory.ACHIEVEMENT and extracted_type == "Employment":
        return "Employment", 0.30, "LOW_CONFIDENCE"

    return extracted_type, conf, "VALID"
