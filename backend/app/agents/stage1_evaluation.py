"""
Stage 1: Deterministic Evaluation Engine.
Performs 100% deterministic parsing, skill extraction, prerequisite inferences,
dimension scoring, policy validation, and evidence gathering.
Numerical scores are calculated EXACTLY ONCE in Stage 1.
"""
import logging
from typing import Dict, List, Any
from app.agents.ingestion import parse_resume_to_json
from app.agents.parser_validation import validate_parsed_resume
from app.agents.deterministic_extractor import (
    extract_contact_info,
    extract_known_skills,
    extract_skills_from_jd
)
from app.agents.normalization import normalize_skills_list
from app.agents.role_intelligence import extract_target_role
from app.agents.decision_engine import run_decision_engine
from app.core.prerequisite_engine import infer_foundational_skills

logger = logging.getLogger("talentscout_stage1_evaluation")

def prepare_final_required_skills(jd_text: str, optional_recruiter_skills: List[str] = None) -> List[str]:
    if optional_recruiter_skills is None:
        optional_recruiter_skills = []

    extracted_jd_skills = extract_skills_from_jd(jd_text)

    normalized_map = {}
    
    # 1. Primary: Extracted JD skills
    for sk in extracted_jd_skills:
        if sk and isinstance(sk, str):
            clean = sk.strip()
            norm_k = clean.lower()
            if norm_k not in normalized_map:
                normalized_map[norm_k] = clean

    # 2. Optional: Merge Recruiter skills
    for sk in optional_recruiter_skills:
        if sk and isinstance(sk, str):
            clean = sk.strip()
            norm_k = clean.lower()
            if norm_k not in normalized_map:
                normalized_map[norm_k] = clean

    return list(normalized_map.values())

def _extract_sentence_for_skill(text: str, skill_name: str) -> str:
    if not text:
        return ""
    import re
    sentences = re.split(r'(?<=[.!?])\s+', text)
    skill_lower = skill_name.lower()
    for s in sentences:
        if skill_lower in s.lower():
            cleaned = s.strip()
            return cleaned[:250] + "..." if len(cleaned) > 250 else cleaned
    return ""

def _build_skills_evidence(evidence_states: Dict[str, Any], raw_text: str, parsed_resume: Dict) -> List[Dict[str, Any]]:
    items = []
    inferred_details = evidence_states.get("inferred_details", {})

    for status_key in ("MATCHED", "INFERRED", "MISSING"):
        skill_list = evidence_states.get(status_key, [])
        if not isinstance(skill_list, list):
            continue

        for skill_name in skill_list:
            if status_key == "MATCHED":
                status_label = "Identified"
                strength = "High"
                confidence = 100
                reasoning = "Skill explicitly found in resume matching job requirement."
            elif status_key == "INFERRED":
                status_label = "Inferred Foundation"
                strength = "Medium"
                confidence = 85
                inf_info = inferred_details.get(skill_name, {})
                triggers = inf_info.get("triggered_by", [])
                reasoning = inf_info.get("reason", f"Inferred foundation: prerequisite technology ({', '.join(triggers)}) detected.")
            else:
                status_label = "Not identified"
                strength = "Low"
                confidence = 0
                reasoning = "Skill not explicitly found in resume or supported by prerequisite ontology."

            snippet = _extract_sentence_for_skill(raw_text, skill_name)
            project_name = None

            lookup_skills = [skill_name]
            if status_key == "INFERRED":
                inf_info = inferred_details.get(skill_name, {})
                lookup_skills.extend(inf_info.get("triggered_by", []))

            for look_s in lookup_skills:
                if snippet:
                    break
                snippet = _extract_sentence_for_skill(raw_text, look_s)

            for proj in parsed_resume.get("projects", []):
                if isinstance(proj, dict):
                    desc = (proj.get("description") or "") + (proj.get("title") or "")
                    for look_s in lookup_skills:
                        if look_s.lower() in desc.lower():
                            project_name = proj.get("title")
                            if not snippet:
                                snippet = desc[:200]
                            break

            if not snippet:
                for work in parsed_resume.get("work_history", []):
                    if isinstance(work, dict):
                        desc = work.get("description") or ""
                        for look_s in lookup_skills:
                            if look_s.lower() in desc.lower():
                                snippet = desc[:200]
                                break

            items.append({
                "skill": skill_name,
                "status": status_label,
                "evidence_snippet": snippet,
                "project_name": project_name,
                "role_held": None,
                "evidence_strength": strength,
                "match_confidence": confidence,
                "reasoning": reasoning
            })
    return items

