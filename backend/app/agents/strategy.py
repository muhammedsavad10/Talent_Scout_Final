from typing import Dict, Any, List
from app.core.criticality_engine import CRITICALITY_THRESHOLDS

def evaluate_recommendation_confidence(
    overall_score: int,
    semantic_score: int,
    explicit_score: int,
    is_eligible: bool,
    critical_missing: List[str]
) -> Dict[str, Any]:
    if not is_eligible or overall_score < 45:
        return {
            "level": "Low",
            "reasoning": "Low confidence due to failed policy validation or score below qualification baseline."
        }

    if overall_score >= 80 and semantic_score >= 85 and not critical_missing:
        return {
            "level": "High",
            "reasoning": "High confidence in recommendation. Candidate demonstrates strong semantic alignment, all critical competencies are satisfied, and missing terms are secondary/preferred only."
        }
    elif overall_score >= 60 and (semantic_score >= 70 or explicit_score >= 60):
        return {
            "level": "Medium",
            "reasoning": "Medium confidence in recommendation. Overall match score is acceptable, with solid technical domain background."
        }
    else:
        return {
            "level": "Low",
            "reasoning": "Low confidence in recommendation. Match score is near baseline threshold; manual interview verification is recommended."
        }

def generate_strategy(scorer_output: Dict[str, Any], policy_output: Dict[str, Any]) -> Dict[str, Any]:
    overall_score = scorer_output.get("overall_score", 0)
    is_eligible = policy_output.get("is_eligible", False)
    evidence_states = scorer_output.get("evidence_states", {})
    dimension_scores = scorer_output.get("dimension_scores", {})

    explicit_dim = dimension_scores.get("explicit_keyword_match", {})
    explicit_score = explicit_dim.score if hasattr(explicit_dim, "score") else (explicit_dim.get("score", 0) if isinstance(explicit_dim, dict) else 0)

    semantic_dim = dimension_scores.get("semantic_similarity", {})
    semantic_score = semantic_dim.score if hasattr(semantic_dim, "score") else (semantic_dim.get("score", 0) if isinstance(semantic_dim, dict) else 0)

    matched = evidence_states.get("EXPLICITLY_MATCHED", evidence_states.get("MATCHED", []))
    missing = evidence_states.get("EXPLICITLY_MISSING", evidence_states.get("MISSING", []))
    inferred = evidence_states.get("INFERRED", [])
    equivalent = evidence_states.get("EQUIVALENT", [])

    criticality_info = policy_output.get("job_criticality", {
        "criticality_level": "Professional",
        "display_name": "Professional Role",
        "thresholds": CRITICALITY_THRESHOLDS["Professional"]
    })
    thresholds = criticality_info.get("thresholds", CRITICALITY_THRESHOLDS["Professional"])

    tier = "Reject"
    reasoning = []

    if not is_eligible:
        tier = "Reject"
        reasoning.append("Candidate failed mandatory policy validation:")
        for flag in policy_output.get("flags", []):
            reasoning.append(f" • {flag}")
    else:
        if overall_score >= thresholds["strong_hire"]:
            tier = "Strong Hire"
            reasoning.append(f"• Overall match score ({overall_score}%) exceeds the {criticality_info['display_name']} Strong Hire threshold ({thresholds['strong_hire']}%).")
        elif overall_score >= thresholds["hire"]:
            tier = "Hire"
            reasoning.append(f"• Overall match score ({overall_score}%) meets the {criticality_info['display_name']} target threshold ({thresholds['hire']}%).")
        elif overall_score >= thresholds["interview"]:
            tier = "Interview"
            reasoning.append(f"• Overall match score ({overall_score}%) meets the {criticality_info['display_name']} Interview threshold ({thresholds['interview']}%). Recommend validating technical depth.")
        elif overall_score >= thresholds["review"]:
            tier = "Review"
            reasoning.append(f"• Overall match score ({overall_score}%) suggests manual recruiter review for {criticality_info['display_name']}.")
        else:
            tier = "Reject"
            reasoning.append(f"• Overall match score ({overall_score}%) is below baseline qualification threshold ({thresholds['review']}%).")

        reasoning.append(f"• Evaluation Breakdown: Explicit ATS Keyword Match = {explicit_score}%, Semantic AI Similarity = {semantic_score}%.")

        if equivalent:
            reasoning.append(f"• Equivalent Technologies: Demonstrated proficiency in {', '.join(equivalent)}.")
        if inferred:
            reasoning.append(f"• Concept & Prerequisite Alignment: Demonstrated capability in {', '.join(inferred)}.")

        policy_overrides = policy_output.get("policy_overrides", [])
        if policy_overrides:
            for override in policy_overrides:
                reasoning.append(f"• {override}")

    critical_missing = policy_output.get("critical_missing", [])
    confidence_data = evaluate_recommendation_confidence(
        overall_score=overall_score,
        semantic_score=semantic_score,
        explicit_score=explicit_score,
        is_eligible=is_eligible,
        critical_missing=critical_missing
    )

    strengths = []
    if matched:
        strengths.append(f"Explicit ATS keyword matches: {', '.join(matched[:5])}")
    if semantic_score >= 75:
        strengths.append(f"High semantic AI alignment ({semantic_score}%) with target role requirements")
    if equivalent:
        strengths.append(f"Equivalent technology alignment: {', '.join(equivalent)}")
    if inferred:
        strengths.append(f"Inferred concept capability: {', '.join(inferred)}")

    weaknesses = []
    if missing:
        weaknesses.append(f"Explicitly missing terms: {', '.join(missing[:5])}")
    if not is_eligible:
        for flag in policy_output.get("flags", []):
            weaknesses.append(flag)

    return {
        "hiring_recommendation": tier,
        "confidence": confidence_data["level"],
        "confidence_reasoning": confidence_data["reasoning"],
        "job_criticality": criticality_info["criticality_level"],
        "recommendation_basis": {
            "strengths": strengths,
            "weaknesses": weaknesses,
            "critical_missing_skills": critical_missing,
            "domain_alignment": f"Technical alignment: Explicit ATS = {explicit_score}%, Semantic AI = {semantic_score}%.",
            "reasoning": "\n".join(reasoning)
        }
    }
