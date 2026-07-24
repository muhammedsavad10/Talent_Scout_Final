"""
Policy Engine for TalentScout Enterprise.
Evaluates hiring policy gates deterministically using Stage 1 outputs directly.
Stage 2 NEVER invents new scores or recalculates scores.
"""
from typing import Dict, Any, List
from app.core.prerequisite_engine import classify_skill_category, is_senior_candidate
from app.core.criticality_engine import determine_job_criticality

DEFAULT_POLICY_CONFIG = {
    "min_overall_score": 45,
    "require_education": False,
    "require_experience": False,
}

def evaluate_policy(
    scorer_output: Dict[str, Any],
    required_skills: List[str] = None,
    bypass_policy: bool = False,
    config: Dict[str, Any] = None,
    parsed_resume: Dict[str, Any] = None,
    jd_text: str = "",
    target_role: str = ""
) -> Dict[str, Any]:
    """
    Evaluates hiring policy gates on Stage 1 scorer output using Job Criticality context.
    Consumes Stage 1 outputs directly without creating or modifying scores.
    """
    if config is None:
        config = DEFAULT_POLICY_CONFIG

    if bypass_policy:
        return {
            "policy_eligible": True,
            "is_eligible": True,
            "flags": [],
            "critical_missing": [],
            "policy_overrides": ["Policy evaluation bypassed by recruiter override."]
        }

    if parsed_resume is None:
        parsed_resume = scorer_output.get("parsed_resume", {})

    overall_score = scorer_output.get("overall_score", 0)
    dimensions = scorer_output.get("dimension_scores", {})
    evidence = scorer_output.get("evidence_states", {})

    inferred_skills = set(evidence.get("INFERRED", []))
    missing_skills = evidence.get("MISSING", [])
    equivalent_skills = set(evidence.get("EQUIVALENT", []))

    is_senior = is_senior_candidate(parsed_resume)
    criticality = determine_job_criticality(jd_text, target_role)
    min_overall = config.get("min_overall_score", criticality["thresholds"]["review"])

    is_eligible = True
    flags = []
    critical_missing = []
    policy_overrides = []

    # 1. Baseline Score Gate (Consumes Stage 1 overall_score directly)
    if overall_score < min_overall:
        is_eligible = False
        flags.append(f"Overall match score ({overall_score}%) is below baseline threshold ({min_overall}%) for {criticality['display_name']}.")

    # 2. Hard Policy Gates (True Disqualifiers only for unmitigated critical requirements)
    missing_preferred_tools = []

    if required_skills:
        for req in required_skills:
            if req in missing_skills:
                category = classify_skill_category(req)
                
                # Preferred and Important missing skills flow into weighted score; NEVER cause policy rejection
                if category in ("Preferred", "Important"):
                    missing_preferred_tools.append(req)
                elif req in inferred_skills or req in equivalent_skills or (is_senior and category in ("Foundational", "Critical")):
                    policy_overrides.append(
                        f"Demonstrated domain competence covers {category.lower()} requirement '{req}' via equivalent technology, concept alignment, or seniority."
                    )
                else:
                    critical_missing.append(req)
                    is_eligible = False
                    flags.append(f"Missing mandatory critical requirement: {req}")

    if missing_preferred_tools:
        tools_str = ", ".join(missing_preferred_tools)
        policy_overrides.append(
            f"The candidate satisfies core technical requirements. Missing secondary/preferred tools ({tools_str}) were factored into the weighted score but do not disqualify the candidate."
        )

    # 3. Experience Gate
    exp_dim = dimensions.get("experience_quantity")
    if hasattr(exp_dim, "score"):
        exp_score = exp_dim.score
    elif isinstance(exp_dim, dict):
        exp_score = exp_dim.get("score", 0)
    else:
        exp_score = 0

    if config.get("require_experience") and exp_score == 0:
        is_eligible = False
        flags.append("Candidate lacks documented work history experience.")

    return {
        "policy_eligible": is_eligible,
        "is_eligible": is_eligible,
        "flags": flags,
        "critical_missing": critical_missing,
        "policy_overrides": policy_overrides,
        "job_criticality": criticality
    }
