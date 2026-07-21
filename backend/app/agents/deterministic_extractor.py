"""
Deterministic Extraction Engine.
"""
import re
from typing import Dict, List, Any

ONTOLOGY_VERSION = "2.0"

# Simple regex patterns for deterministic extraction
EMAIL_PATTERN = re.compile(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}')
PHONE_PATTERN = re.compile(r'\+?\d[\d\-\(\)\s]{8,14}\d')
URL_PATTERN = re.compile(r'https?://(?:www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b(?:[-a-zA-Z0-9()@:%_\+.~#?&//=]*)')

def extract_contact_info(text: str) -> Dict[str, Any]:
    emails = EMAIL_PATTERN.findall(text)
    phones = PHONE_PATTERN.findall(text)
    links = URL_PATTERN.findall(text)
    
    def dedupe(seq):
        seen = set()
        return [x for x in seq if not (x in seen or seen.add(x))]
        
    return {
        "email": emails[0] if emails else None,
        "phone": phones[0].strip() if phones else None,
        "links": dedupe(links)
    }

def extract_known_skills(text: str, known_ontology: List[str]) -> List[str]:
    extracted = []
    text_lower = text.lower()
    for skill in known_ontology:
        escaped_skill = re.escape(skill.lower())
        pattern = re.compile(rf'\b{escaped_skill}\b')
        if pattern.search(text_lower):
            extracted.append(skill)
    return extracted

def extract_skills_deterministically(text: str, source: str) -> List[Dict[str, Any]]:
    # A basic implementation for the deterministic extractor that was lost.
    # We will use the known languages and skills to simulate ontology matching.
    known_languages = {"python", "javascript", "java", "c++", "go", "ruby", "typescript"}
    known_frameworks = {"fastapi", "react", "docker", "spring", "django", "kubernetes", "aws", "pytorch"}
    
    found = []
    words = set(re.findall(r'[a-zA-Z\+]+', text.lower()))
    
    for word in words:
        if word in known_languages:
            found.append({
                "name": word.capitalize(),
                "category": "language",
                "confidence": 90,
                "categories": ["language"]
            })
        elif word in known_frameworks:
            found.append({
                "name": "FastAPI" if word == "fastapi" else ("AWS" if word == "aws" else word.capitalize()),
                "category": "framework",
                "confidence": 90,
                "categories": ["framework"]
            })
    return found

def extract_certifications_deterministically(text: str) -> List[Dict[str, str]]:
    certs = []
    if "AWS Certified" in text:
        certs.append({"title": "AWS Certified"})
    return certs

def extract_languages_deterministically(text: str) -> List[str]:
    # Extract spoken languages if possible. For now, empty or basic matching.
    return []
