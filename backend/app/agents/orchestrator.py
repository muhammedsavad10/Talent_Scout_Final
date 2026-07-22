"""
Temporary reconstruction stub for Phase C4A.
Evaluation Pipeline Orchestrator.
Reconstructed after Phase 5 data loss.
"""
import logging
import json
from typing import Dict, Any, List
from app.agents.normalization import normalize_skills_list
from app.agents.parser_validation import validate_parsed_resume
from app.agents.deterministic_extractor import extract_contact_info, extract_known_skills
from app.agents.decision_engine import run_decision_engine
from app.agents.ingestion import parse_resume_to_json

logger = logging.getLogger(__name__)

def _build_skills_evidence(evidence_states: Dict[str, List[str]]) -> List[Dict[str, Any]]:
    items = []
    for status_key, skill_list in evidence_states.items():
        is_identified = status_key in ("MATCHED", "INFERRED")
        status_label = "Identified" if is_identified else "Not identified"
        strength = "High" if is_identified else "Low"
        for skill_name in skill_list:
            items.append({
                "skill": skill_name,
                "status": status_label,
                "evidence_snippet": None,
                "project_name": None,
                "role_held": None,
                "evidence_strength": strength,
                "match_confidence": 100 if is_identified else 0,
                "reasoning": None
            })
    return items

async def run_evaluation_pipeline(text: str, candidate_id: str, required_skills: List[str] = None) -> Dict[str, Any]:
    """
    Orchestrates the internal evaluation pipeline.
    Does NOT calculate scores, apply policy, or generate recommendations.
    """
    if required_skills is None:
        required_skills = []
        
    try:
        # 1. Parser (Delegated to LLM)
        parsed_resume = parse_resume_to_json(text)
        if not parsed_resume:
            return {"status": "error", "error_stage": "parser", "message": "Failed to parse resume"}
            
        if "error" in parsed_resume:
            return {"status": "error", "error_stage": "parser", "message": parsed_resume["error"]}
            
        # 2. Normalization
        if "skills" in parsed_resume:
            for cat, skills_list in parsed_resume["skills"].items():
                if isinstance(skills_list, list):
                    parsed_resume["skills"][cat] = normalize_skills_list(skills_list)
                    
        if "hard_skills" in parsed_resume:
            parsed_resume["hard_skills"] = normalize_skills_list(parsed_resume["hard_skills"])

        # 3. Parser Validation
        validation_report = validate_parsed_resume(parsed_resume)
        if validation_report["overall_score"] < 50:
            return {"status": "error", "error_stage": "validation", "message": "Parsed resume failed validation"}

        # 4. Deterministic Extraction
        contacts = extract_contact_info(text)
        known_skills = extract_known_skills(text, required_skills)
        parsed_resume["contacts"] = contacts
        
        # Merge known_skills if parser missed them
        if "hard_skills" not in parsed_resume:
            parsed_resume["hard_skills"] = []
        parsed_resume["hard_skills"].extend([s for s in known_skills if s not in parsed_resume["hard_skills"]])
        parsed_resume["hard_skills"] = normalize_skills_list(parsed_resume["hard_skills"])

        # 5, 6, 7. Scorer -> Policy -> Strategy (Delegated to Decision Engine)
        decision_output = run_decision_engine(parsed_resume, required_skills)
        
        # Extract nested data for enriched output
        rec_section = decision_output.get("recommendation", {})
        rec_basis = rec_section.get("recommendation_basis", {})
        evidence_states = decision_output.get("evidence_states", {})
        overall = decision_output.get("overall_score", 0)
        
        # Build the evidence section frontend expects
        skills_evidence = _build_skills_evidence(evidence_states)
        reasoning_text = rec_basis.get("reasoning", "")
        strengths = rec_basis.get("strengths", [])
        
        result = {
            "evaluation_id": candidate_id,
            "status": "success",
            "personal_info": parsed_resume.get("personal_info", {}),
            "contacts": contacts,
            "overall_score": overall,
            "decision_engine": decision_output,
            "recommendation": {
                "hiring_recommendation": rec_section.get("hiring_recommendation", "Unknown"),
                "rationale_bullets": [reasoning_text] if reasoning_text else [],
                "candidate_summary": strengths,
                "candidate_highlights": strengths[:3],
                "disclaimer": "This assessment is based only on information present in the submitted resume."
            },
            "recommendation_basis": {
                "strengths": strengths,
                "weaknesses": rec_basis.get("weaknesses", []),
                "critical_missing_skills": rec_basis.get("critical_missing_skills", []),
                "domain_alignment": rec_basis.get("domain_alignment", "Unknown"),
                "decision_reasoning": reasoning_text,
                "reasoning": reasoning_text
            },
            "evidence": {
                "skills_evidence": skills_evidence,
                "business_impact": [],
                "career_timeline": [],
                "timeline_title": "Chronological Career Milestones"
            },
            "onboarding": {
                "estimated_ramp_up": "2-4 weeks",
                "rationale_factors": [],
                "learning_curve": []
            },
            "interview": {
                "verify_during_interview": [],
                "interview_questions": {"easy": [], "medium": [], "advanced": []}
            },
            "recruiter": {
                "confidence": {
                    "skill_extraction": "High",
                    "reasoning": "Medium",
                    "learnability": "Medium",
                    "evidence_justification": "Automated evaluation"
                },
                "resume_feedback": [],
                "recruiter_notes": ""
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
                    "Scorer", "PolicyEngine", "Strategy"
                ]
            }
        }
        return result
        
    except Exception as e:
        logger.exception("Pipeline failed unexpectedly")
        return {"status": "error", "error_stage": "orchestrator", "message": str(e)}
