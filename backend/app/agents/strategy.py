"""
Temporary reconstruction stub for Phase C3.
Recommendation Strategy.
Reconstructed after Phase 5 data loss.
"""
from typing import Dict, Any

def generate_strategy(scorer_output: Dict[str, Any], policy_output: Dict[str, Any]) -> Dict[str, Any]:
    """
    Generates recruiter-facing guidance based on scorer and policy outputs.
    Does NOT modify scores.
    Returns recommendation_tier, strengths, weaknesses, critical_missing.
    """
    overall_score = scorer_output.get("overall_score", 0)
    is_eligible = policy_output.get("is_eligible", False)
    
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
            reasoning.append("Solid candidate meeting primary requirements.")
        elif overall_score >= 60:
            tier = "Interview"
            reasoning.append("Borderline candidate. Requires deep interview validation.")
        else:
            # Policy bypass case where score is low but bypassed
            tier = "Hold"
            reasoning.append("Candidate preserved by policy override but scores low.")
            
    return {
        "hiring_recommendation": tier,
        "recommendation_basis": {
            "strengths": ["Policy Eligible"] if is_eligible else [],
            "weaknesses": policy_output.get("flags", []),
            "critical_missing_skills": policy_output.get("critical_missing", []),
            "reasoning": "\n".join(reasoning)
        }
    }
