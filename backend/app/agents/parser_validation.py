"""
Parser Validation Engine.
Validates parsed resume JSON structure against minimum production threshold.
"""
from typing import Dict, Any

def validate(parsed_data: Dict[str, Any], sections: Dict[str, Any] = None, raw_text: str = None) -> Dict[str, Any]:
    """
    Validates a parsed resume payload and returns a ParserValidationReport dictionary.
    Deterministic validation without synthetic data injection.
    """
    report = {
        "overall_score": 100.0,
        "sections": {},
        "repair_performed": False,
        "repair_sections": []
    }
    
    has_skills = bool(parsed_data.get("skills")) or bool(parsed_data.get("hard_skills"))
    has_experience = bool(parsed_data.get("experience")) or bool(parsed_data.get("work_history")) or bool(parsed_data.get("projects"))
    has_info = bool(parsed_data.get("personal_info")) or bool(parsed_data.get("raw_resume_text")) or bool(raw_text)
    
    # Valid resume parsing requires at least skills, experience/projects, or candidate text
    if has_skills or has_experience or has_info:
        score = 70.0
        if has_skills:
            score += 15.0
        if has_experience:
            score += 15.0
        report["overall_score"] = min(100.0, score)
    else:
        report["overall_score"] = 0.0

    return report

validate_parsed_resume = validate
