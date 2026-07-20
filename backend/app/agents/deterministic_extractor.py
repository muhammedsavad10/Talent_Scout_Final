"""
Temporary reconstruction stub for Phase C1.
Deterministic Extraction Engine.
Reconstructed after Phase 5 data loss.
"""
import re
from typing import Dict, List, Any

# Simple regex patterns for deterministic extraction
EMAIL_PATTERN = re.compile(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}')
# A very basic phone pattern
PHONE_PATTERN = re.compile(r'\+?\d[\d\-\(\)\s]{8,14}\d')
URL_PATTERN = re.compile(r'https?://(?:www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b(?:[-a-zA-Z0-9()@:%_\+.~#?&//=]*)')

def extract_contact_info(text: str) -> Dict[str, Any]:
    """
    Extracts email, phone, and links deterministically from raw resume text.
    """
    emails = EMAIL_PATTERN.findall(text)
    phones = PHONE_PATTERN.findall(text)
    links = URL_PATTERN.findall(text)
    
    # Deduplicate while preserving order
    def dedupe(seq):
        seen = set()
        return [x for x in seq if not (x in seen or seen.add(x))]
        
    return {
        "email": emails[0] if emails else None,
        "phone": phones[0].strip() if phones else None,
        "links": dedupe(links)
    }

def extract_known_skills(text: str, known_ontology: List[str]) -> List[str]:
    """
    Extracts skills deterministically by matching known ontology against the text.
    Uses word boundaries to prevent partial matches.
    """
    extracted = []
    text_lower = text.lower()
    
    for skill in known_ontology:
        # Simple word boundary regex to find skill in text
        escaped_skill = re.escape(skill.lower())
        pattern = re.compile(rf'\b{escaped_skill}\b')
        if pattern.search(text_lower):
            extracted.append(skill)
            
    return extracted
