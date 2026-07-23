from typing import Dict, Any, List

def generate_strategy(scorer_output: Dict[str, Any], policy_output: Dict[str, Any]) -> Dict[str, Any]:
    overall_score = scorer_output.get("overall_score", 0)
    is_eligible = policy_output.get("is_eligible", False)
    evidence_states = scorer_output.get("evidence_states", {})
    dimension_scores = scorer_output.get("dimension_scores", {})

    matched = evidence_states.get("MATCHED", [])
    missing = evidence_states.get("MISSING", [])
    inferred = evidence_states.get("INFERRED", [])

    tier = "Reject"
    reasoning = []

    if not is_eligible:
        tier = "Reject"
        reasoning.append("Candidate failed one or more mandatory policy gates.")
        for flag in policy_output.get("flags", []):
            reasoning.append(f" - {flag}")
    else:
        if overall_score >= 90:
            tier = "Strong Hire"
            reasoning.append("Exceptional candidate exceeding all baseline thresholds.")
        elif overall_score >= 75:
            tier = "Hire"
            reasoning.append("Candidate meets primary requirements with solid skill alignment.")
        elif overall_score >= 60:
            tier = "Interview"
            reasoning.append("Borderline candidate. Requires deep interview validation.")
        else:
            tier = "Hold"
            reasoning.append("Candidate preserved by policy override but scores low.")

    strengths = []
    if matched:
        strengths.append(f"Strong proficiency in {', '.join(matched[:4])}")
    if inferred:
        strengths.append(f"Demonstrated aptitude for {', '.join(inferred[:3])}")
    matched_skill_dim = dimension_scores.get("skill_match", {})
    if hasattr(matched_skill_dim, "score"):
        skill_score = matched_skill_dim.score
    elif isinstance(matched_skill_dim, dict):
        skill_score = matched_skill_dim.get("score", 0)
    else:
        skill_score = 0
    if skill_score >= 80:
        strengths.append("Strong overall skill match with job requirements.")

    weaknesses = []
    if missing:
        weaknesses.append(f"Missing key skills: {', '.join(missing[:5])}")
    if not is_eligible:
        for flag in policy_output.get("flags", []):
            weaknesses.append(flag)

    return {
        "hiring_recommendation": tier,
        "recommendation_basis": {
            "strengths": strengths,
            "weaknesses": weaknesses,
            "critical_missing_skills": policy_output.get("critical_missing", []),
            "domain_alignment": "Technical domain alignment assessed from resume content.",
            "reasoning": "\n".join(reasoning)
        }
    }
