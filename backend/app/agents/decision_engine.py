"""
Temporary reconstruction stub for Phase C3.
Decision Engine.
Reconstructed after Phase 5 data loss.
"""
import logging
from typing import Dict, Any, List
from app.agents.scorer import run_scorer
from app.agents.policy_engine import evaluate_policy
from app.agents.strategy import generate_strategy

logger = logging.getLogger(__name__)

def validate_decision_configs():
    """
    Validates decision engine configurations on startup.
    """
    logger.info("Reconstructed stub: validate_decision_configs executed.")
    return True

def run_decision_engine(parsed_resume: Dict[str, Any], required_skills: List[str] = None) -> Dict[str, Any]:
    """
    Orchestrates the decision logic without duplicating business rules.
    Pipeline: Scorer -> Policy Engine -> Strategy.
    """
    if required_skills is None:
        required_skills = []
        
    # 1. Scorer (calculates dimension scores and overall score)
    scorer_output = run_scorer(parsed_resume, required_skills)
    
    # 2. Policy Engine (evaluates gates, does not recalculate scores)
    policy_output = evaluate_policy(scorer_output, required_skills)
    
    # 3. Strategy (generates recruiter-facing recommendation tiers)
    strategy_output = generate_strategy(scorer_output, policy_output)
    
    # 4. Assemble final Decision Engine output
    decision = {
        "overall_score": scorer_output.get("overall_score", 0),
        "dimension_scores": scorer_output.get("dimension_scores", {}),
        "evidence_states": scorer_output.get("evidence_states", {}),
        "policy_eligible": policy_output.get("is_eligible", False),
        "policy_flags": policy_output.get("flags", []),
        "recommendation": strategy_output,
        "recommendation_basis": strategy_output.get("recommendation_basis", {})
    }
    
    return decision
