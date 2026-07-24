"""
Decision Engine for TalentScout Enterprise.
Orchestrates pipeline execution (Scorer -> Policy Engine -> Strategy)
and generates transparent candidate decision traces.
"""
import logging
from typing import Dict, Any, List
from app.agents.scorer import run_scorer
from app.agents.policy_engine import evaluate_policy
from app.agents.strategy import generate_strategy
from app.core.prerequisite_engine import classify_skill_category

logger = logging.getLogger("talentscout_decision_engine")

def validate_decision_configs():
    logger.info("validate_decision_configs executed successfully.")
    return True

def generate_decision_trace(
    scorer_output: Dict[str, Any],
    policy_output: Dict[str, Any],
    strategy_output: Dict[str, Any],
    required_skills: List[str],
    parsed_resume: Dict[str, Any]
) -> Dict[str, Any]:
    overall_score = scorer_output.get("overall_score", 0)
    dimensions = scorer_output.get("dimension_scores", {})
    
    explicit_dim = dimensions.get("explicit_keyword_match", {})
    explicit_score = explicit_dim.score if hasattr(explicit_dim, "score") else (explicit_dim.get("score", 0) if isinstance(explicit_dim, dict) else 0)
    
    semantic_dim = dimensions.get("semantic_similarity", {})
    semantic_score = semantic_dim.score if hasattr(semantic_dim, "score") else (semantic_dim.get("score", 0) if isinstance(semantic_dim, dict) else 0)

    evidence = scorer_output.get("evidence_states", {})
    matched = set(evidence.get("MATCHED", []))
    inferred = set(evidence.get("INFERRED", []))
    equivalent = set(evidence.get("EQUIVALENT", []))

    work_entries = parsed_resume.get("work_history", [])
    years_est = len(work_entries) * 2

    critical_status = []
    for req in required_skills:
        cat = classify_skill_category(req)
        if req in matched:
            st = "Explicit"
        elif req in inferred:
            st = "Inferred"
        elif req in equivalent:
            st = "Equivalent"
        else:
            st = f"Missing ({cat})"
        critical_status.append({"skill": req, "category": cat, "status": st})

    policy_eligible = policy_output.get("is_eligible", False)
    recommendation = strategy_output.get("hiring_recommendation", "Unknown")
    reasoning = strategy_output.get("recommendation_basis", {}).get("reasoning", "")

    trace = {
        "overall_score": overall_score,
        "explicit_match_score": explicit_score,
        "semantic_similarity_score": semantic_score,
        "relevant_experience": f"PASS ({years_est} years)" if years_est >= 3 else f"INFO ({years_est} years)",
        "skill_status_breakdown": critical_status,
        "policy_decision": "PASS" if policy_eligible else "FAIL",
        "policy_overrides": policy_output.get("policy_overrides", []),
        "recommendation": recommendation,
        "reason": reasoning
    }

    logger.info("========== CANDIDATE DECISION TRACE ==========")
    logger.info(f"Overall Score: {overall_score} | Explicit: {explicit_score}% | Semantic: {semantic_score}%")
    logger.info(f"Policy Decision: {trace['policy_decision']} | Recommendation: {recommendation}")
    logger.info(f"Reason: {reasoning}")
    logger.info("===============================================")

    return trace

def run_decision_engine(
    parsed_resume: Dict[str, Any],
    required_skills: List[str] = None,
    target_role: str = "Software Engineer",
    raw_resume_text: str = "",
    jd_text: str = ""
) -> Dict[str, Any]:
    if required_skills is None:
        required_skills = []
        
    scorer_output = run_scorer(
        parsed_resume,
        required_skills,
        target_role=target_role,
        raw_resume_text=raw_resume_text,
        jd_text=jd_text
    )
    scorer_output["parsed_resume"] = parsed_resume
    
    policy_output = evaluate_policy(scorer_output, required_skills, parsed_resume=parsed_resume)
    strategy_output = generate_strategy(scorer_output, policy_output)
    
    trace = generate_decision_trace(scorer_output, policy_output, strategy_output, required_skills, parsed_resume)

    from app.core.hiring_priority import compute_hiring_priority_score
    eval_payload = {
        "result": {
            "overall_score": scorer_output.get("overall_score", 0),
            "raw_resume_text": parsed_resume.get("raw_resume_text", ""),
            "projects": parsed_resume.get("projects", []),
            "work_history": parsed_resume.get("work_history", []),
            "experience": parsed_resume.get("experience", []),
            "certifications": parsed_resume.get("certifications", []),
            "personal_info": parsed_resume.get("personal_info", {})
        },
        "parsed_resume": parsed_resume,
        "raw_resume_text": parsed_resume.get("raw_resume_text", "")
    }
    hiring_priority = compute_hiring_priority_score(eval_payload, parsed_resume=parsed_resume)

    decision = {
        "overall_score": scorer_output.get("overall_score", 0),
        "hiring_priority_score": hiring_priority["hiring_priority_score"],
        "hiring_priority": hiring_priority,
        "dimension_scores": scorer_output.get("dimension_scores", {}),
        "evidence_states": scorer_output.get("evidence_states", {}),
        "policy_eligible": policy_output.get("is_eligible", False),
        "policy_flags": policy_output.get("flags", []),
        "policy_overrides": policy_output.get("policy_overrides", []),
        "recommendation": strategy_output,
        "recommendation_basis": strategy_output.get("recommendation_basis", {}),
        "decision_trace": trace,
        "certification_suitability": scorer_output.get("certification_suitability", {}),
        "semantic_breakdown": scorer_output.get("semantic_breakdown", {})
    }

    return decision
