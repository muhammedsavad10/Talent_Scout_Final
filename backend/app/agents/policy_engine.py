"""
Temporary reconstruction stub for Phase C3.
Policy Engine.
Reconstructed after Phase 5 data loss.
"""
from typing import Dict, Any, List

# Fallback config due to missing YAML files
DEFAULT_POLICY_CONFIG = {
    "min_overall_score": 60,
    "min_skill_score": 50,
    "require_education": False,
    "require_experience": False,
}

def evaluate_policy(scorer_output: Dict[str, Any], required_skills: List[str] = None, bypass_policy: bool = False, config: Dict[str, Any] = None) -> Dict[str, Any]:
    """
    Evaluates hiring policy gates on scorer output.
    Does NOT recalculate scores.
    """
    if config is None:
        config = DEFAULT_POLICY_CONFIG
        
    overall_score = scorer_output.get("overall_score", 0)
    dimensions = scorer_output.get("dimension_scores", {})
    
    # Defensively get skill_score
    skill_dim = dimensions.get("skill_match")
    if hasattr(skill_dim, "score"):
        skill_score = skill_dim.score
    elif isinstance(skill_dim, dict):
        skill_score = skill_dim.get("score", 0)
    else:
        skill_score = 0
        
    evidence = scorer_output.get("evidence_states", {})
    missing_skills = evidence.get("MISSING", [])
    
    is_eligible = True
    flags = []
    critical_missing = []
    policy_overrides = []
    
    # 1. Score Gates
    if overall_score < config.get("min_overall_score", 0):
        is_eligible = False
        flags.append(f"Overall score {overall_score} below minimum {config['min_overall_score']}")
        
    if skill_score < config.get("min_skill_score", 0):
        is_eligible = False
        flags.append(f"Skill score {skill_score} below minimum {config['min_skill_score']}")
        
    # 2. Critical skills (for C3, treat all required_skills as critical if they are completely missing)
    if required_skills:
        for req in required_skills:
            if req in missing_skills:
                critical_missing.append(req)
                is_eligible = False
                flags.append(f"Missing mandatory skill: {req}")
                
    # 3. Experience gates (Stubbed)
    exp_dim = dimensions.get("experience_quantity")
    if hasattr(exp_dim, "score"):
        exp_score = exp_dim.score
    elif isinstance(exp_dim, dict):
        exp_score = exp_dim.get("score", 0)
    else:
        exp_score = 0
        
    if config.get("require_experience") and exp_score == 0:
        is_eligible = False
        flags.append("Missing mandatory experience.")

    # 4. Education gates (Stubbed)
    if config.get("require_education"):
        # We assume score lacks education right now, fail by default for test
        is_eligible = False
        flags.append("Missing mandatory education.")
        
    # 5. Policy Bypass
    if bypass_policy and not is_eligible:
        is_eligible = True
        policy_overrides.append("Policy bypassed manually.")
        
    return {
        "is_eligible": is_eligible,
        "flags": flags,
        "critical_missing": critical_missing,
        "policy_overrides": policy_overrides
    }