def _generate_career_timeline(parsed_resume: Dict) -> List[Dict[str, Any]]:
    work_entries = parsed_resume.get("work_history", [])
    timeline = []
    for entry in work_entries:
        if isinstance(entry, dict):
            company = entry.get("company", "Unknown")
            role = entry.get("role", "Engineer")
            desc = entry.get("description", "")
            duration = str(entry.get("duration") or entry.get("dates") or "Recent").strip()
            timeline.append({
                "period": duration,
                "year": duration,
                "dates": duration,
                "company": company,
                "role": role,
                "title": f"{role} at {company}",
                "description": desc[:150] if desc else f"Worked as {role} at {company}."
            })
    return timeline

def _generate_business_impact(parsed_resume: Dict) -> List[str]:
    impacts = []
    projects = parsed_resume.get("projects", [])
    for proj in projects:
        if isinstance(proj, dict) and proj.get("description"):
            desc = proj["description"]
            if any(w in desc.lower() for w in ["reduced", "improved", "increased", "built", "designed", "scaled", "led"]):
                impacts.append(f"Project '{proj.get('title', 'System')}': {desc[:120]}")
    if not impacts:
        work_entries = parsed_resume.get("work_history", [])
        for w in work_entries:
            if isinstance(w, dict) and w.get("description"):
                desc = w["description"]
                if len(desc) > 40:
                    impacts.append(f"Role '{w.get('role', 'Work')}': {desc[:120]}")
                    if len(impacts) >= 2:
                        break
    return impacts[:3]

def _extract_current_role_and_company(work_history: List) -> str:
    for w in work_history:
        if not isinstance(w, dict):
            continue
        role = w.get("role") or w.get("title")
        company = w.get("company") or w.get("employer")
        if role and company:
            return f"{role} at {company}"
        elif role:
            return role
        elif company:
            return company
    return "Not Mentioned"

