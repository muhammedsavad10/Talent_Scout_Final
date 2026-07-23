import re
from typing import Dict, List, Any
from app.models.schemas import DimensionMetadata

DIMENSION_WEIGHTS = {
    "skill_match": 0.40,
    "experience_quantity": 0.20,
    "experience_relevance": 0.25,
    "experience_quality": 0.15,
}

def _get_raw_text(parsed_resume: Dict[str, Any]) -> str:
    return parsed_resume.get("raw_resume_text") or ""

def _skill_appears_in_text(text_lower: str, skill_name: str) -> bool:
    try:
        return bool(re.search(r'\b' + re.escape(skill_name.lower()) + r'\b', text_lower))
    except re.error:
        return skill_name.lower() in text_lower

def collect_evidence(parsed_resume: Dict[str, Any], required_skills: List[str]) -> Dict[str, Any]:
    candidate_skills_lower = set()

    if "skills" in parsed_resume and isinstance(parsed_resume["skills"], dict):
        for cat, skills in parsed_resume["skills"].items():
            if isinstance(skills, list):
                for s in skills:
                    if isinstance(s, str):
                        candidate_skills_lower.add(s.lower())

    for s in parsed_resume.get("hard_skills", []):
        if isinstance(s, str):
            candidate_skills_lower.add(s.lower())

    raw_text = _get_raw_text(parsed_resume)
    text_lower = raw_text.lower()

    evidence = {
        "MATCHED": [],
        "INFERRED": [],
        "MISSING": [],
        "CONTRADICTED": []
    }

    for req in required_skills:
        req_lower = req.lower()
        in_parsed_list = req_lower in candidate_skills_lower
        in_resume_text = _skill_appears_in_text(text_lower, req)

        if in_parsed_list or in_resume_text:
            evidence["MATCHED"].append(req)
        else:
            evidence["MISSING"].append(req)

    return evidence

def score_dimension(dimension: str, evidence: Dict[str, Any], parsed_resume: Dict[str, Any]) -> DimensionMetadata:
    weight = DIMENSION_WEIGHTS.get(dimension, 0.1)
    score = 0
    confidence = 100
    evidence_list = []

    if dimension == "skill_match":
        total_req = len(evidence["MATCHED"]) + len(evidence["INFERRED"]) + len(evidence["MISSING"]) + len(evidence["CONTRADICTED"])
        if total_req > 0:
            matched = len(evidence["MATCHED"])
            inferred = len(evidence["INFERRED"])
            raw_score = (matched * 1.0 + inferred * 0.5) / total_req
            score = int(raw_score * 100)
            matched_names = evidence["MATCHED"][:5]
            missing_names = evidence["MISSING"][:5]
            parts = []
            if matched_names:
                parts.append(f"Matched {matched}/{total_req} required skills: {', '.join(matched_names)}")
            else:
                parts.append(f"Matched {matched}/{total_req} required skills")
            if missing_names:
                parts.append(f"Missing: {', '.join(missing_names)}")
            evidence_list.extend(parts)
        else:
            score = 100
            evidence_list.append("No required skills specified for comparison.")

    elif dimension == "experience_quantity":
        work_entries = parsed_resume.get("work_history", [])
        years_est = len(work_entries) * 2
        score = min(100, years_est * 10)
        if work_entries:
            roles = [w.get("role", "Unknown") for w in work_entries[:3]]
            evidence_list.append(f"Found {len(work_entries)} roles: {', '.join(roles)}")
        else:
            evidence_list.append("No work history entries found in resume.")

    elif dimension == "experience_relevance":
        matched_skills = evidence.get("MATCHED", [])
        if matched_skills:
            score = min(100, 50 + len(matched_skills) * 10)
            evidence_list.append(f"Resume contains {len(matched_skills)} matching skills relevant to the role.")
        else:
            score = 30
            evidence_list.append("No matching skills found in resume for this role.")

    elif dimension == "experience_quality":
        work_entries = parsed_resume.get("work_history", [])
        if work_entries:
            has_detailed = sum(1 for w in work_entries if len(w.get("description", "")) > 50)
            quality_pct = (has_detailed / len(work_entries)) * 100
            score = int(quality_pct)
            evidence_list.append(f"{has_detailed}/{len(work_entries)} roles have detailed descriptions.")
        else:
            score = 30
            evidence_list.append("No detailed work history to evaluate quality.")

    else:
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
    evidence = collect_evidence(parsed_resume, required_skills)
    dimensions = {}
    for dim in DIMENSION_WEIGHTS.keys():
        dimensions[dim] = score_dimension(dim, evidence, parsed_resume)
    overall_score = calculate_weighted_aggregation(dimensions)

    return {
        "overall_score": overall_score,
        "dimension_scores": dimensions,
        "evidence_states": evidence
    }
