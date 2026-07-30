"""
API Router for the LangGraph Multi-Agent Evaluation Engine and Grounded Recruiter Assistant.
"""
import logging
import json
import unicodedata
import traceback
import re
import uuid
from typing import Optional, List, Dict, Any

from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from app.agents.orchestrator import run_evaluation_pipeline
from app.services.evaluation_store import evaluation_store
from app.core.config import call_llm
from app.agents.ingestion import extract_text_from_pdf

logger = logging.getLogger("talentscout_api_evaluate")
router = APIRouter()

@router.post("/evaluate")
async def evaluate_candidate(
    file: UploadFile = File(...),
    jd_text: str = Form(...),
    jd_skills: Optional[str] = Form(default="")  # Optional comma-separated string (e.g., "Python, FastAPI")
):
    """
    Ingests a PDF resume and job parameters, executes the LangGraph multi-agent swarm,
    and returns a mathematically transparent evaluation and feedback report.
    """
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")
    
    try:
        # Read the upload stream into raw bytes for the ingestion node
        pdf_bytes = await file.read()
        
        # Security Hardening (Phase C): File size check (Max 5MB)
        if len(pdf_bytes) > 5 * 1024 * 1024:
            raise HTTPException(status_code=413, detail="File size exceeds the 5MB limit.")
            
        # Security Hardening (Phase C): Magic Bytes validation for genuine PDF
        if not pdf_bytes.startswith(b"%PDF"):
            raise HTTPException(status_code=415, detail="Invalid file type. File is not a genuine PDF.")
        
        # Extract text from the PDF for the pipeline
        try:
            text = extract_text_from_pdf(pdf_bytes)
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"PDF extraction failed: {str(e)}")
        
        # Pre-parsing Resume Document Validation Gate
        from app.core.resume_validator import validate_is_resume
        is_resume, conf_score, val_msg = validate_is_resume(text)
        if not is_resume:
            logger.warning(f"Resume validation gate rejected {file.filename} (Score: {conf_score:.1f}): {val_msg}")
            raise HTTPException(status_code=400, detail=val_msg)
        
        # Parse the comma-separated target skills into a clean list
        skills_list = [skill.strip() for skill in jd_skills.split(",") if skill.strip()]
        
        logger.info(f"Web request received: Initiating LangGraph pipeline for {file.filename}")
        
        candidate_id = f"eval_{uuid.uuid4().hex[:8]}"
        
        # Execute the unified state machine
        final_state = await run_evaluation_pipeline(
            text=text,
            candidate_id=candidate_id,
            required_skills=skills_list,
            jd_text=jd_text
        )
        
        # Gracefully handle internal state machine tracking drops
        if final_state.get("status") == "error":
            logger.error(f"LangGraph execution error drop: {final_state.get('message')}")
            raise HTTPException(status_code=500, detail=final_state.get("message"))
        
        # Save to store and return the standardized payload contract matching status & batch endpoints
        final_state["filename"] = file.filename
        final_state["evaluation_id"] = candidate_id
        final_state["candidate_id"] = candidate_id
        
        full_eval = {
            "evaluation_id": candidate_id,
            "filename": file.filename,
            "status": "COMPLETED",
            "result": final_state
        }
        from app.core.consistency_validator import validate_final_api_response
        full_eval = validate_final_api_response(full_eval)
        await evaluation_store.save_evaluation(candidate_id, full_eval)
        
        return full_eval
        
    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"Unhandled evaluation gateway failure: {e}")
        raise HTTPException(status_code=500, detail="Internal server error during pipeline evaluation.")

@router.get("/status/{evaluation_id}")
async def get_evaluation_status(evaluation_id: str):
    """
    Retrieves the full evaluation status and results for a specific candidate.
    """
    eval_data = await evaluation_store.get_evaluation(evaluation_id)
    if not eval_data:
        raise HTTPException(status_code=404, detail="Evaluation not found.")
    from app.core.consistency_validator import validate_final_api_response
    return validate_final_api_response(eval_data)

