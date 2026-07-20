"""
Temporary reconstruction stub for Phase C1.
Parser Validation Engine.
Reconstructed after Phase 5 data loss.
"""
from typing import Dict, Any

def validate_parsed_resume(parsed_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validates a parsed resume payload and returns a ParserValidationReport dictionary.
    Deterministic validation without LLM calls.
    """
    sections = ["education", "experience", "skills"]
    report = {
        "overall_score": 100.0,
        "sections": {},
        "repair_performed": False,
        "repair_sections": []
    }
    
    for sec in sections:
        val = parsed_data.get(sec, [])
        status = "PASS" if val else "FAIL"
        score = 100.0 if val else 0.0
        
        report["sections"][sec] = {
            "status": status,
            "confidence": 100,
            "expected": 1,
            "parsed": len(val) if isinstance(val, list) else 1 if val else 0,
            "completeness": 1.0 if val else 0.0,
            "evidence_quality": 1.0 if val else 0.0,
            "section_score": score,
            "repair_threshold": 50,
            "reason": None
        }
        
        if status == "FAIL":
            report["overall_score"] -= 33.3
            
    # Normalize score
    report["overall_score"] = max(0.0, round(report["overall_score"], 2))
    
    return report
