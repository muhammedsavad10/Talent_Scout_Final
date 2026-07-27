"""
Role & Domain Relevance Engine for TalentScout Enterprise (v1.8.4 Domain-Adaptive Architecture).
Evaluates candidate role history and domain competencies dynamically against the JDCompetencyModel.
Ensures zero hardcoded role lists or case-by-case exceptions.
"""
from typing import List, Dict, Any
from app.core.jd_competency_model import build_jd_competency_model, JDCompetencyModel
from app.core.evidence_relevance_engine import evaluate_work_history_evidence, evaluate_skill_evidence

def calculate_role_and_domain_relevance(
    work_history: List[Dict[str, Any]],
    candidate_skills: List[str],
    jd_title: str = "Target Role",
    required_skills: List[str] = None
) -> float:
    """
    v1.8.4 Domain-Adaptive Role Relevance Calculation.
    Returns a score from 0.0 to 100.0 based on dynamic JD Competency Model alignment and Dual-Dimension Evidence Scoring.
    """
    if required_skills is None:
        required_skills = []

    # Build dynamic competency model from JD title and required skills
    comp_model = build_jd_competency_model(jd_title, required_skills)

    # 1. Score Employment History Relevance (Confidence x Relevance)
    role_relevance_scores = []
    if work_history:
        for item in work_history:
            if isinstance(item, dict):
                evaluated = evaluate_work_history_evidence(item, comp_model)
                role_relevance_scores.append(evaluated.relevance * 100.0)

    max_role_score = max(role_relevance_scores) if role_relevance_scores else 40.0

    # 2. Score Skill Competency Relevance (Top matching competencies)
    skill_relevance_scores = []
    if candidate_skills:
        for sk in candidate_skills:
            if isinstance(sk, str):
                evaluated = evaluate_skill_evidence(
                    sk, comp_model, is_explicit_match=(sk.lower() in comp_model.required_skills)
                )
                skill_relevance_scores.append(evaluated.relevance * 100.0)

    # Take maximum / top 3 skill relevance scores so core matching skills are weighted strongly
    top_skill_scores = sorted(skill_relevance_scores, reverse=True)[:3] if skill_relevance_scores else []
    max_skill_score = (sum(top_skill_scores) / len(top_skill_scores)) if top_skill_scores else 50.0

    final_relevance = (max_role_score * 0.60) + (max_skill_score * 0.40)
    return round(min(100.0, max(10.0, final_relevance)), 1)
