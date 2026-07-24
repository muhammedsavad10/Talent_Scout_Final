"""
Temporary reconstruction stub for Phase C2.
Candidate Comparator Engine.
Reconstructed after Phase 5 data loss.
"""
import logging
from typing import List, Dict, Any, Union

logger = logging.getLogger(__name__)

def safe_get(obj: Any, key: str, default: Any = None) -> Any:
    """
    Defensive extraction helper.
    Supports both Pydantic models (via getattr) and legacy dictionaries (via get).
    """
    if isinstance(obj, dict):
        return obj.get(key, default)
    return getattr(obj, key, default)

def extract_dimension_score(dimensions: Any, dim_key: str) -> float:
    """
    Extracts a score from a dimension, supporting both models and dicts.
    """
    if not dimensions:
        return 0.0
        
    dim_obj = safe_get(dimensions, dim_key)
    if dim_obj:
        return float(safe_get(dim_obj, "score", 0.0))
    return 0.0

def compare_candidates(evaluations: List[Any]) -> List[Dict[str, Any]]:
    """
    Ranks a list of candidate evaluations independently of the frontend.
    Handles partial evaluations, failed evaluations, missing optional dimensions.
    """
    valid_candidates = []
    failed_candidates = []
    
    for eval_obj in evaluations:
        # Check if it failed (e.g., missing essential keys or explicitly marked failed)
        overall_score = safe_get(eval_obj, "overall_score")
        if overall_score is None:
            failed_candidates.append(eval_obj)
            continue
            
        dimensions = safe_get(safe_get(eval_obj, "decision_engine", {}), "dimension_scores", {})
        if not dimensions and isinstance(eval_obj, dict):
             # Fallback if evaluation is flattened
             dimensions = eval_obj.get("dimension_scores", {})

        recommendation_basis = safe_get(eval_obj, "recommendation_basis", {})
        rec_section = safe_get(eval_obj, "recommendation", {})
        
        hiring_priority = safe_get(eval_obj, "hiring_priority")
        if not hiring_priority:
            from app.core.hiring_priority import compute_hiring_priority_score
            eval_dict = eval_obj if isinstance(eval_obj, dict) else (eval_obj.__dict__ if hasattr(eval_obj, "__dict__") else {})
            hiring_priority = compute_hiring_priority_score(eval_dict)
            
        hiring_priority_score = int(safe_get(hiring_priority, "hiring_priority_score", overall_score))
        hiring_priority_tier = str(safe_get(hiring_priority, "hiring_priority_tier", "Standard Review"))

        row = {
            "evaluation_id": safe_get(eval_obj, "evaluation_id", "unknown"),
            "candidate_name": safe_get(safe_get(eval_obj, "personal_info", {}), "name", "Unknown Candidate"),
            "filename": safe_get(eval_obj, "filename", "unknown.pdf"),
            "recommendation_tier": safe_get(rec_section, "hiring_recommendation", "Unknown"),
            "policy_eligible": safe_get(safe_get(eval_obj, "decision_engine", {}), "policy_eligible", False),
            "overall_score": float(overall_score),
            "hiring_priority_score": hiring_priority_score,
            "hiring_priority_tier": hiring_priority_tier,
            "hiring_priority": hiring_priority,
            "explicit_keyword_match": extract_dimension_score(dimensions, "explicit_keyword_match") or extract_dimension_score(dimensions, "skill_match"),
            "semantic_similarity": extract_dimension_score(dimensions, "semantic_similarity") or extract_dimension_score(dimensions, "role_fit"),
            "skill_match": extract_dimension_score(dimensions, "skill_match"),
            "experience_quantity": extract_dimension_score(dimensions, "experience_quantity"),
            "experience_relevance": extract_dimension_score(dimensions, "experience_relevance"),
            "experience_quality": extract_dimension_score(dimensions, "experience_quality"),
            "project_complexity": extract_dimension_score(dimensions, "project_complexity"),
            "role_fit": extract_dimension_score(dimensions, "role_fit"),
            "technical_match": extract_dimension_score(dimensions, "technical_match"),
            "experience_alignment": extract_dimension_score(dimensions, "experience_alignment"),
            "project_relevance": extract_dimension_score(dimensions, "project_relevance"),
            "evidence_confidence": extract_dimension_score(dimensions, "evidence_confidence"),
            "critical_missing": safe_get(recommendation_basis, "critical_missing_skills", []),
            "required_missing": [], 
            "strengths": safe_get(recommendation_basis, "strengths", []),
            "weaknesses": safe_get(recommendation_basis, "weaknesses", [])
        }
        valid_candidates.append(row)
        
    # Sort valid candidates primarily by Stage 2 hiring_priority_score, with Stage 1 overall_score as tiebreaker
    valid_candidates.sort(key=lambda x: (x["hiring_priority_score"], x["overall_score"]), reverse=True)
    
    # Assign ranks
    ranked = []
    for i, cand in enumerate(valid_candidates):
        cand["rank"] = i + 1
        ranked.append(cand)
        
    # Append failed candidates at the bottom with rank 999
    for f_cand in failed_candidates:
        ranked.append({
            "evaluation_id": safe_get(f_cand, "evaluation_id", "unknown"),
            "candidate_name": safe_get(safe_get(f_cand, "personal_info", {}), "name", "Failed Evaluation"),
            "filename": safe_get(f_cand, "filename", "unknown.pdf"),
            "recommendation_tier": "Failed",
            "policy_eligible": False,
            "overall_score": 0.0,
            "skill_match": 0.0,
            "experience_quantity": 0.0,
            "experience_relevance": 0.0,
            "experience_quality": 0.0,
            "project_complexity": 0.0,
            "critical_missing": [],
            "required_missing": [],
            "strengths": [],
            "weaknesses": [],
            "rank": 999
        })
        
    return ranked
