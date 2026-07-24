import logging
import json
import re
import time
from typing import Dict, Any, List
from app.agents.normalization import normalize_skills_list
from app.agents.parser_validation import validate_parsed_resume
from app.agents.deterministic_extractor import extract_contact_info, extract_known_skills
from app.agents.decision_engine import run_decision_engine
from app.agents.ingestion import parse_resume_to_json
from app.core.config import call_llm

logger = logging.getLogger(__name__)


def _extract_sentence_for_skill(text: str, skill: str) -> str:
    if not text:
        return None
    sentences = re.split(r'(?<=[.!?])\s+', text)
    for sent in sentences:
        if re.search(r'\b' + re.escape(skill) + r'\b', sent, re.IGNORECASE):
            return sent.strip()[:200]
    return None


def _calculate_years_experience(work_history: list) -> str:
    if not work_history:
        return "Not Mentioned"
    
    year_pattern = re.compile(r'\b(19\d{2}|20\d{2})\b')
    total_years = 0.0
    current_year = 2026
    has_valid_dates = False
    
    for work in work_history:
        if not isinstance(work, dict):
            continue
        dates_str = work.get("dates") or ""
        if not dates_str:
            continue
        years = [int(y) for y in year_pattern.findall(dates_str)]
        is_current = any(w in dates_str.lower() for w in ["present", "current", "now", "ongoing"])
        
        if len(years) >= 2:
            start_year, end_year = years[0], years[1]
            total_years += max(0.0, end_year - start_year)
            has_valid_dates = True
        elif len(years) == 1:
            start_year = years[0]
            end_year = current_year if is_current else start_year
            total_years += max(0.5, end_year - start_year)
            has_valid_dates = True
        elif is_current:
            total_years += 1.0
            has_valid_dates = True
            
    if has_valid_dates:
        years_val = max(1.0, round(total_years, 1))
        if years_val.is_integer():
            return f"{int(years_val)} Years"
        return f"{years_val} Years"
    
    return "Not Mentioned"

def _extract_salary_information(raw_text: str) -> str:
    if not raw_text:
        return "Not Mentioned"
    salary_patterns = [
        r'(?:CTC|salary|package|compensation|remuneration)\b[^\n.]{0,50}(?:\d[\d,.]*\s*(?:lakh|lpa|k|l|million|\$|inr|rs|usd))',
        r'(?:\$|rs\.?|inr)\s*\d[\d,.]*\s*(?:lpa|lakh|k|pm|per\s*month)?'
    ]
    for pattern in salary_patterns:
        match = re.search(pattern, raw_text, re.IGNORECASE)
        if match:
            return match.group(0).strip()
    return "Not Mentioned"

def _extract_notice_period(raw_text: str) -> str:
    if not raw_text:
        return "Not Mentioned"
    notice_pattern = r'(?:\bnotice\s*period\b|\bserving\s*notice\b|\bnotice\b)[^\n.]{0,30}(?:\d+\s*(?:day|month|week|lpa)|immediate|active)'
    match = re.search(notice_pattern, raw_text, re.IGNORECASE)
    if match:
        return match.group(0).strip()
    return "Not Mentioned"

def _extract_location(raw_text: str) -> str:
    if not raw_text:
        return "Not Mentioned"
    common_locations = ["Bangalore", "Bengaluru", "Mumbai", "Pune", "Hyderabad", "Chennai", "Delhi", "Noida", "Gurgaon", "Gurugram", "San Francisco", "London", "New York", "Remote", "India", "USA", "UK"]
    for loc in common_locations:
        if re.search(r'\b' + re.escape(loc) + r'\b', raw_text, re.IGNORECASE):
            return loc
    return "Not Mentioned"

def _extract_current_role_and_company(work_history: list) -> str:
    if not work_history:
        return "Not Mentioned"
    first_job = work_history[0]
    if isinstance(first_job, dict):
        role = first_job.get("role") or ""
        company = first_job.get("company") or ""
        dates = first_job.get("dates") or ""
        is_current = any(w in dates.lower() for w in ["present", "current", "now", "ongoing"])
        if role and company:
            suffix = " (Current)" if is_current else ""
            return f"{role} at {company}{suffix}"
        elif role:
            return role
        elif company:
            return company
    return "Not Mentioned"

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

            # If inferred, look for snippet of triggering technology
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


def _generate_career_timeline(parsed_resume: Dict) -> List[Dict[str, str]]:
    timeline = []
    work_history = parsed_resume.get("work_history", [])
    for work in work_history:
        if isinstance(work, dict):
            role = work.get("role") or "Unknown Role"
            company = work.get("company") or "Unknown Company"
            dates = work.get("dates") or ""
            details = work.get("description") or ""
            timeline.append({
                "year": dates,
                "role": role,
                "company": company,
                "details": details[:150] if details else ""
            })
    projects = parsed_resume.get("projects", [])
    for proj in projects:
        if isinstance(proj, dict):
            title = proj.get("title") or "Project"
            role = proj.get("role") or ""
            dates = proj.get("dates") or ""
            desc = proj.get("description") or ""
            timeline.append({
                "year": dates,
                "role": f"{role} - {title}" if role else title,
                "company": "Personal/Academic Project",
                "details": desc[:150] if desc else ""
            })
    return timeline


