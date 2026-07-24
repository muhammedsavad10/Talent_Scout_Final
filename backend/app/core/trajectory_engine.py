"""
Deterministic Career Trajectory & Duty Progression Engine.
Analyzes work history progression and duty descriptions against target role signatures.
"""
import logging
from typing import Dict, Any, List
from app.core.role_ontology import get_canonical_role_id, ROLE_TAXONOMY

logger = logging.getLogger("talentscout_trajectory_engine")

def calculate_experience_trajectory_score(parsed_resume: Dict[str, Any], target_role_id: str) -> Dict[str, Any]:
    """
    Evaluates Experience Alignment deterministically using trajectory direction and duty descriptions.
    """
    work_history = parsed_resume.get("work_history", [])
    role_meta = ROLE_TAXONOMY.get(target_role_id, ROLE_TAXONOMY["backend_developer"])
    
    if not work_history:
        return {
            "score": 30,
            "confidence": 80,
            "reasoning": "No work history entries cataloged to evaluate experience trajectory.",
            "trajectory_type": "Unverified"
        }

    core_skills = role_meta["core_skills"]
    total_roles = len(work_history)
    aligned_roles_count = 0
    duty_matches_count = 0

    reasons = []

    for idx, work in enumerate(work_history):
        if not isinstance(work, dict):
            continue
        role_title = work.get("role", "")
        desc = (work.get("description") or "").lower()
        
        canonical_id = get_canonical_role_id(role_title)
        
        # Check title alignment
        if canonical_id == target_role_id or canonical_id in role_meta.get("related_roles", []):
            aligned_roles_count += 1
            reasons.append(f"Role {idx+1} ({role_title}) aligns with target domain.")
            
        # Check duty description alignment
        found_duties = [s for s in core_skills if s in desc]
        if found_duties:
            duty_matches_count += 1

    title_ratio = aligned_roles_count / max(1, total_roles)
    duty_ratio = duty_matches_count / max(1, total_roles)

    # Calculate experience alignment score
    trajectory_score = int(55 + (25 * title_ratio) + (20 * duty_ratio))
    trajectory_score = max(30, min(98, trajectory_score))

    if title_ratio >= 0.5:
        trajectory_type = "Coherent Progression"
    elif duty_ratio >= 0.5:
        trajectory_type = "Cross-Domain Technical Transfer"
    else:
        trajectory_type = "Divergent Career Field"

    reasoning = (
        f"Career trajectory evaluated as '{trajectory_type}'. "
        f"{aligned_roles_count}/{total_roles} direct/related roles, {duty_matches_count}/{total_roles} roles with matching core duties."
    )

    return {
        "score": trajectory_score,
        "confidence": 90,
        "reasoning": reasoning,
        "trajectory_type": trajectory_type,
        "aligned_roles_count": aligned_roles_count
    }