@router.post("/email/generate")
async def generate_email(payload: dict):
    evaluation_id = payload.get("evaluation_id") or payload.get("id", "")
    template_type = payload.get("template_type") or payload.get("template", "interview_invitation")
    
    cand_name = "Candidate"
    cand_role = "Senior Engineer"
    cand_company = "Tech"
    cand_skills = "Python, FastAPI"
    
    if evaluation_id:
        eval_data = await evaluation_store.get_evaluation(evaluation_id)
        if eval_data and isinstance(eval_data, dict):
            res = eval_data.get("result", eval_data)
            info = res.get("personal_info", {}) if isinstance(res, dict) else {}
            if isinstance(info, dict) and info.get("name"):
                cand_name = info["name"]
            work = res.get("work_history", []) if isinstance(res, dict) else []
            if work and isinstance(work, list) and isinstance(work[0], dict):
                cand_company = work[0].get("company", cand_company)
                cand_role = work[0].get("role", cand_role)
            skills = res.get("hard_skills") or res.get("skills") or []
            if skills and isinstance(skills, list):
                cand_skills = ", ".join([str(s) for s in skills[:4]])

    templates = {
        "interview_invitation": {
            "subject": f"TalentScout Enterprise — Technical Interview Invitation for {cand_name}",
            "body": f"Dear {cand_name},\n\nThank you for applying for the {cand_role} position. Based on your impressive background in {cand_skills} and your achievements at {cand_company}, we would like to invite you for a technical interview.\n\nPlease let us know your availability over the next few business days so we can schedule the discussion.\n\nBest regards,\nTalentScout Recruitment Team"
        },
        "technical_assessment": {
            "subject": f"Technical Assessment Invitation: {cand_role} Position — {cand_name}",
            "body": f"Dear {cand_name},\n\nFollowing our review of your background in {cand_skills}, we are excited to advance your application for the {cand_role} position.\n\nThe next step is a practical technical assessment designed to demonstrate your hands-on engineering capabilities. The assignment will take approximately 60-90 minutes.\n\nPlease reply to confirm when you are ready to begin the assessment window.\n\nBest regards,\nTalentScout Engineering Team"
        },
        "hr_screening": {
            "subject": f"Initial HR Screening Call — TalentScout Enterprise ({cand_name})",
            "body": f"Dear {cand_name},\n\nYour profile for the {cand_role} position stood out to our hiring team, particularly your expertise in {cand_skills}.\n\nWe would love to schedule a brief 15-20 minute initial screening call to discuss your career background at {cand_company}, your compensation expectations, and upcoming opportunities.\n\nPlease share 2-3 time slots that work best for you this week.\n\nWarm regards,\nTalentScout Talent Acquisition"
        },
        "shortlisted_candidate": {
            "subject": f"Update on Your Application: Shortlisted for {cand_role}",
            "body": f"Dear {cand_name},\n\nWe are pleased to inform you that your profile has been officially shortlisted for the {cand_role} position.\n\nOur leadership team was highly impressed by your production experience with {cand_skills}. We are currently finalizing the panel interview schedule and will reach out with calendar invites shortly.\n\nThank you for your continued interest in TalentScout Enterprise.\n\nBest regards,\nTalentScout Executive Search"
        },
        "offer_letter": {
            "subject": f"Formal Employment Offer — {cand_role} at TalentScout Enterprise",
            "body": f"Dear {cand_name},\n\nOn behalf of TalentScout Enterprise, we are thrilled to offer you the position of {cand_role}.\n\nWe were immensely impressed by your technical precision in {cand_skills} and the leadership demonstrated throughout your career. We believe your contributions will be pivotal to our engineering division.\n\nAttached is the formal offer letter outlining compensation and start dates. Please review and return a signed copy by the indicated deadline.\n\nWelcome to the team!\n\nBest regards,\nTalentScout People Operations"
        },
        "hold_future": {
            "subject": f"TalentScout Enterprise — Application Status Update ({cand_role})",
            "body": f"Dear {cand_name},\n\nThank you for giving us the opportunity to consider your background for the {cand_role} position.\n\nWhile we have decided to move forward with another candidate whose immediate domain focus matched our present sprint, your strong profile in {cand_skills} left a lasting impression on our team.\n\nWith your permission, we will keep your profile active in our Talent Vault and reach out immediately when matching roles open.\n\nSincerely,\nTalentScout Talent Acquisition"
        },
        "rejection_email": {
            "subject": f"Application Status for {cand_role} — TalentScout Enterprise",
            "body": f"Dear {cand_name},\n\nThank you for taking the time to apply for the {cand_role} role and sharing your experience at {cand_company}.\n\nAfter careful consideration of all applicants, we have chosen to proceed with candidates whose current project scope aligns more closely with our active requirements.\n\nWe appreciate your interest in TalentScout Enterprise and wish you continued success in your professional endeavors.\n\nSincerely,\nTalentScout Recruitment Team"
        },
        "follow_up_reminder": {
            "subject": f"Follow-up Regarding Your {cand_role} Application — TalentScout Enterprise",
            "body": f"Dear {cand_name},\n\nI hope this email finds you well.\n\nI am following up on our previous communication regarding the {cand_role} position. We remain very interested in your experience with {cand_skills} and would love to hear your thoughts on proceeding with the next steps.\n\nPlease let us know if you are still available for a brief conversation.\n\nBest regards,\nTalentScout Recruitment Team"
        }
    }
    
    selected = templates.get(template_type, templates["interview_invitation"])
    return selected

