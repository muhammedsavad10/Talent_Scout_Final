"""
Temporary reconstruction stub for Phase C2.
Scoring Engine.
Reconstructed after Phase 5 data loss.
"""
from typing import Dict, List, Any
from app.models.schemas import DimensionMetadata

# Hardcoded weights for deterministic reconstruction
DIMENSION_WEIGHTS = {
    "skill_match": 0.40,
    "experience_quantity": 0.20,
    "experience_relevance": 0.25,
    "experience_quality": 0.15,
}

def collect_evidence(parsed_resume: Dict[str, Any], required_skills: List[str]) -> Dict[str, Any]:
    """
    Separated evidence collection phase.
    Categorizes skills into MATCHED, INFERRED, MISSING, CONTRADICTED.
    """
    candidate_skills = []
    if "skills" in parsed_resume and isinstance(parsed_resume["skills"], dict):
        for cat, skills in parsed_resume["skills"].items():
            if isinstance(skills, list):
                candidate_skills.extend([s.lower() for s in skills])
    
    # Also grab hard_skills if present
    candidate_skills.extend([s.lower() for s in parsed_resume.get("hard_skills", [])])
    
    evidence = {
        "MATCHED": [],
        "INFERRED": [],
        "MISSING": [],
        "CONTRADICTED": []
    }
    
    for req in required_skills:
        req_lower = req.lower()
        if req_lower in candidate_skills:
            evidence["MATCHED"].append(req)
        else:
            # Without LLM, we don't have inference yet, so default to MISSING
            evidence["MISSING"].append(req)
            
    # For duplicate detection/contradiction, assume a simplified logic
    return evidence

def score_dimension(dimension: str, evidence: Dict[str, Any], parsed_resume: Dict[str, Any]) -> DimensionMetadata:
    """
    Separated dimension scoring phase.
    """
    weight = DIMENSION_WEIGHTS.get(dimension, 0.1)
    score = 0
    confidence = 100
    evidence_list = []
    
    if dimension == "skill_match":
        total_req = len(evidence["MATCHED"]) + len(evidence["INFERRED"]) + len(evidence["MISSING"]) + len(evidence["CONTRADICTED"])
        if total_req > 0:
            # Basic deterministic scoring: Matched=1.0, Inferred=0.5
            matched = len(evidence["MATCHED"])
            inferred = len(evidence["INFERRED"])
            raw_score = (matched * 1.0 + inferred * 0.5) / total_req
            score = int(raw_score * 100)
            evidence_list.append(f"Matched {matched} out of {total_req} required skills.")
        else:
            score = 100
            evidence_list.append("No specific skills required.")
            
    elif dimension == "experience_quantity":
        # Simplified deterministic experience scoring based on work history count
        work_entries = parsed_resume.get("work_history", [])
        years_est = len(work_entries) * 2 # Assume 2 years per entry deterministically
        score = min(100, years_est * 10)
        evidence_list.append(f"Found {len(work_entries)} roles.")
        
    elif dimension == "experience_relevance":
        # Simplified
        score = 75 if evidence["MATCHED"] else 50
        evidence_list.append("Deterministic baseline relevance.")
        
    elif dimension == "experience_quality":
        score = 80
        evidence_list.append("Deterministic baseline quality.")
        
    else:
        # Fallback for unknown optional dimensions
        score = 50
        weight = 0.0
        confidence = 50
        evidence_list.append("Unknown optional dimension.")

    return DimensionMetadata(
        score=score,
        confidence=confidence,
        weight=weight,
        evidence=evidence_list,
        status="EVALUATED",
        sources=["resume"]
    )

def calculate_weighted_aggregation(dimensions: Dict[str, DimensionMetadata]) -> int:
    """
    Separated weighted aggregation phase.
    """
    total_score = 0.0
    total_weight = 0.0
    
    for dim_name, meta in dimensions.items():
        if meta.weight > 0:
            total_score += meta.score * meta.weight
            total_weight += meta.weight
            
    if total_weight > 0:
        return int(total_score / total_weight)
    return 0

def run_scorer(parsed_resume: Dict[str, Any], required_skills: List[str]) -> Dict[str, Any]:
    """
    Main entry point for the scorer.
    """
    # 1. Evidence Collection
    evidence = collect_evidence(parsed_resume, required_skills)
    
    # 2. Dimension Scoring
    dimensions = {}
    for dim in DIMENSION_WEIGHTS.keys():
        dimensions[dim] = score_dimension(dim, evidence, parsed_resume)
        
    # 3. Weighted Aggregation
    overall_score = calculate_weighted_aggregation(dimensions)
    
    return {
        "overall_score": overall_score,
        "dimension_scores": dimensions,
        "evidence_states": evidence
    }
