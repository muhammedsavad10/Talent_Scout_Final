"""
Temporary reconstruction stub for Phase C1.
Deterministic Normalization Engine.
Reconstructed after Phase 5 data loss.
"""
import re
import unicodedata
from typing import List

# Minimal ontology aliases for fallback if config isn't available
DEFAULT_ALIASES = {
    "fast-api": "FastAPI",
    "fastapi": "FastAPI",
    "fast api": "FastAPI",
    "reactjs": "ReactJS",
    "react.js": "ReactJS",
    "node.js": "Node.js",
    "nodejs": "Node.js"
}

def split_camel_case(text: str) -> str:
    """
    Splits CamelCase into Space Separated words unless it's a known single entity (like ReactJS).
    But for simple normalization, we can insert spaces before capitals that follow lowercase.
    """
    # Simple regex to add space between lowercase and uppercase
    return re.sub(r'([a-z])([A-Z])', r'\1 \2', text)

def normalize_unicode(text: str) -> str:
    """
    Normalizes unicode characters (e.g., smart quotes, accents).
    """
    return unicodedata.normalize('NFKD', text).encode('ascii', 'ignore').decode('utf-8')

def normalize_punctuation(text: str) -> str:
    """
    Normalizes punctuation (e.g., removing extra spaces around hyphens).
    """
    # Replace multiple spaces with a single space
    text = re.sub(r'\s+', ' ', text)
    # Strip leading/trailing punctuation except alphanumeric
    text = text.strip(" .,;:|/'\"-")
    return text

def resolve_alias(skill: str) -> str:
    """
    Resolves a skill to its canonical name using the ontology aliases.
    """
    lower_skill = skill.lower()
    return DEFAULT_ALIASES.get(lower_skill, skill)

def normalize_skill(skill: str) -> str:
    """
    Full pipeline to normalize a single skill string.
    """
    if not skill:
        return ""
    
    # 1. Unicode normalization
    text = normalize_unicode(skill)
    
    # 2. Check if it's a known alias
    canonical = resolve_alias(text)
    if canonical != text:
        return canonical
    
    # Check if the text itself (without alias mapping) is in the values (e.g. "FastAPI")
    if text.lower() in [v.lower() for v in DEFAULT_ALIASES.values()]:
        # Return the exact casing from the known canonical form
        for v in DEFAULT_ALIASES.values():
            if v.lower() == text.lower():
                return v
        
    # If not a known alias, normalize it generically
    text = split_camel_case(text)
    text = normalize_punctuation(text)
    
    return text.strip()

def normalize_skills_list(skills: List[str]) -> List[str]:
    """
    Normalizes a list of skills and removes duplicates.
    """
    normalized = []
    seen = set()
    for skill in skills:
        norm = normalize_skill(skill)
        if norm and norm.lower() not in seen:
            seen.add(norm.lower())
            normalized.append(norm)
    return normalized