def normalize_skill(skill: str) -> str:
    if not isinstance(skill, str):
        return ""
    return unicodedata.normalize("NFKC", skill).casefold().strip()

def calculate_years_experience(work_history: list) -> str:
    if not isinstance(work_history, list) or not work_history:
        return "Experience duration cannot be determined from the available information."
    
    year_pattern = re.compile(r'\b(19\d{2}|20\d{2})\b')
    total_years = 0.0
    current_year = 2026
    has_valid_dates = False
    
    for work in work_history:
        if not isinstance(work, dict):
            continue
        dates_val = work.get("dates")
        dates_str = str(dates_val) if dates_val is not None else ""
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
        return f"{years_val} Years"
    
    return "Experience duration cannot be determined from the available information."

def extract_salary_information(raw_text: str) -> str:
    raw_text_str = str(raw_text) if raw_text is not None else ""
    if not raw_text_str:
        return "Salary information is not available in the resume."
    salary_patterns = [
        r'(?:CTC|salary|package|compensation|remuneration)\b[^\n.]{0,50}(?:\d[\d,.]*\s*(?:lakh|lpa|k|l|million|\$|inr|rs|usd))',
        r'(?:\$|rs\.?|inr)\s*\d[\d,.]*\s*(?:lakh|lpa|k|pm|per\s*month)?'
    ]
    for pattern in salary_patterns:
        match = re.search(pattern, raw_text_str, re.IGNORECASE)
        if match:
            return match.group(0).strip()
    return "Salary information is not available in the resume."

def extract_notice_period(raw_text: str) -> str:
    raw_text_str = str(raw_text) if raw_text is not None else ""
    if not raw_text_str:
        return "Notice period is not specified."
    notice_patterns = [
        r'\b\d+\s*(?:days?|months?|weeks?)\s+(?:notice\s*period|notice|serving\s*notice)\b',
        r'\b(?:notice\s*period|serving\s*notice|notice)\b[^\n.]{0,30}(?:\d+\s*(?:days?|months?|weeks?|lpa)|immediate|active)'
    ]
    for pattern in notice_patterns:
        match = re.search(pattern, raw_text_str, re.IGNORECASE)
        if match:
            return match.group(0).strip()
    return "Notice period is not specified."

def extract_current_role_and_company(work_history: list) -> str:
    if not isinstance(work_history, list) or not work_history:
        return "Current role and company are not specified in the resume."
    first_job = work_history[0]
    if isinstance(first_job, dict):
        role = str(first_job.get("role") or "").strip()
        company = str(first_job.get("company") or "").strip()
        dates = str(first_job.get("dates") or "").strip()
        is_current = any(w in dates.lower() for w in ["present", "current", "now", "ongoing"])
        if role and company:
            suffix = " (Current)" if is_current else ""
            return f"{role} at {company}{suffix}"
        elif role:
            return role
        elif company:
            return company
    return "Current role and company are not specified in the resume."

def extract_education(education_list: list) -> str:
    if isinstance(education_list, list) and education_list:
        clean_items = [str(e).strip() for e in education_list if e]
        if clean_items:
            return ", ".join(clean_items)
    elif isinstance(education_list, str) and education_list.strip():
        return education_list.strip()
    return "No education details are explicitly listed in the resume."

def extract_certifications(certifications_list: list, flat_cert_names: list) -> str:
    certs = []
    if isinstance(certifications_list, list) and certifications_list:
        for cert in certifications_list:
            if isinstance(cert, dict):
                title = str(cert.get("title") or "").strip()
                issuer = str(cert.get("issuer") or "").strip()
                if title:
                    certs.append(f"{title} from {issuer}" if issuer else title)
            elif isinstance(cert, str) and cert.strip():
                certs.append(cert.strip())
    
    if not certs and isinstance(flat_cert_names, list) and flat_cert_names:
        certs = [str(c).strip() for c in flat_cert_names if c]
        
    if certs:
        return ", ".join(certs)
    return "No certifications are explicitly listed in the resume."

