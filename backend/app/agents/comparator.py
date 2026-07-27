"""
Candidate Comparator Engine for TalentScout Enterprise (v1.8.5).
Implements Hierarchical (Lexicographic) Candidate Ranking with Technical Dominance Gating.

Ranking Philosophy:
1. Primary Discriminator: Stage 1 Technical Match. Differences > technical_margin (default 3.0) strictly determine rank.
2. Secondary Discriminator: Stage 2 Hiring Priority. Acts as tie-breaker ONLY when Stage 1 scores are within margin.
3. Tertiary Discriminator: Evidence Confidence, Project Relevance, Experience Quality.
"""
import logging
import functools
from typing import List, Dict, Any, Union

logger = logging.getLogger("talentscout_candidate_comparator")

def safe_get(obj: Any, key: str, default: Any = None) -> Any:
    """Defensive extraction helper supporting Pydantic models and dictionaries."""
    if isinstance(obj, dict):
        return obj.get(key, default)
    return getattr(obj, key, default)

def extract_dimension_score(dimensions: Any, dim_key: str) -> float:
    """Extracts a score from a dimension, supporting both models and dicts."""
    if not dimensions:
        return 0.0
    dim_obj = safe_get(dimensions, dim_key)
    if dim_obj:
        return float(safe_get(dim_obj, "score", 0.0))
    return 0.0

def candidate_comparator_key(a: Dict[str, Any], b: Dict[str, Any], margin: float = 3.0) -> int:
    """
    Lexicographic candidate comparison key function.
    Returns -1 if 'a' should precede 'b' (higher rank), 1 if 'b' should precede 'a', 0 if equal.
    """
    s1_a = float(a.get("overall_score", 0.0))
    s1_b = float(b.get("overall_score", 0.0))
    diff_s1 = s1_a - s1_b

    # Primary Sort: Technical Dominance Gating (if difference exceeds margin)
    if diff_s1 > margin:
        return -1
    elif diff_s1 < -margin:
        return 1

    # Secondary Sort: Stage 2 Hiring Priority Score (within technical match margin)
    s2_a = float(a.get("hiring_priority_score", 0.0))
    s2_b = float(b.get("hiring_priority_score", 0.0))
    if s2_a != s2_b:
        return -1 if s2_a > s2_b else 1

    # Tertiary Sort: Exact Stage 1 Match, Evidence Confidence, Experience Quality
    if s1_a != s1_b:
        return -1 if s1_a > s1_b else 1

    conf_a = float(a.get("evidence_confidence", 0.95))
    conf_b = float(b.get("evidence_confidence", 0.95))
    if conf_a != conf_b:
        return -1 if conf_a > conf_b else 1

    exp_a = float(a.get("experience_quality", 0.0))
    exp_b = float(b.get("experience_quality", 0.0))
    if exp_a != exp_b:
        return -1 if exp_a > exp_b else 1

    return 0

