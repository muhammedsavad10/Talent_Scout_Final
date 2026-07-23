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

def _build_skills_evidence(evidence_states: Dict[str, List[str]], raw_text: str, parsed_resume: Dict) -> List[Dict[str, Any]]:
    items = []
    for status_key, skill_list in evidence_states.items():
        is_identified = status_key in ("MATCHED", "INFERRED")
        status_label = "Identified" if is_identified else "Not identified"
        strength = "High" if is_identified else "Low"
        for skill_name in skill_list:
            snippet = _extract_sentence_for_skill(raw_text, skill_name)
            project_name = None
            for proj in parsed_resume.get("projects", []):
                if isinstance(proj, dict):
                    desc = (proj.get("description") or "") + (proj.get("title") or "")
                    if skill_name.lower() in desc.lower():
                        project_name = proj.get("title")
                        if not snippet:
                            snippet = desc[:200]
                        break
            if not snippet:
                for work in parsed_resume.get("work_history", []):
                    if isinstance(work, dict):
                        desc = work.get("description") or ""
                        if skill_name.lower() in desc.lower():
                            snippet = desc[:200]
                            break
            items.append({
                "skill": skill_name,
                "status": status_label,
                "evidence_snippet": snippet,
                "project_name": project_name,
                "role_held": None,
                "evidence_strength": strength,
                "match_confidence": 100 if is_identified else 0,
                "reasoning": f"Skill found in resume {'and matches job requirement' if is_identified else 'but not found in resume text'}"
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


async def run_evaluation_pipeline(text: str, candidate_id: str, required_skills: List[str] = None) -> Dict[str, Any]:
    if required_skills is None:
        required_skills = []

    try:
        parsed_resume = parse_resume_to_json(text)
        if not parsed_resume:
            return {"status": "error", "error_stage": "parser", "message": "Failed to parse resume"}

        if "error" in parsed_resume:
            return {"status": "error", "error_stage": "parser", "message": parsed_resume["error"]}

        if "skills" in parsed_resume:
            for cat, skills_list in parsed_resume["skills"].items():
                if isinstance(skills_list, list):
                    parsed_resume["skills"][cat] = normalize_skills_list(skills_list)

        if "hard_skills" in parsed_resume:
            parsed_resume["hard_skills"] = normalize_skills_list(parsed_resume["hard_skills"])

        validation_report = validate_parsed_resume(parsed_resume)
        if validation_report["overall_score"] < 50:
            return {"status": "error", "error_stage": "validation", "message": "Parsed resume failed validation"}

        contacts = extract_contact_info(text)
        known_skills = extract_known_skills(text, required_skills)
        parsed_resume["contacts"] = contacts

        if "hard_skills" not in parsed_resume:
            parsed_resume["hard_skills"] = []
        parsed_resume["hard_skills"].extend([s for s in known_skills if s not in parsed_resume["hard_skills"]])
        parsed_resume["hard_skills"] = normalize_skills_list(parsed_resume["hard_skills"])

        decision_output = run_decision_engine(parsed_resume, required_skills)

        rec_section = decision_output.get("recommendation", {})
        rec_basis = rec_section.get("recommendation_basis", {})
        evidence_states = decision_output.get("evidence_states", {})
        overall = decision_output.get("overall_score", 0)

        skills_evidence = _build_skills_evidence(evidence_states, text, parsed_resume)
        career_timeline = _generate_career_timeline(parsed_resume)
        business_impact = _generate_business_impact(parsed_resume)
        interview_questions = _generate_interview_questions(parsed_resume, required_skills, evidence_states)
        resume_feedback = _generate_resume_feedback(parsed_resume)
        recruiter_notes = _generate_recruiter_notes(parsed_resume, decision_output)

        reasoning_text = rec_basis.get("reasoning", "")
        strengths = rec_basis.get("strengths", [])
        weaknesses = rec_basis.get("weaknesses", [])

        matched_skills = evidence_states.get("MATCHED", [])
        missing_skills = evidence_states.get("MISSING", [])

        # Calculate candidate facts deterministically
        work_history = parsed_resume.get("work_history") or []
        experience_years = _calculate_years_experience(work_history)
        salary = _extract_salary_information(text)
        notice_period = _extract_notice_period(text)
        location = _extract_location(text)
        current_employer = _extract_current_role_and_company(work_history)

        candidate_facts = {
            "current_employer": current_employer if current_employer != "Not Mentioned" else None,
            "policy_eligible": decision_output.get("policy_eligible", False)
        }

        result = {
            "evaluation_id": candidate_id,
            "status": "success",
            "candidate_facts": candidate_facts,
            "personal_info": parsed_resume.get("personal_info", {}),
            "contacts": contacts,
            "matched_skills": matched_skills,
            "missing_skills": missing_skills,
            "overall_score": overall,
            "decision_engine": decision_output,
            "recommendation": {
                "hiring_recommendation": rec_section.get("hiring_recommendation", "Unknown"),
                "rationale_bullets": reasoning_text.split("\n") if reasoning_text else [],
                "candidate_summary": strengths,
                "candidate_highlights": strengths[:3],
                "disclaimer": "This assessment is based only on information present in the submitted resume."
            },
            "recommendation_basis": {
                "strengths": strengths,
                "weaknesses": weaknesses,
                "critical_missing_skills": rec_basis.get("critical_missing_skills", []),
                "domain_alignment": rec_basis.get("domain_alignment", "Unknown"),
                "decision_reasoning": reasoning_text,
                "reasoning": reasoning_text
            },
            "evidence": {
                "skills_evidence": skills_evidence,
                "business_impact": business_impact,
                "career_timeline": career_timeline,
                "timeline_title": "Chronological Career Milestones"
            },
            "onboarding": {
                "estimated_ramp_up": "2-4 weeks",
                "rationale_factors": [],
                "learning_curve": []
            },
            "interview": {
                "verify_during_interview": [],
                "interview_questions": interview_questions
            },
            "recruiter": {
                "confidence": {
                    "skill_extraction": "High",
                    "reasoning": "Medium",
                    "learnability": "Medium",
                    "evidence_justification": "Automated evaluation"
                },
                "resume_feedback": resume_feedback,
                "recruiter_notes": recruiter_notes
            },
            "debug": {
                "raw_weighted_score": overall / 100.0,
                "raw_semantic_similarity": 0.0,
                "raw_containment_score": 0.0,
                "matched_tokens": evidence_states.get("MATCHED", []) + evidence_states.get("INFERRED", []),
                "processing_ms": 0.0,
                "agent_logs": [],
                "pipeline_node_transitions": [
                    "Parser", "Normalization", "Validation",
                    "Scorer", "PolicyEngine", "Strategy",
                    "EvidenceBuilder", "TimelineGenerator",
                    "InterviewGenerator", "FeedbackGenerator"
                ]
            }
        }
        return result

    except Exception as e:
        logger.exception("Pipeline failed unexpectedly")
        return {"status": "error", "error_stage": "orchestrator", "message": str(e)}
