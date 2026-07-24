"""
Section-Aware Semantic Similarity Engine.
Parses candidate resume and JD into structured sections and computes section-level similarities.
Replaces whole-document black-box embeddings with interpretable, section-aware multi-domain semantic scoring.
"""
from typing import Dict, Any, List
from app.core.domain_classifier import (
    classify_text_domain,
    classify_multi_domain_profile,
    compute_multi_domain_alignment
)

SECTION_WEIGHTS = {
    "role_similarity": 0.30,
    "skill_similarity": 0.25,
    "project_similarity": 0.20,
    "responsibility_similarity": 0.15,
    "experience_similarity": 0.10,
}

def evaluate_role_title_similarity(candidate_roles: List[str], target_role: str, candidate_domain: str, jd_domain: str) -> int:
    cand_str = " ".join(candidate_roles).lower()
    target_lower = target_role.lower()

    if any(target_lower in r.lower() for r in candidate_roles):
        return 98 if "senior" in cand_str or "lead" in cand_str or "dr" in cand_str else 90
    elif candidate_domain == jd_domain:
        return 85
    elif (candidate_domain, jd_domain) in [("data_science", "machine_learning"), ("machine_learning", "data_science")]:
        return 75
    elif (candidate_domain, jd_domain) in [("backend_engineering", "data_science"), ("machine_learning", "backend_engineering")]:
        return 45
    else:
        return 15

def evaluate_skill_inventory_similarity(candidate_skills: List[str], required_skills: List[str], candidate_domain: str, jd_domain: str) -> int:
    if not required_skills:
        return 80

    cand_skills_lower = set(s.lower() for s in candidate_skills)
    req_skills_lower = set(s.lower() for s in required_skills)

    direct_overlap = cand_skills_lower.intersection(req_skills_lower)
    overlap_ratio = len(direct_overlap) / len(req_skills_lower)

    if candidate_domain == jd_domain:
        return int(round(30 + overlap_ratio * 68))
    elif candidate_domain in ("backend_engineering", "machine_learning") and jd_domain in ("data_science", "machine_learning"):
        return int(round(15 + overlap_ratio * 55))
    else:
        return int(round(5 + overlap_ratio * 35))

def evaluate_project_portfolio_similarity(parsed_resume: Dict[str, Any], candidate_domain: str, jd_domain: str) -> int:
    projects = parsed_resume.get("projects", [])
    if not projects:
        if candidate_domain == jd_domain:
            return 75
        elif candidate_domain in ("backend_engineering", "machine_learning") and jd_domain == "data_science":
            return 45
        else:
            return 10

    proj_text = " ".join([f"{p.get('title', '')} {p.get('description', '')}" for p in projects if isinstance(p, dict)]).lower()

    if jd_domain in ("data_science", "machine_learning"):
        ai_ml_keywords = ["model", "neural", "deep learning", "llm", "transformers", "pytorch", "tensorflow", "vector", "qdrant", "pinecone", "predictive", "recommendation", "scikit-learn"]
        matches = sum(1 for kw in ai_ml_keywords if kw in proj_text)
        if matches >= 3:
            return 95
        elif matches >= 1:
            return 75
        else:
            return 10 if candidate_domain in ("fullstack_mern", "frontend_engineering") else 45

    return 70

def evaluate_responsibility_similarity(parsed_resume: Dict[str, Any], candidate_domain: str, jd_domain: str) -> int:
    work_history = parsed_resume.get("work_history", [])
    if not work_history:
        return 15 if candidate_domain != jd_domain else 70

    work_text = " ".join([str(w.get("description", "")) for w in work_history if isinstance(w, dict)]).lower()

    if jd_domain in ("data_science", "machine_learning"):
        if any(k in work_text for k in ["predictive machine learning", "statistical modeling", "deep learning", "feature engineering"]):
            return 95
        elif any(k in work_text for k in ["data science", "machine learning", "scikit-learn", "eda", "baseline"]):
            return 75
        elif any(k in work_text for k in ["backend", "fastapi", "django", "microservices", "python"]):
            return 55
        else:
            return 15

    return 70

def evaluate_experience_trajectory_similarity(parsed_resume: Dict[str, Any], candidate_domain: str, jd_domain: str) -> int:
    work_history = parsed_resume.get("work_history", [])
    years_est = len(work_history) * 2

    if candidate_domain == jd_domain:
        return min(98, 70 + years_est * 5)
    elif candidate_domain in ("backend_engineering", "machine_learning") and jd_domain == "data_science":
        return min(75, 45 + years_est * 4)
    else:
        return min(30, 15 + years_est * 3)

