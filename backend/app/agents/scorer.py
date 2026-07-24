import re
from typing import Dict, List, Any, Optional
from app.models.schemas import DimensionMetadata
from app.agents.role_intelligence import evaluate_role_intelligence
from app.core.prerequisite_engine import infer_foundational_skills, get_inference_credit_weight
from app.agents.deterministic_extractor import extract_skills_deterministically

DIMENSION_WEIGHTS = {
    "skill_match": 0.40,
    "experience_quantity": 0.20,
    "experience_relevance": 0.25,
    "experience_quality": 0.15,
}

def _get_raw_text(parsed_resume: Dict[str, Any]) -> str:
    if parsed_resume.get("raw_resume_text"):
        return parsed_resume["raw_resume_text"]
    work = parsed_resume.get("work_history", [])
    roles = [str(w.get("role", "")) for w in work if isinstance(w, dict)]
    work_text = " ".join([str(w.get("description", "")) for w in work if isinstance(w, dict)])
    skills = " ".join(parsed_resume.get("hard_skills", []))
    return f"{' '.join(roles)} {skills} {work_text}"

def _skill_appears_in_text(text_lower: str, skill_name: str) -> bool:
    try:
        return bool(re.search(r'\b' + re.escape(skill_name.lower()) + r'\b', text_lower))
    except re.error:
        return skill_name.lower() in text_lower

def collect_evidence(parsed_resume: Dict[str, Any], required_skills: List[str]) -> Dict[str, Any]:
    candidate_skills_set = set()

    if "skills" in parsed_resume and isinstance(parsed_resume["skills"], dict):
        for cat, skills in parsed_resume["skills"].items():
            if isinstance(skills, list):
                for s in skills:
                    if isinstance(s, str):
                        candidate_skills_set.add(s)

    for s in parsed_resume.get("hard_skills", []):
        if isinstance(s, str):
            candidate_skills_set.add(s)

    raw_text = _get_raw_text(parsed_resume)
    text_lower = raw_text.lower()

    if raw_text:
        for sk_obj in extract_skills_deterministically(raw_text, "resume"):
            if isinstance(sk_obj, dict) and sk_obj.get("name"):
                candidate_skills_set.add(sk_obj["name"])

    # Stage 1A — Explicit ATS Match: Pure literal presence check
    explicitly_matched = []
    explicitly_missing = []

    for req in required_skills:
        if _skill_appears_in_text(text_lower, req) or req in candidate_skills_set:
            explicitly_matched.append(req)
            candidate_skills_set.add(req)
        else:
            explicitly_missing.append(req)

    # Stage 1B — Prerequisite, Concept Support & Equivalence Inferences for Semantic AI Engine
    res = infer_foundational_skills(candidate_skills_set, required_skills, parsed_resume=parsed_resume)

    evidence = {
        "EXPLICITLY_MATCHED": explicitly_matched,
        "EXPLICITLY_MISSING": explicitly_missing,
        "MATCHED": explicitly_matched,
        "INFERRED": res["INFERRED"],
        "EQUIVALENT": res.get("EQUIVALENT", []),
        "MISSING": explicitly_missing,
        "CONTRADICTED": [],
        "inferred_details": res.get("inferred_details", {}),
        "credit_weight": res.get("credit_weight", 0.85),
        "equivalent_weight": res.get("equivalent_weight", 0.80)
    }

    return evidence

def score_dimension(dimension: str, evidence: Dict[str, Any], parsed_resume: Dict[str, Any]) -> DimensionMetadata:
    weight = DIMENSION_WEIGHTS.get(dimension, 0.1)
    score = 0
    confidence = 100
    evidence_list = []

    if dimension == "skill_match":
        total_req = len(evidence.get("EXPLICITLY_MATCHED", [])) + len(evidence.get("EXPLICITLY_MISSING", []))
        if total_req > 0:
            matched = len(evidence.get("EXPLICITLY_MATCHED", []))
            raw_score = matched / total_req
            score = int(raw_score * 100)
            matched_names = evidence.get("EXPLICITLY_MATCHED", [])[:5]
            missing_names = evidence.get("EXPLICITLY_MISSING", [])[:5]
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
        matched_skills = evidence.get("EXPLICITLY_MATCHED", [])
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