async def run_stage1_evaluation(
    text: str,
    candidate_id: str,
    required_skills: List[str] = None,
    jd_text: str = ""
) -> Dict[str, Any]:
    if required_skills is None:
        required_skills = []

    final_required_skills = prepare_final_required_skills(jd_text, required_skills)
    logger.info(f"Stage 1: Extracted final required skills ({len(final_required_skills)}): {final_required_skills}")

    parsed_resume = parse_resume_to_json(text)
    if not parsed_resume:
        return {"status": "error", "error_stage": "stage1_parser", "message": "Failed to parse resume"}

    if "error" in parsed_resume:
        return {"status": "error", "error_stage": "stage1_parser", "message": parsed_resume["error"]}

    if "skills" in parsed_resume:
        for cat, skills_list in parsed_resume["skills"].items():
            if isinstance(skills_list, list):
                parsed_resume["skills"][cat] = normalize_skills_list(skills_list)

    if "hard_skills" in parsed_resume:
        parsed_resume["hard_skills"] = normalize_skills_list(parsed_resume["hard_skills"])

    if "projects" in parsed_resume and isinstance(parsed_resume["projects"], list):
        from app.core.project_deduplicator import deduplicate_projects
        parsed_resume["projects"] = deduplicate_projects(parsed_resume["projects"])

    validation_report = validate_parsed_resume(parsed_resume)
    if validation_report["overall_score"] < 50:
        return {"status": "error", "error_stage": "stage1_validation", "message": "Parsed resume failed validation"}

    contacts = extract_contact_info(text)
    known_skills = extract_known_skills(text, final_required_skills)
    parsed_resume["contacts"] = contacts
    parsed_resume["raw_resume_text"] = text

    if "hard_skills" not in parsed_resume:
        parsed_resume["hard_skills"] = []
    parsed_resume["hard_skills"].extend([s for s in known_skills if s not in parsed_resume["hard_skills"]])
    parsed_resume["hard_skills"] = normalize_skills_list(parsed_resume["hard_skills"])

    target_role = extract_target_role(jd_text)

    # 100% Deterministic Decision Engine & Scorer
    decision_output = run_decision_engine(
        parsed_resume,
        final_required_skills,
        target_role=target_role,
        raw_resume_text=text,
        jd_text=jd_text
    )

    evidence_states = decision_output.get("evidence_states", {})
    overall_score = decision_output.get("overall_score", 0)

    dim_scores = decision_output.get("dimension_scores", {})
    explicit_score = dim_scores.get("explicit_keyword_match", {}).score if hasattr(dim_scores.get("explicit_keyword_match"), "score") else 0
    semantic_score = dim_scores.get("semantic_similarity", {}).score if hasattr(dim_scores.get("semantic_similarity"), "score") else 0

    skills_evidence = _build_skills_evidence(evidence_states, text, parsed_resume)
    career_timeline = _generate_career_timeline(parsed_resume)
    business_impact = _generate_business_impact(parsed_resume)

    matched_skills = evidence_states.get("MATCHED", [])
    inferred_skills = evidence_states.get("INFERRED", [])
    equivalent_skills = evidence_states.get("EQUIVALENT", [])
    missing_skills = evidence_states.get("MISSING", [])
    explicitly_matched_skills = evidence_states.get("EXPLICITLY_MATCHED", matched_skills)
    explicitly_missing_skills = evidence_states.get("EXPLICITLY_MISSING", missing_skills)

    semantic_evidence_list = dim_scores.get("semantic_similarity", {}).evidence if hasattr(dim_scores.get("semantic_similarity"), "evidence") else []

    work_history = parsed_resume.get("work_history") or []
    current_employer = _extract_current_role_and_company(work_history)

    rec_section = decision_output.get("recommendation", {})
    rec_basis = rec_section.get("recommendation_basis", {})

    candidate_facts = {
        "current_employer": current_employer if current_employer != "Not Mentioned" else None,
        "policy_eligible": decision_output.get("policy_eligible", False)
    }

    evaluation_result = {
        "evaluation_id": candidate_id,
        "status": "success",
        "overall_score": overall_score,
        "explicit_keyword_score": explicit_score,
        "semantic_similarity_score": semantic_score,
        "dimension_scores": dim_scores,
        "matched_skills": matched_skills,
        "explicitly_matched_skills": explicitly_matched_skills,
        "explicitly_missing_skills": explicitly_missing_skills,
        "inferred_skills": inferred_skills,
        "equivalent_skills": equivalent_skills,
        "missing_skills": missing_skills,
        "required_skills": final_required_skills,
        "evidence_states": evidence_states,
        "candidate_facts": candidate_facts,
        "personal_info": parsed_resume.get("personal_info", {}),
        "contacts": contacts,
        "certification_suitability": decision_output.get("certification_suitability", {}),
        "semantic_evidence": semantic_evidence_list,
        "semantic_similarity_breakdown": decision_output.get("semantic_breakdown", {}),
        "policy_validation": {
            "policy_eligible": decision_output.get("policy_eligible", False),
            "is_eligible": decision_output.get("policy_eligible", False),
            "flags": decision_output.get("policy_flags", []),
            "critical_missing_skills": rec_basis.get("critical_missing_skills", []),
            "hiring_recommendation": rec_section.get("hiring_recommendation", "Unknown")
        },
        "decision_trace": decision_output.get("decision_trace", {}),
        "hiring_priority": decision_output.get("hiring_priority", {}),
        "evidence": {
            "skills_evidence": skills_evidence,
            "business_impact": business_impact,
            "career_timeline": career_timeline,
            "timeline_title": "Chronological Career Milestones"
        },
        "parsed_resume": parsed_resume,
        "raw_resume_text": text,
        "raw_text": text
    }

    return evaluation_result