def extract_candidate_deterministic_metadata(eval_data: dict) -> dict:
    if not isinstance(eval_data, dict):
        eval_data = {}
    result = eval_data.get("result", {}) if isinstance(eval_data.get("result"), dict) else {}
    personal_info = result.get("personal_info", {}) if isinstance(result.get("personal_info"), dict) else {}
    evidence = result.get("evidence", {}) if isinstance(result.get("evidence"), dict) else {}
    
    # Extract work history safely
    work_history = result.get("work_history")
    if not isinstance(work_history, list) or not work_history:
        parsed_resume = result.get("parsed_resume", {}) if isinstance(result.get("parsed_resume"), dict) else {}
        work_history = parsed_resume.get("work_history")
    if not isinstance(work_history, list) or not work_history:
        timeline = evidence.get("career_timeline", [])
        if isinstance(timeline, list) and timeline:
            work_history = [
                {"role": t.get("role"), "company": t.get("company"), "dates": t.get("year")}
                for t in timeline if isinstance(t, dict)
            ]
    if not isinstance(work_history, list):
        work_history = []
            
    # Years of experience calculation
    exp_duration = calculate_years_experience(work_history)
    
    # Raw text for regex searches
    raw_text = result.get("raw_resume_text") or ""
    if not isinstance(raw_text, str):
        raw_text = str(raw_text)
    
    salary_info = extract_salary_information(raw_text)
    notice_period = extract_notice_period(raw_text)
    current_role_company = extract_current_role_and_company(work_history)
    
    # Education
    education_list = result.get("education")
    if not isinstance(education_list, list) or not education_list:
        parsed_resume = result.get("parsed_resume", {}) if isinstance(result.get("parsed_resume"), dict) else {}
        education_list = parsed_resume.get("education") or []
    education = extract_education(education_list)
    
    # Certifications
    certifications_list = result.get("certifications")
    if not isinstance(certifications_list, list) or not certifications_list:
        parsed_resume = result.get("parsed_resume", {}) if isinstance(result.get("parsed_resume"), dict) else {}
        certifications_list = parsed_resume.get("certifications") or []
    flat_cert_names = result.get("certification_names")
    if not isinstance(flat_cert_names, list) or not flat_cert_names:
        parsed_resume = result.get("parsed_resume", {}) if isinstance(result.get("parsed_resume"), dict) else {}
        flat_cert_names = parsed_resume.get("certification_names") or []
    certifications = extract_certifications(certifications_list, flat_cert_names)
    
    return {
        "candidate_name": str(personal_info.get("name") or "Unknown"),
        "experience_duration": exp_duration,
        "salary_info": salary_info,
        "notice_period": notice_period,
        "current_role_company": current_role_company,
        "education": education,
        "certifications": certifications
    }

