"""
Role & Domain Relevance Engine for TalentScout Enterprise v1.5.
Evaluates semantic role titles and technical skill domains to scale candidate priority.
Ensures technical match and role relevance remain the dominant ranking signals.
"""
import re
from typing import List, Dict, Any, Tuple

ROLE_DOMAINS = {
    "data_science_ai": [
        "data scientist", "machine learning engineer", "ml engineer", "ai engineer",
        "ai developer", "research engineer", "nlp engineer", "computer vision engineer",
        "deep learning engineer", "applied scientist", "data science intern"
    ],
    "backend_python": [
        "python developer", "python engineer", "backend engineer", "backend developer",
        "full stack developer", "full stack engineer", "software engineer", "systems engineer"
    ],
    "frontend_ui": [
        "frontend developer", "frontend engineer", "ui engineer", "react developer",
        "web developer", "ui/ux designer", "qa engineer", "testing engineer"
    ]
}

def calculate_role_and_domain_relevance(
    work_history: List[Dict[str, Any]],
    candidate_skills: List[str],
    jd_title: str = "Data Scientist",
    required_skills: List[str] = None
) -> float:
    """
    Phase 8 & 9: Role Relevance & Domain Matching Engine.
    Returns a score from 0.0 to 100.0 indicating how closely candidate role history and domain skills match the target JD.
    """
    if required_skills is None:
        required_skills = []

    jd_lower = (jd_title or "").lower()
    
    # 1. Classify target JD domain
    target_domain = "data_science_ai"
    if any(kw in jd_lower for kw in ["full stack", "frontend", "web", "react"]):
        target_domain = "frontend_ui"
    elif any(kw in jd_lower for kw in ["backend", "software engineer", "devops", "cloud"]):
        target_domain = "backend_python"

    # 2. Score role history relevance against target domain
    max_role_score = 40.0  # Base line score if no work history
    
    for item in work_history:
        role_str = str(item.get("role") or item.get("title") or "").lower()
        if not role_str:
            continue
            
        if any(role_kw in role_str for role_kw in ROLE_DOMAINS["data_science_ai"]):
            if target_domain == "data_science_ai":
                max_role_score = max(max_role_score, 100.0)
            else:
                max_role_score = max(max_role_score, 75.0)
        elif any(role_kw in role_str for role_kw in ROLE_DOMAINS["backend_python"]):
            if target_domain == "data_science_ai":
                max_role_score = max(max_role_score, 60.0)
            else:
                max_role_score = max(max_role_score, 90.0)
        elif any(role_kw in role_str for role_kw in ROLE_DOMAINS["frontend_ui"]):
            if target_domain == "data_science_ai":
                max_role_score = max(max_role_score, 30.0)
            else:
                max_role_score = max(max_role_score, 50.0)

    # 3. Score technical skill domain relevance
    skill_score = 50.0
    if candidate_skills:
        ai_skills = {"python", "pytorch", "tensorflow", "scikit-learn", "xgboost", "nlp", "rag", "qdrant", "langchain", "langgraph", "fastapi", "spark"}
        matched_ai = sum(1 for s in candidate_skills if s.lower() in ai_skills)
        if target_domain == "data_science_ai":
            skill_score = min(100.0, 40.0 + (matched_ai * 12.0))
        else:
            skill_score = min(100.0, 50.0 + (len(candidate_skills) * 5.0))

    final_relevance = (max_role_score * 0.60) + (skill_score * 0.40)
    return round(min(100.0, max(10.0, final_relevance)), 1)
