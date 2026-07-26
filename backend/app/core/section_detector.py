"""
Section Boundary Detection Engine for TalentScout Enterprise v1.1.
Detects resume headings and parses raw text into explicit, bounded section blocks.
Prevents cross-section contamination between Projects, Experience, and Certifications.
"""
import re
from typing import Dict, List, Any

SECTION_HEADINGS = {
    "certifications": [
        r"(?i)^\s*(?:certifications?|licenses?|credentials?|accreditations?|courses?|certificates?)\b"
    ],
    "experience": [
        r"(?i)^\s*(?:professional\s+experience|work\s+experience|employment\s+history|career\s+history|experience|employment)\b"
    ],
    "projects": [
        r"(?i)^\s*(?:personal\s+projects|technical\s+projects|academic\s+projects|notable\s+projects|projects|portfolio)\b"
    ],
    "education": [
        r"(?i)^\s*(?:education|academic\s+background|academic\s+history|studies|degrees?)\b"
    ],
    "skills": [
        r"(?i)^\s*(?:technical\s+skills|core\s+competencies|skills\s+inventory|hard\s+skills|skills)\b"
    ]
}

def detect_resume_sections(text: str) -> Dict[str, str]:
    """
    Parses raw resume text into distinct section blocks.
    Returns a dictionary mapping section names to their text content.
    """
    lines = text.splitlines()
    sections: Dict[str, List[str]] = {
        "header": [],
        "experience": [],
        "projects": [],
        "certifications": [],
        "education": [],
        "skills": [],
        "other": []
    }
    
    current_section = "header"
    
    for line in lines:
        line_clean = line.strip()
        if not line_clean:
            continue
            
        detected = None
        for sec_name, patterns in SECTION_HEADINGS.items():
            for pat in patterns:
                if re.match(pat, line_clean):
                    detected = sec_name
                    break
            if detected:
                break
                
        if detected:
            current_section = detected
        else:
            sections[current_section].append(line_clean)
            
    return {sec: "\n".join(content) for sec, content in sections.items()}
