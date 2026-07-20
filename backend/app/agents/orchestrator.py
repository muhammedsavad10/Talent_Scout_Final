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
from app.agents.scout import parse_resume_stub

logger = logging.getLogger(__name__)

async def run_evaluation_pipeline(text: str, candidate_id: str, required_skills: List[str] = None) -> Dict[str, Any]:
    """
    Orchestrates the internal evaluation pipeline.
    Does NOT calculate scores, apply policy, or generate recommendations.
    """
    if required_skills is None:
        required_skills = []
        
    try:
        # 1. Parser (Delegated to Scout/LLM facade)
        parsed_resume = parse_resume_stub(text)
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
        
        # 8. Collect Outputs
        result = {
            "evaluation_id": candidate_id,
            "status": "success",
            "personal_info": parsed_resume.get("personal_info", {}),
            "contacts": contacts,
            "overall_score": decision_output["overall_score"],
            "decision_engine": decision_output,
            "recommendation": decision_output["recommendation"]
        }
        return result
        
    except Exception as e:
        logger.exception("Pipeline failed unexpectedly")
        return {"status": "error", "error_stage": "orchestrator", "message": str(e)}
