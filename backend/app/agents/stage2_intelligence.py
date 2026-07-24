"""
Stage 2: Recruiter Intelligence Engine.
Provides explanatory narratives, candidate highlights, interview prep, resume feedback,
and recruiter notes strictly by consuming Stage 1 evaluation results as READ-ONLY input.
STRICT RULE: Stage 2 NEVER calculates, modifies, boosts, or recalculates any numerical scores.
"""
import logging
from typing import Dict, List, Any

logger = logging.getLogger("talentscout_stage2_intelligence")

def _generate_interview_questions(parsed_resume: Dict, required_skills: List[str], evidence_states: Dict) -> Dict[str, List[str]]:
    matched = evidence_states.get("MATCHED", [])
    inferred = evidence_states.get("INFERRED", [])
    missing = evidence_states.get("MISSING", [])

    easy = []
    medium = []
    advanced = []

    if matched:
        primary = matched[0]
        easy.append(f"Can you explain your core experience using {primary} in production applications?")
        if len(matched) > 1:
            medium.append(f"How do you approach architecture and design decisions when implementing {matched[1]}?")
    else:
        easy.append("Can you walk us through your most technical software engineering project?")

    if inferred:
        inf = inferred[0]
        medium.append(f"While you have advanced experience, can you discuss your underlying foundational practice with {inf}?")

    if missing:
        crit = missing[0]
        advanced.append(f"The job requires {crit}. How would you bridge this requirement gap quickly?")

    if not easy:
        easy.append("What are your primary technical strengths and programming languages?")
    if not medium:
        medium.append("Describe a challenging technical problem you solved recently.")
    if not advanced:
        advanced.append("How do you ensure system performance, testing, and scalability in high-throughput applications?")

    return {
        "easy": easy,
        "medium": medium,
        "advanced": advanced
    }

def _generate_resume_feedback(parsed_resume: Dict) -> List[Dict[str, str]]:
    feedback = []
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

def _generate_recruiter_notes(stage1_eval: Dict[str, Any]) -> str:
    personal_info = stage1_eval.get("personal_info", {})
    name = personal_info.get("name", "Candidate") if isinstance(personal_info, dict) else "Candidate"
    
    matched = stage1_eval.get("matched_skills", [])
    inferred = stage1_eval.get("inferred_skills", [])
    missing = stage1_eval.get("missing_skills", [])
    overall = stage1_eval.get("overall_score", 0)

    parts = [f"{name} evaluated with overall match score {overall}/100."]
    if matched:
        parts.append(f"Validated core alignment on {', '.join(matched[:5])}.")
    if inferred:
        parts.append(f"Inferred foundational proficiency in {', '.join(inferred[:3])}.")
    if missing:
        parts.append(f"Potential skill gap areas: {', '.join(missing[:5])}.")
    return " ".join(parts)

def run_stage2_intelligence(stage1_eval: Dict[str, Any]) -> Dict[str, Any]:
    """
    Executes Stage 2 Recruiter Intelligence Engine.
    Takes Stage 1 evaluation outputs as READ-ONLY input.
    Returns structured recruiter intelligence explanatory object.
    """
    parsed_resume = stage1_eval.get("parsed_resume", {})
    required_skills = stage1_eval.get("required_skills", [])
    evidence_states = stage1_eval.get("evidence_states", {})
    policy_validation = stage1_eval.get("policy_validation", {})

    matched_skills = stage1_eval.get("matched_skills", [])
    inferred_skills = stage1_eval.get("inferred_skills", [])
    equivalent_skills = evidence_states.get("EQUIVALENT", [])
    missing_skills = stage1_eval.get("missing_skills", [])
    overall_score = stage1_eval.get("overall_score", 0)

    hiring_recommendation = policy_validation.get("hiring_recommendation", "Consider for Interview")

    # Generate Strengths & Weaknesses grounded in Stage 1 evidence
    strengths = []
    if matched_skills:
        strengths.append(f"Validated proficiency in core skills: {', '.join(matched_skills[:5])}")
    if inferred_skills:
        strengths.append(f"Supported foundational & concept knowledge in: {', '.join(inferred_skills[:3])}")
    if equivalent_skills:
        strengths.append(f"Demonstrates transferable equivalent technologies: {', '.join(equivalent_skills[:3])}")
    if overall_score >= 80:
        strengths.append("High overall deterministic alignment with target role parameters")

    weaknesses = []
    critical_missing = policy_validation.get("critical_missing_skills", [])
    if critical_missing:
        weaknesses.append(f"Critical missing mandatory skills: {', '.join(critical_missing)}")
    elif missing_skills:
        weaknesses.append(f"Skill gaps identified in: {', '.join(missing_skills[:5])}")

    interview_questions = _generate_interview_questions(parsed_resume, required_skills, evidence_states)
    resume_feedback = _generate_resume_feedback(parsed_resume)
    recruiter_notes = _generate_recruiter_notes(stage1_eval)

    rationale_bullets = []
    if matched_skills:
        rationale_bullets.append(f"Candidate explicitly demonstrates {len(matched_skills)} core required skills.")
    if inferred_skills:
        rationale_bullets.append(f"Seniority & prerequisite ontology strongly support {len(inferred_skills)} inferred skills ({', '.join(inferred_skills[:3])}).")
    if equivalent_skills:
        rationale_bullets.append(f"Transferable equivalent technologies matched for {len(equivalent_skills)} requirements ({', '.join(equivalent_skills[:3])}).")
    policy_overrides = policy_validation.get("policy_overrides", [])
    for ov in policy_overrides:
        rationale_bullets.append(ov)
    if missing_skills:
        rationale_bullets.append(f"Candidate requires onboarding focus in {len(missing_skills)} gap areas.")

    confidence_level = stage1_eval.get("confidence", "High")
    confidence_reasoning = stage1_eval.get("confidence_reasoning", "Strong deterministic evidence coverage and high semantic alignment.")
    job_criticality = stage1_eval.get("job_criticality", "Professional")

    recruiter_intelligence = {
        "recommendation": {
            "hiring_recommendation": hiring_recommendation,
            "confidence": confidence_level,
            "confidence_reasoning": confidence_reasoning,
            "job_criticality": job_criticality,
            "rationale_bullets": rationale_bullets if rationale_bullets else ["Automated policy assessment completed."],
            "candidate_summary": strengths,
            "candidate_highlights": strengths[:3],
            "disclaimer": "This assessment is generated strictly from deterministic Stage 1 evidence."
        },
        "recommendation_basis": {
            "strengths": strengths,
            "weaknesses": weaknesses,
            "critical_missing_skills": critical_missing,
            "domain_alignment": "Strong Alignment" if overall_score >= 75 else "Moderate Alignment",
            "decision_reasoning": recruiter_notes
        },
        "interview": {
            "verify_during_interview": missing_skills[:3],
            "interview_questions": interview_questions
        },
        "onboarding": {
            "estimated_ramp_up": "1-2 weeks" if overall_score >= 85 else "2-4 weeks",
            "rationale_factors": weaknesses,
            "learning_curve": [{"skill": s, "difficulty": "Moderate", "reason": "Requires onboarding"} for s in missing_skills[:3]]
        },
        "recruiter": {
            "confidence": {
                "level": confidence_level,
                "confidence_reasoning": confidence_reasoning,
                "skill_extraction": "High",
                "reasoning": "High",
                "learnability": "Medium",
                "evidence_justification": "Deterministic Stage 1 Evidence Grounding"
            },
            "resume_feedback": resume_feedback,
            "recruiter_notes": recruiter_notes
        }
    }

    return recruiter_intelligence