def validate_and_sanitize_response(parsed: dict, deterministic_data: dict) -> dict:
    if not isinstance(parsed, dict):
        return {
            "answer": "I couldn't find evidence for that in the evaluated resume.",
            "citations": [],
            "confidence": "Low",
            "match_type": "None",
            "interview_verification": "Verify candidate details during interview."
        }
    if not isinstance(deterministic_data, dict):
        deterministic_data = {}

    try:
        answer = str(parsed.get("answer") or "")
        
        # 1. Validate experience duration mismatch
        experience_str = str(deterministic_data.get("experience_duration") or "")
        years_mentioned = re.findall(r'\b(\d+(?:\.\d+)?)\s*(?:years|year)\b', answer.lower())
        
        if years_mentioned:
            det_years_match = re.search(r'\b(\d+(?:\.\d+)?)\s*Years\b', experience_str)
            if det_years_match:
                det_years = float(det_years_match.group(1))
                for yr_str in years_mentioned:
                    yr_val = float(yr_str)
                    if abs(yr_val - det_years) > 1.5 or yr_val > det_years + 0.5:
                        logger.warning("Factual mismatch detected: LLM claims %s years of experience, but deterministic is %s. Applying fallback.", yr_str, det_years)
                        parsed["answer"] = parsed["answer"].replace(yr_str + " years", f"{det_years} years").replace(yr_str + " year", f"{det_years} years")
                        parsed["answer"] = f"Candidate has a verified total of {experience_str} of experience. " + parsed["answer"]
                        parsed["confidence"] = "Medium"
            else:
                for yr_str in years_mentioned:
                    logger.warning("LLM guessed experience (%s years) but experience duration cannot be determined. Applying fallback.", yr_str)
                    parsed["answer"] = parsed["answer"].replace(f"{yr_str} years", "unspecified duration").replace(f"{yr_str} year", "unspecified duration")
                    parsed["confidence"] = "Low"

        # 2. Validate salary expectations/current salary fabrication
        salary_info = str(deterministic_data.get("salary_info") or "")
        if "not available" in salary_info.lower():
            salary_markers = re.findall(r'\b(?:\d[\d,.]*\s*(?:lakh|lpa|k|l|million|\$|inr|rs|usd))\b', answer.lower())
            if salary_markers:
                logger.warning("LLM generated a salary fabrication: %s. Sanitizing response.", salary_markers)
                parsed["answer"] = re.sub(r'\b(?:\d[\d,.]*\s*(?:lakh|lpa|k|l|million|\$|inr|rs|usd))\b', "[information not specified in resume]", parsed["answer"], flags=re.IGNORECASE)
                parsed["confidence"] = "Low"

        # 3. Validate notice period fabrication
        notice_info = str(deterministic_data.get("notice_period") or "")
        if "not specified" in notice_info.lower():
            notice_words = ["notice period", "notice", "days notice", "month notice"]
            if any(w in answer.lower() for w in notice_words):
                fabricated_notice = re.findall(r'\b(?:30|60|90|15|45)\b', answer.lower())
                if fabricated_notice:
                    logger.warning("LLM fabricated notice period: %s. Sanitizing response.", fabricated_notice)
                    parsed["answer"] = "Notice period is not specified in the candidate's resume. " + parsed["answer"]
                    parsed["confidence"] = "Low"
    except Exception as e:
        logger.exception("Error during response validation/sanitization: %s", e)

    return parsed

