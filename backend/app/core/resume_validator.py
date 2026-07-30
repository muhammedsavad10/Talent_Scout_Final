"""
Resume Document Validation Engine for TalentScout Enterprise.
Pre-parsing validation gate to verify whether an uploaded document is a genuine resume
before invoking LangGraph parsing and LLM evaluation pipelines.
"""
import re
from typing import Tuple, Dict, Any

NON_RESUME_KEYWORDS = [
    r"(?i)\binvoice\b",
    r"(?i)\bbill\s+to\b",
    r"(?i)\btotal\s+amount\s+due\b",
    r"(?i)\bsubtotal\b",
    r"(?i)\btax\s+rate\b",
    r"(?i)\breceipt\s*#?\b",
    r"(?i)\babstract\b\s*[\n:]",
    r"(?i)\breferences\b\s*[\n:]\s*\[1\]",
    r"(?i)\bfigure\s+\d+:\b",
    r"(?i)\btable\s+\d+:\b",
    r"(?i)\bterms\s+and\s+conditions\b"
]

def validate_is_resume(text: str) -> Tuple[bool, float, str]:
    """
    Evaluates raw extracted document text and calculates a Resume Confidence Score (0-100).
    Returns a tuple of (is_valid: bool, score: float, user_message: str).
    """
    if not text or not text.strip():
        return False, 0.0, "The uploaded document appears to be empty."

    text_clean = text.strip()
    text_lower = text_clean.lower()
    score = 0.0

    # 1. Contact Information Signal (Weight: 25 points)
    email_match = re.search(r'[\w\.-]+@[\w\.-]+\.\w+', text_clean)
    phone_match = re.search(r'\+?\d[\d\s\-\(\)]{7,}\d', text_clean)
    link_match = re.search(r'(?i)(github\.com|linkedin\.com)', text_clean)

    if email_match:
        score += 10.0
    if phone_match:
        score += 10.0
    if link_match:
        score += 5.0

    # 2. Work Experience / Employment History Signal (Weight: 30 points)
    exp_patterns = [
        r"(?i)\b(?:work\s+experience|professional\s+experience|employment\s+history|career\s+history|experience)\b",
        r"(?i)\b(?:present|202[0-6]|201[0-9])\b"
    ]
    if re.search(exp_patterns[0], text_clean):
        score += 20.0
    if re.search(exp_patterns[1], text_clean):
        score += 10.0

    # 3. Education Signal (Weight: 15 points)
    edu_pattern = r"(?i)\b(?:education|academic|bachelor|master|degree|b\.tech|b\.e|m\.tech|m\.s|b\.s|university|college)\b"
    if re.search(edu_pattern, text_clean):
        score += 15.0

    # 4. Technical Skills / Projects Signal (Weight: 20 points)
    skills_pattern = r"(?i)\b(?:skills|technical\s+skills|projects|built|developed|python|java|javascript|c\+\+|sql|aws|docker)\b"
    if re.search(skills_pattern, text_clean):
        score += 20.0

    # 5. Non-Resume Penalties (-50 points for non-resume document types)
    for pattern in NON_RESUME_KEYWORDS:
        if re.search(pattern, text_clean):
            score -= 25.0

    score = max(0.0, min(100.0, score))

    if score < 40.0:
        return False, score, "The uploaded document does not appear to be a valid résumé. Please upload a résumé in PDF or DOCX format."

    return True, score, "Valid résumé document detected."