def compute_section_aware_semantic_similarity(
    parsed_resume: Dict[str, Any],
    jd_text: str,
    target_role: str,
    required_skills: List[str]
) -> Dict[str, Any]:
    work_history = parsed_resume.get("work_history", [])
    years_exp = len(work_history) * 2.0

    hard_skills = parsed_resume.get("hard_skills", [])
    skills_dict = parsed_resume.get("skills", {})
    all_cand_skills = list(hard_skills)
    if isinstance(skills_dict, dict):
        for slist in skills_dict.values():
            if isinstance(slist, list):
                all_cand_skills.extend([str(s) for s in slist])

    raw_text = parsed_resume.get("raw_resume_text") or ""
    roles = [w.get("role", "") for w in work_history if isinstance(w, dict) and w.get("role")]
    if not roles and parsed_resume.get("personal_info", {}).get("title"):
        raw_text = parsed_resume.get("raw_resume_text", "")
    if not raw_text:
        roles_list = [str(w.get("role", "")) for w in work_history if isinstance(w, dict)]
        roles_list.append(str(parsed_resume.get("personal_info", {}).get("title", "")))
        skills_text = " ".join(all_cand_skills)
        work_desc = " ".join([str(w.get("description", "")) for w in work_history if isinstance(w, dict)])
        raw_text = f"{' '.join(roles_list)} {skills_text} {work_desc}"

    role_hint = " ".join(roles)
    cand_profiles = classify_multi_domain_profile(raw_text, candidate_roles_hint=role_hint)
    jd_domain_id = classify_text_domain(jd_text, role_title_hint="")

    domain_align = compute_multi_domain_alignment(
        candidate_profiles=cand_profiles,
        jd_domain=jd_domain_id,
        years_experience=years_exp
    )

    best_cand_domain_id = cand_profiles[0]["domain_id"]
    for p in cand_profiles:
        if p["domain"] == domain_align["best_matching_domain"]:
            best_cand_domain_id = p["domain_id"]

    hard_skills = parsed_resume.get("hard_skills", [])
    skills_dict = parsed_resume.get("skills", {})
    all_cand_skills = list(hard_skills)
    if isinstance(skills_dict, dict):
        for slist in skills_dict.values():
            if isinstance(slist, list):
                all_cand_skills.extend([str(s) for s in slist])

    s_role = evaluate_role_title_similarity(roles, target_role, best_cand_domain_id, jd_domain_id)
    s_skill = evaluate_skill_inventory_similarity(all_cand_skills, required_skills, best_cand_domain_id, jd_domain_id)
    s_project = evaluate_project_portfolio_similarity(parsed_resume, best_cand_domain_id, jd_domain_id)
    s_resp = evaluate_responsibility_similarity(parsed_resume, best_cand_domain_id, jd_domain_id)
    s_exp = evaluate_experience_trajectory_similarity(parsed_resume, best_cand_domain_id, jd_domain_id)

    raw_weighted = (
        s_role * SECTION_WEIGHTS["role_similarity"] +
        s_skill * SECTION_WEIGHTS["skill_similarity"] +
        s_project * SECTION_WEIGHTS["project_similarity"] +
        s_resp * SECTION_WEIGHTS["responsibility_similarity"] +
        s_exp * SECTION_WEIGHTS["experience_similarity"]
    )

    multiplier = domain_align["penalty_multiplier"]
    if multiplier >= 0.85:
        final_semantic = int(round(raw_weighted))
    else:
        final_semantic = int(round(raw_weighted * multiplier))

    final_semantic = min(98, max(0, final_semantic))

    return {
        "overall_semantic_similarity": final_semantic,
        "domain_alignment": domain_align["match_type"],
        "domain_alignment_score": domain_align["alignment_score"],
        "domain_penalty_multiplier": round(multiplier, 2),
        "domain_cap": domain_align.get("domain_cap", 100),
        "primary_domain": domain_align["primary_domain"],
        "best_matching_domain": domain_align["best_matching_domain"],
        "candidate_domain": domain_align["best_matching_domain"],
        "jd_domain": domain_align["jd_domain"],
        "candidate_domains": domain_align["candidate_domains"],
        "domain_evidence": domain_align["domain_evidence"],
        "role_similarity": s_role,
        "skill_similarity": s_skill,
        "project_similarity": s_project,
        "responsibility_similarity": s_resp,
        "experience_similarity": s_exp
    }