def run_scorer(
    parsed_resume: Dict[str, Any],
    required_skills: List[str],
    target_role: str = "Software Engineer",
    raw_resume_text: str = "",
    jd_text: str = ""
) -> Dict[str, Any]:
    if not jd_text and required_skills:
        jd_text = f"{target_role} requiring {', '.join(required_skills)}"

    if raw_resume_text and not parsed_resume.get("raw_resume_text"):
        parsed_resume["raw_resume_text"] = raw_resume_text

    evidence = collect_evidence(parsed_resume, required_skills)
    dimensions = {}

    # 1. Compute Legacy Dimensions for backwards compatibility
    for dim in DIMENSION_WEIGHTS.keys():
        dimensions[dim] = score_dimension(dim, evidence, parsed_resume)

    # 2. Compute Role Intelligence for Section-Aware Semantic Similarity
    role_data = evaluate_role_intelligence(
        parsed_resume, jd_text, target_role, raw_resume_text, required_skills=required_skills
    )
    semantic_breakdown = role_data.get("semantic_breakdown", {})
    
    # 3. Stage 1A — Explicit Keyword Match Score (Weight: 40% ATS Scorer)
    # Pure literal ATS matching score — NO inferences, NO equivalents, NO embeddings!
    total_req = len(required_skills)
    explicit_matched_count = len(evidence.get("EXPLICITLY_MATCHED", []))
    explicit_missing_count = len(evidence.get("EXPLICITLY_MISSING", []))

    if total_req > 0:
        keyword_score = int(round((explicit_matched_count / total_req) * 100))
        keyword_score = min(100, max(0, keyword_score))
    else:
        keyword_score = 100

    matched_explicit_names = evidence.get("EXPLICITLY_MATCHED", [])
    missing_explicit_names = evidence.get("EXPLICITLY_MISSING", [])

    keyword_evidence = [
        f"ATS Explicit Match: {explicit_matched_count}/{total_req if total_req > 0 else 'All'} required terms literally present" + (f": {', '.join(matched_explicit_names[:5])}" if matched_explicit_names else "")
    ]
    if missing_explicit_names:
        keyword_evidence.append(f"Explicitly missing terms: {', '.join(missing_explicit_names[:5])}")

    explicit_keyword_match_dim = DimensionMetadata(
        score=keyword_score,
        confidence=100,
        weight=0.40,
        evidence=keyword_evidence,
        status="EVALUATED",
        sources=["resume"]
    )
    dimensions["explicit_keyword_match"] = explicit_keyword_match_dim
    dimensions["skill_match"] = explicit_keyword_match_dim
    dimensions["technical_match"] = explicit_keyword_match_dim

    # 4. Stage 1B — Section-Aware Semantic Similarity Score (Weight: 60% AI Engine)
    base_semantic_score = semantic_breakdown.get("overall_semantic_similarity", 75)
    domain_cap = semantic_breakdown.get("domain_cap", 100)

    semantic_boost = 0
    semantic_evidence = [
        f"Domain Alignment: {semantic_breakdown.get('domain_alignment', 'Aligned')}.",
        f"Section Similarity: Role={semantic_breakdown.get('role_similarity', 0)}%, Skills={semantic_breakdown.get('skill_similarity', 0)}%, Projects={semantic_breakdown.get('project_similarity', 0)}%, Responsibilities={semantic_breakdown.get('responsibility_similarity', 0)}%."
    ]

    inferred_details = evidence.get("inferred_details", {})
    for item_skill, detail in inferred_details.items():
        st = detail.get("status")
        reason = detail.get("reason", "")
        if st == "EQUIVALENT":
            semantic_boost += 10
            semantic_evidence.append(f"Equivalent Technology Alignment: {reason}")
        elif st in ("INFERRED", "PREFERRED_OMITTED"):
            semantic_boost += 5
            semantic_evidence.append(f"Concept & Prerequisite Support: {reason}")

    if domain_cap < 50:
        semantic_score = min(domain_cap, base_semantic_score)
    else:
        semantic_score = min(domain_cap, min(98, max(0, base_semantic_score + semantic_boost)))

    semantic_quotes = role_data.get("role_fit", {}).get("evidence_quotes", [])
    if semantic_quotes:
        semantic_evidence.append(f"Grounding Quote: '{semantic_quotes[0]}'")

    semantic_similarity_dim = DimensionMetadata(
        score=semantic_score,
        confidence=90,
        weight=0.60,
        evidence=semantic_evidence,
        status="EVALUATED",
        sources=["resume"]
    )
    dimensions["semantic_similarity"] = semantic_similarity_dim
    dimensions["role_fit"] = semantic_similarity_dim
    dimensions["experience_alignment"] = semantic_similarity_dim
    dimensions["project_relevance"] = semantic_similarity_dim

    # 5. Overall Match Score = (Explicit Keyword Match * 0.40) + (Semantic Similarity * 0.60)
    overall_score = int(round((keyword_score * 0.40) + (semantic_score * 0.60)))

    return {
        "overall_score": overall_score,
        "dimension_scores": dimensions,
        "evidence_states": evidence,
        "certification_suitability": role_data.get("certification_suitability", {}),
        "semantic_breakdown": semantic_breakdown
    }
