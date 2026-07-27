"""
Text Processing Utilities Module for TalentScout Enterprise (Phase B Reliability & Code Quality).
Provides centralized, strongly-typed, deterministic text cleaning and extraction helpers.
Preserves 100% backward compatibility with all AI evaluation engines.
"""
import re
from typing import Optional, List, Set

def clean_text_string(text: Optional[str]) -> str:
    """
    Safely cleans raw text input by stripping whitespace and removing null characters.
    Returns empty string if input is None.
    """
    if text is None:
        return ""
    return str(text).replace("\0", "").strip()

def normalize_candidate_name(name: Optional[str]) -> str:
    """
    Normalizes candidate name strings for display and logging.
    Capitalizes words cleanly while stripping trailing punctuation.
    """
    cleaned = clean_text_string(name)
    if not cleaned or cleaned.lower() in ["unknown", "unknown candidate", "none", "null"]:
        return "Unknown Candidate"
    cleaned = re.sub(r'[\,\.\;\:\(\)\[\]\{\}\<\>]', '', cleaned)
    return " ".join([word.capitalize() for word in cleaned.split()])

def extract_lowercase_keywords(text: Optional[str]) -> Set[str]:
    """
    Extracts lowercase alphanumeric word tokens from text.
    """
    cleaned = clean_text_string(text).lower()
    if not cleaned:
        return set()
    tokens = re.findall(r'\b[a-z0-9\+\#\.\-]{2,30}\b', cleaned)
    return set(tokens)

def sanitize_prompt_input(text: Optional[str]) -> str:
    """
    Phase C Security Hardening:
    Sanitizes raw text inputs to prevent prompt injection and XSS script tags.
    Strips dangerous HTML/script tags and adversarial system override instructions.
    """
    cleaned = clean_text_string(text)
    if not cleaned:
        return ""
    # Neutralize HTML script tags
    cleaned = re.sub(r'<script.*?>.*?</script>', '', cleaned, flags=re.IGNORECASE | re.DOTALL)
    cleaned = re.sub(r'<iframe.*?>.*?</iframe>', '', cleaned, flags=re.IGNORECASE | re.DOTALL)
    # Neutralize prompt injection system overrides
    cleaned = re.sub(r'(?i)ignore\s+all\s+previous\s+instructions', '[REDACTED_ADVERSARIAL_PROMPT]', cleaned)
    cleaned = re.sub(r'(?i)system\s+prompt\s+override', '[REDACTED_ADVERSARIAL_PROMPT]', cleaned)
    return cleaned