def _generate_business_impact(parsed_resume: Dict) -> List[Dict[str, str]]:
    impact_items = []
    impact_keywords = {
        "Performance": ["performance", "latency", "throughput", "optimized", "faster", "speed", "scalability", "response time"],
        "Cost": ["cost", "saved", "reduced", "budget", "spend", "efficiency", "optimization"],
        "Automation": ["automated", "automation", "ci/cd", "pipeline", "deployment", "self-service"],
        "Revenue": ["revenue", "sales", "growth", "profit", "monetization", "conversion"],
        "Quality": ["quality", "defect", "bug", "reliability", "uptime", "availability", "accuracy"],
        "Team": ["team", "mentor", "lead", "managed", "hired", "scaled"],
    }

    work_history = parsed_resume.get("work_history", [])
    for work in work_history:
        if isinstance(work, dict):
            desc = (work.get("description") or "").lower()
            role = work.get("role") or "Role"
            for category, keywords in impact_keywords.items():
                matched = [kw for kw in keywords if kw in desc]
                if matched:
                    impact_items.append({
                        "category": category,
                        "description": f"In {role}: {work.get('description', '')[:200]}"
                    })
                    break

    for proj in parsed_resume.get("projects", []):
        if isinstance(proj, dict):
            desc = (proj.get("description") or "").lower()
            title = proj.get("title") or "Project"
            for category, keywords in impact_keywords.items():
                matched = [kw for kw in keywords if kw in desc]
                if matched:
                    impact_items.append({
                        "category": category,
                        "description": f"In project '{title}': {proj.get('description', '')[:200]}"
                    })
                    break

    return impact_items


def _generate_interview_questions(parsed_resume: Dict, required_skills: List[str], evidence_states: Dict) -> Dict[str, List[str]]:
    questions = {"easy": [], "medium": [], "advanced": []}
    matched = evidence_states.get("MATCHED", [])
    missing = evidence_states.get("MISSING", [])

    try:
        work_summary = ""
        for w in parsed_resume.get("work_history", []):
            if isinstance(w, dict):
                work_summary += f"- {w.get('role', '')} at {w.get('company', '')}: {w.get('description', '')[:200]}\n"

        prompt = f"""Generate interview questions for a candidate based on their resume and job requirements.

Resume Work History:
{work_summary[:2000]}

Skills found in resume: {', '.join(matched) if matched else 'None'}
Missing skills to probe: {', '.join(missing) if missing else 'None'}
Job required skills: {', '.join(required_skills) if required_skills else 'None'}

Return ONLY valid JSON in this exact structure:
{{
  "easy": ["Question about matched skills", "Question about general experience"],
  "medium": ["Scenario question combining skills", "Problem-solving with matched tech"],
  "advanced": ["Deep technical question on missing skills", "Architecture/design question"]
}}

Rules:
- 2-3 questions per difficulty level
- Easy: fact-based on skills they have
- Medium: scenario-based connecting their experience to job needs
- Advanced: probing missing skills and deep expertise
- Questions must be specific to the actual resume and job, not generic."""

        result = call_llm(
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            response_format={"type": "json_object"},
            max_tokens=1000,
            stage="interview_questions",
        )

        try:
            parsed = json.loads(result)
            for level in ["easy", "medium", "advanced"]:
                if parsed.get(level) and isinstance(parsed[level], list):
                    questions[level] = parsed[level][:5]
        except (json.JSONDecodeError, KeyError):
            logger.warning("Failed to parse LLM interview questions, using fallback")
            questions = _fallback_interview_questions(matched, missing)

    except Exception as e:
        logger.warning(f"LLM interview generation failed: {e}, using fallback")
        questions = _fallback_interview_questions(matched, missing)

    if not any(questions.values()):
        questions = _fallback_interview_questions(matched, missing)

    return questions


def _fallback_interview_questions(matched: List[str], missing: List[str]) -> Dict[str, List[str]]:
    questions = {"easy": [], "medium": [], "advanced": []}
    if matched:
        for s in matched[:3]:
            questions["easy"].append(f"Describe your experience with {s}.")
            questions["medium"].append(f"Walk me through a project where you used {s} to solve a complex problem.")
    else:
        questions["easy"].append("Describe your overall technical background and experience.")
    if missing:
        for s in missing[:3]:
            questions["advanced"].append(f"How would you approach learning and implementing {s} in a production environment?")
    if not questions["easy"]:
        questions["easy"].append("Tell me about your most recent role and responsibilities.")
    if not questions["medium"]:
        questions["medium"].append("Describe a challenging technical problem you solved recently.")
    if not questions["advanced"]:
        questions["advanced"].append("How do you stay current with emerging technologies in your field?")
    return questions