def compare_candidates(evaluations: List[Any], technical_margin: float = 3.0) -> List[Dict[str, Any]]:
    """
    v1.8.5 Hierarchical Lexicographic Candidate Ranking Engine.
    Sorts candidate evaluations using Technical Dominance Gating and Stage 2 Tie-Breaking.
    """
    valid_candidates = []
    failed_candidates = []

    for eval_obj in evaluations:
        overall_score = safe_get(eval_obj, "overall_score")
        if overall_score is None:
            failed_candidates.append(eval_obj)
            continue

        dimensions = safe_get(safe_get(eval_obj, "decision_engine", {}), "dimension_scores", {})
        if not dimensions and isinstance(eval_obj, dict):
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

        cand_name = safe_get(safe_get(eval_obj, "personal_info", {}), "name", "Unknown Candidate")
        strengths_list = safe_get(recommendation_basis, "strengths", [])
        missing_list = safe_get(recommendation_basis, "critical_missing_skills", [])

        score_breakdown = {
            "stage1_match_score": float(overall_score),
            "stage2_priority_score": float(hiring_priority_score),
            "ats_keyword_contribution": "20.0%",
            "semantic_match_contribution": "15.0%",
            "role_intelligence_contribution": "15.0%",
            "experience_depth_contribution": "20.0%",
            "certification_quality_contribution": "12.5%",
            "corporate_diversity_contribution": "10.0%",
            "production_impact_contribution": "5.0%",
            "leadership_level_contribution": "2.5%"
        }

        explanation_narrative = (
            f"Candidate {cand_name} scored {overall_score:.1f} in Stage 1 Technical Match "
            f"and {hiring_priority_score} in Stage 2 Hiring Priority ({hiring_priority_tier})."
        )

        row = {
            "evaluation_id": safe_get(eval_obj, "evaluation_id", "unknown"),
            "candidate_id": safe_get(eval_obj, "candidate_id", "RES_000"),
            "candidate_name": cand_name,
            "filename": safe_get(eval_obj, "filename", "unknown.pdf"),
            "recommendation_tier": safe_get(rec_section, "hiring_recommendation", "Unknown"),
            "policy_eligible": safe_get(safe_get(eval_obj, "decision_engine", {}), "policy_eligible", False),
            "overall_score": float(overall_score),
            "hiring_priority_score": hiring_priority_score,
            "hiring_priority_tier": hiring_priority_tier,
            "hiring_priority": hiring_priority,
            "score_breakdown": score_breakdown,
            "explanation_narrative": explanation_narrative,
            "explicit_keyword_match": extract_dimension_score(dimensions, "explicit_keyword_match") or extract_dimension_score(dimensions, "skill_match"),
            "semantic_similarity": extract_dimension_score(dimensions, "semantic_similarity") or extract_dimension_score(dimensions, "role_fit"),
            "skill_match": extract_dimension_score(dimensions, "skill_match"),
            "experience_quantity": extract_dimension_score(dimensions, "experience_quantity"),
            "experience_relevance": extract_dimension_score(dimensions, "experience_relevance"),
            "experience_quality": extract_dimension_score(dimensions, "experience_quality"),
            "project_complexity": float(safe_get(hiring_priority, "project_complexity", 0.0)),
            "role_fit": extract_dimension_score(dimensions, "role_fit"),
            "technical_match": extract_dimension_score(dimensions, "technical_match"),
            "experience_alignment": extract_dimension_score(dimensions, "experience_alignment"),
            "project_relevance": extract_dimension_score(dimensions, "project_relevance"),
            "evidence_confidence": float(safe_get(hiring_priority, "evidence_confidence", 0.95)),
            "critical_missing": missing_list,
            "required_missing": [],
            "strengths": strengths_list,
            "weaknesses": safe_get(recommendation_basis, "weaknesses", [])
        }
        valid_candidates.append(row)

    # Sort valid candidates using Hierarchical Lexicographic Comparator
    cmp_key = functools.cmp_to_key(lambda a, b: candidate_comparator_key(a, b, margin=technical_margin))
    valid_candidates.sort(key=cmp_key)

    # Assign ranks and generate recruiter explainability statements
    ranked = []
    for i, cand in enumerate(valid_candidates):
        cand["rank"] = i + 1
        s1 = float(cand.get("overall_score", 0.0))
        s2 = float(cand.get("hiring_priority_score", 0.0))

        if i == 0:
            cand["ranking_explanation"] = (
                f"Ranked #1 due to dominant Technical Role Match ({s1:.1f}%) and direct Role Fit ({s2:.0f})."
            )
        else:
            prev_cand = valid_candidates[i - 1]
            prev_s1 = float(prev_cand.get("overall_score", 0.0))
            if prev_s1 - s1 > technical_margin:
                cand["ranking_explanation"] = (
                    f"Ranked #{i+1}: Technical role match ({s1:.1f}%) is below Rank #{i} ({prev_s1:.1f}%) "
                    f"by >{technical_margin:.1f} points (Technical Dominance)."
                )
            else:
                cand["ranking_explanation"] = (
                    f"Ranked #{i+1}: Comparable technical match ({s1:.1f}% vs {prev_s1:.1f}%), "
                    f"differentiated by Stage 2 Hiring Priority ({s2:.0f})."
                )
        ranked.append(cand)

    # Append failed candidates at bottom
    for f_cand in failed_candidates:
        ranked.append({
            "evaluation_id": safe_get(f_cand, "evaluation_id", "unknown"),
            "candidate_name": safe_get(safe_get(f_cand, "personal_info", {}), "name", "Failed Evaluation"),
            "filename": safe_get(f_cand, "filename", "unknown.pdf"),
            "recommendation_tier": "Failed",
            "policy_eligible": False,
            "overall_score": 0.0,
            "hiring_priority_score": 0,
            "skill_match": 0.0,
            "rank": 999
        })

    return ranked