@router.post("/assistant/ask")
async def ask_assistant(payload: dict):
    """
    Grounded Recruiter Copilot Assistant querying candidate evaluation datasets with robust step instrumentation.
    """
    stage = "initialize_request"
    logger.info("Copilot Assistant Step 1: Received request. Payload: %s", payload)
    
    try:
        if not isinstance(payload, dict):
            payload = {}

        # Extract and validate request parameters
        evaluation_id = payload.get("candidate_id") or payload.get("evaluation_id")
        query = payload.get("query")
        
        if not evaluation_id:
            logger.error("Request validation failed: candidate_id parameter is missing.")
            raise HTTPException(
                status_code=400,
                detail={
                    "error": "missing_candidate_id",
                    "message": "AI assistant initialize failed. Required parameter 'candidate_id' is missing.",
                    "stage": stage
                }
            )
        if not query or not str(query).strip():
            logger.error("Request validation failed: query parameter is missing or empty.")
            raise HTTPException(
                status_code=400,
                detail={
                    "error": "missing_query",
                    "message": "AI assistant initialize failed. Required parameter 'query' is empty.",
                    "stage": stage
                }
            )

        # Step 2: Retrieve evaluation record from database
        stage = "evaluation_lookup"
        logger.info("Copilot Assistant Step 2: Fetching evaluation %s", evaluation_id)
        try:
            eval_data = await evaluation_store.get_evaluation(evaluation_id)
        except Exception as e:
            logger.error("Exception during evaluation_store lookup: %s\n%s", str(e), traceback.format_exc())
            raise HTTPException(
                status_code=500,
                detail={
                    "error": "database_lookup_exception",
                    "message": f"Database error encountered while searching for candidate evaluation: {str(e)}",
                    "stage": stage
                }
            )

        if not eval_data:
            logger.error("Evaluation record not found for ID: %s", evaluation_id)
            raise HTTPException(
                status_code=404,
                detail={
                    "error": "evaluation_not_found",
                    "message": f"Could not find candidate evaluation record for ID: {evaluation_id}",
                    "stage": stage
                }
            )

        # Step 3: Construct Grounded Context
        stage = "context_construction"
        logger.info("Copilot Assistant Step 3: Constructing grounded context.")
        result = eval_data.get("result", {}) if isinstance(eval_data.get("result"), dict) else {}
        personal_info = result.get("personal_info", {}) if isinstance(result.get("personal_info"), dict) else {}
        matched_skills = result.get("matched_skills", []) if isinstance(result.get("matched_skills"), list) else []
        missing_skills = result.get("missing_skills", []) if isinstance(result.get("missing_skills"), list) else []
        evidence = result.get("evidence", {}) if isinstance(result.get("evidence"), dict) else {}
        rec_basis = result.get("recommendation_basis", {}) if isinstance(result.get("recommendation_basis"), dict) else {}
        rec = result.get("recommendation", {}) if isinstance(result.get("recommendation"), dict) else {}
        overall_score = result.get("overall_score", 0)

        # Safely compute deterministic facts programmatically without throwing 500
        try:
            det_data = extract_candidate_deterministic_metadata(eval_data)
        except Exception as e:
            logger.exception("Failed to extract candidate deterministic metadata: %s", e)
            det_data = {
                "candidate_name": str(personal_info.get("name") or "Unknown"),
                "experience_duration": "Experience duration cannot be determined from the available information.",
                "salary_info": "Salary information is not available in the resume.",
                "notice_period": "Notice period is not specified.",
                "current_role_company": "Current role and company are not specified in the resume.",
                "education": "No education details are explicitly listed in the resume.",
                "certifications": "No certifications are explicitly listed in the resume."
            }

        logger.info("Deterministic candidate metadata computed: %s", det_data)

        # Log parameters counts for verification
        matched_count = len(matched_skills)
        missing_count = len(missing_skills)
        impact_count = len(evidence.get("business_impact", [])) if isinstance(evidence.get("business_impact"), list) else 0
        timeline_count = len(evidence.get("career_timeline", [])) if isinstance(evidence.get("career_timeline"), list) else 0

        logger.info(
            "Evaluation context statistics - Matched skills: %d, Missing: %d, Business Impacts: %d, Career milestones: %d",
            matched_count, missing_count, impact_count, timeline_count
        )

        context = f"""
Candidate Name: {det_data.get('candidate_name')}
Overall Fit Score: {overall_score}%
AI Recommendation: {rec.get('hiring_recommendation', 'Unknown')} (Confidence: {rec.get('confidence_score', 0)}%)

Matched Skills: {", ".join(matched_skills) if matched_skills else "None"}
Missing Skills: {", ".join(missing_skills) if missing_skills else "None"}

Candidate Strengths:
{chr(10).join(f"- {s}" for s in rec_basis.get('strengths', [])) if isinstance(rec_basis.get('strengths'), list) else "- None"}

Candidate Gap Areas:
{chr(10).join(f"- {w}" for w in rec_basis.get('weaknesses', [])) if isinstance(rec_basis.get('weaknesses'), list) else "- None"}

Business Impact:
{chr(10).join(f"- [{i.get('category')}]: {i.get('description')}" for i in evidence.get('business_impact', []) if isinstance(i, dict)) if isinstance(evidence.get('business_impact'), list) else "- None"}

Detailed Skills Evidence:
"""
        skills_evidence = evidence.get("skills_evidence") or []
        logger.info("Copilot Assistant: matched_skills=%s, skills_evidence type=%s content=%s", matched_skills, type(skills_evidence).__name__, skills_evidence)
        
        if isinstance(skills_evidence, list):
            for item in skills_evidence:
                if isinstance(item, dict):
                    skill = item.get("skill") or item.get("skill_name") or "Unknown"
                    snippet = item.get("evidence_snippet") or item.get("sentence") or "No explicit sentence matched."
                    context += f"- {skill}: {snippet}\n"
        elif isinstance(skills_evidence, dict):
            for skill, details in skills_evidence.items():
                if isinstance(details, dict):
                    context += f"- {skill}: {details.get('sentence', '')} (Found in section: {details.get('section', 'N/A')})\n"
                elif isinstance(details, str):
                    context += f"- {skill}: {details}\n"
        else:
            logger.warning("skills_evidence format is unsupported: %s", type(skills_evidence).__name__)
                
        context += "\nCareer Timeline Milestones:\n"
        if isinstance(evidence.get("career_timeline"), list):
            for milestone in evidence.get("career_timeline", []):
                if isinstance(milestone, dict):
                    context += f"- {milestone.get('year', '')}: {milestone.get('role', '')} at {milestone.get('company', '')} ({str(milestone.get('description', ''))[:200]})\n"

        # Step 4: Call LLM model pipeline
        stage = "llm_query"
        logger.info("Copilot Assistant Step 4: Dispatching grounded prompt to call_llm.")
        
        system_prompt = f"""You are an AI Recruiter Copilot.
You are not allowed to invent, extrapolate, or assume facts. Answer questions only using the supplied candidate context evaluation record and the verified deterministic candidate metadata.
If the evidence is not sufficient to answer the question, explicitly state: "I couldn't find evidence for that in the evaluated resume." Do not guess or extrapolate.

We have deterministically extracted these verified facts from the candidate's file. You MUST use these values as the source of truth if the user's question asks for them:
- Candidate Name: {det_data.get('candidate_name')}
- Total Experience: {det_data.get('experience_duration')}
- Notice Period: {det_data.get('notice_period')}
- Salary Information: {det_data.get('salary_info')}
- Current Role / Company: {det_data.get('current_role_company')}
- Education: {det_data.get('education')}
- Certifications: {det_data.get('certifications')}

Do not under any circumstances fabricate or estimate dates, project timelines, certifications, expected salary, notice period, or previous employers. Being incomplete is preferable to being incorrect.

Your output response must be structured in valid JSON with these exact keys:
- "answer": A direct, grounded answer string explaining the findings.
- "citations": A list of short string references/proof sentences extracted directly from the candidate's context.
- "confidence": "High", "Medium", or "Low".
- "match_type": "Explicit" or "Inferred" or "None".
- "interview_verification": A suggestion of what the recruiter should verify during the interview.
"""

        user_message = f"""
Candidate context:
{context}

Question: {query}
"""
        try:
            response = call_llm(
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message}
                ],
                temperature=0.0,
                response_format={"type": "json_object"},
                max_tokens=600,
                stage="assistant_ask"
            )
        except Exception as e:
            logger.error("Exception raised during call_llm query: %s\n%s", str(e), traceback.format_exc())
            logger.info("Providing grounded fallback response due to LLM provider exception.")
            return {
                "answer": "The AI assistant LLM pipeline is temporarily unavailable. Candidate evaluation data was successfully retrieved, but the query response could not be generated.",
                "citations": [f"Candidate overall match score is {overall_score}%"],
                "confidence": "Low",
                "match_type": "None",
                "interview_verification": f"Please interview candidate {personal_info.get('name', 'Unknown')} directly about '{query}'."
            }

        # Step 5: Parse and validate LLM output structure
        stage = "llm_json_parser"
        logger.info("Copilot Assistant Step 5: Parsing LLM JSON response.")
        try:
            parsed = json.loads(response)
        except Exception as e:
            logger.error("Failed to parse JSON response from LLM. Raw response content: %s\n%s", response, traceback.format_exc())
            raise HTTPException(
                status_code=500,
                detail={
                    "error": "llm_response_parse_failed",
                    "message": f"AI Copilot returned malformed response details. JSON parsing failed.",
                    "stage": stage
                }
            )

        # Validate required properties
        required_keys = ["answer", "citations", "confidence", "match_type", "interview_verification"]
        missing_keys = [k for k in required_keys if not isinstance(parsed, dict) or k not in parsed]
        if missing_keys:
            logger.error("LLM JSON output is missing required fields: %s. Raw response: %s", missing_keys, response)
            raise HTTPException(
                status_code=500,
                detail={
                    "error": "llm_schema_validation_failed",
                    "message": f"AI Copilot response is missing mandatory fields: {', '.join(missing_keys)}.",
                    "stage": stage
                }
            )

        # Step 6: Response Validation & Sanitization layer
        stage = "response_validation_layer"
        logger.info("Copilot Assistant Step 6: Validating response correctness against deterministic metadata.")
        validated_parsed = validate_and_sanitize_response(parsed, det_data)

        logger.info("Copilot Assistant Step 7: Query successfully evaluated.")
        return validated_parsed

    except HTTPException as he:
        raise he
    except Exception as ge:
        logger.error("General unhandled exception in ask_assistant: %s\n%s", str(ge), traceback.format_exc())
        raise HTTPException(
            status_code=500,
            detail={
                "error": "internal_gateway_failure",
                "message": f"An unhandled backend failure occurred during copilot evaluation. Details: {str(ge)}",
                "stage": stage
            }
        )

@router.post("/dev-mode/verify")
async def dev_mode_verify(payload: dict):
    return {"success": True}