def _generate_resume_feedback(parsed_resume: Dict) -> List[Dict[str, str]]:
    feedback = []
    contacts = parsed_resume.get("contacts", {}) or parsed_resume.get("personal_info", {})
    if not contacts.get("email"):
        feedback.append({"label": "Add email contact information", "status": "warning"})
    if not contacts.get("phone"):
        feedback.append({"label": "Add phone number for recruiter reachability", "status": "warning"})
    if not parsed_resume.get("work_history"):
        feedback.append({"label": "Include detailed work history with role, company, and dates", "status": "warning"})
    if not parsed_resume.get("education"):
        feedback.append({"label": "Include education details", "status": "warning"})
    work_history = parsed_resume.get("work_history", [])
    has_short_descriptions = any(
        isinstance(w, dict) and len(w.get("description", "") or "") < 50
        for w in work_history
    )
    if has_short_descriptions:
        feedback.append({"label": "Expand work experience descriptions with specific technologies and outcomes", "status": "warning"})
    if parsed_resume.get("projects"):
        feedback.append({"label": "Projects section present - good for demonstrating practical experience", "status": "pass"})
    if parsed_resume.get("hard_skills") or parsed_resume.get("skills"):
        feedback.append({"label": "Technical skills are well-documented", "status": "pass"})
    else:
        feedback.append({"label": "Add a dedicated technical skills section", "status": "warning"})
    if not feedback:
        feedback.append({"label": "Resume is well-structured and complete", "status": "pass"})
    return feedback


def _generate_recruiter_notes(parsed_resume: Dict, decision_output: Dict) -> str:
    name = "Candidate"
    personal_info = parsed_resume.get("personal_info", {})
    if isinstance(personal_info, dict) and personal_info.get("name"):
        name = personal_info["name"]

    evidence_states = decision_output.get("evidence_states", {})
    matched = evidence_states.get("MATCHED", [])
    missing = evidence_states.get("MISSING", [])
    overall = decision_output.get("overall_score", 0)

    parts = [f"{name} evaluated with overall score {overall}/100."]
    if matched:
        parts.append(f"Strong alignment on {', '.join(matched[:5])}.")
    if missing:
        parts.append(f"Gap areas: {', '.join(missing[:5])}.")
    return " ".join(parts)


def prepare_final_required_skills(jd_text: str, optional_recruiter_skills: List[str] = None) -> List[str]:
    """
    Primary Source: Automatically extracts skills from Job Description (jd_text).
    Optional Source: Merges optional recruiter-entered skills (optional_recruiter_skills).
    Deduplicates after normalization.
    """
    if optional_recruiter_skills is None:
        optional_recruiter_skills = []

    from app.agents.deterministic_extractor import extract_skills_from_jd
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


from app.agents.stage1_evaluation import run_stage1_evaluation, prepare_final_required_skills
from app.agents.stage2_intelligence import run_stage2_intelligence


async def run_evaluation_pipeline(
    text: str,
    candidate_id: str,
    required_skills: List[str] = None,
    jd_text: str = ""
) -> Dict[str, Any]:
    if required_skills is None:
        required_skills = []

    try:
        # Stage 1: Deterministic Evaluation Engine (Owns 100% of score calculations)
        evaluation_data = await run_stage1_evaluation(
            text=text,
            candidate_id=candidate_id,
            required_skills=required_skills,
            jd_text=jd_text
        )

        if evaluation_data.get("status") == "error":
            return evaluation_data

        # Stage 2: Recruiter Intelligence Engine (Explanatory layer, consumes Stage 1 as read-only)
        intelligence_data = run_stage2_intelligence(evaluation_data)

        # Build response with strict Stage 1 ("evaluation") and Stage 2 ("recruiter_intelligence") separation
        result = {
            "evaluation": evaluation_data,
            "recruiter_intelligence": intelligence_data,
            
            # Root-level property aliases for complete backward compatibility
            "evaluation_id": evaluation_data.get("evaluation_id"),
            "status": evaluation_data.get("status"),
            "candidate_facts": evaluation_data.get("candidate_facts"),
            "personal_info": evaluation_data.get("personal_info"),
            "contacts": evaluation_data.get("contacts"),
            "matched_skills": evaluation_data.get("matched_skills"),
            "inferred_skills": evaluation_data.get("inferred_skills"),
            "missing_skills": evaluation_data.get("missing_skills"),
            "overall_score": evaluation_data.get("overall_score"),
            "decision_engine": {
                "overall_score": evaluation_data.get("overall_score"),
                "policy_eligible": evaluation_data.get("policy_validation", {}).get("policy_eligible", True),
                "evidence_states": evaluation_data.get("evidence_states", {}),
                "dimension_scores": evaluation_data.get("dimension_scores", {}),
                "recommendation": intelligence_data.get("recommendation", {})
            },
            "certification_suitability": evaluation_data.get("certification_suitability"),
            "evidence": evaluation_data.get("evidence"),
            "recommendation": intelligence_data.get("recommendation"),
            "recommendation_basis": intelligence_data.get("recommendation_basis"),
            "onboarding": intelligence_data.get("onboarding"),
            "interview": intelligence_data.get("interview"),
            "recruiter": intelligence_data.get("recruiter")
        }

        return result

    except Exception as e:
        logger.exception("Pipeline failed unexpectedly")
        return {"status": "error", "error_stage": "orchestrator", "message": str(e)}
