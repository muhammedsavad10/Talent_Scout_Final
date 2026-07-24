"""
Deterministic Certification Authority Ontology Module.
Classifies certifications into Tier 1 (Enterprise/Industry Standard) vs Tier 2 (Coursework).
"""
import re
import logging
from typing import Dict, Any, List

logger = logging.getLogger("talentscout_cert_ontology")

TIER_1_KEYWORDS = [
    "aws certified", "gcp professional", "google cloud certified", "azure certified",
    "cissp", "oscp", "cka", "ckad", "pmp", "databricks certified",
    "terraform associate", "red hat certified", "comptia security+", "ccna", "ccnp"
]

TIER_2_KEYWORDS = [
    "udemy", "coursera", "linkedin learning", "edx", "sololearn",
    "hackerrank", "bootcamp", "deeplearning.ai", "certificate of completion",
    "course completion", "completion certificate"
]

def classify_certification(title: str, issuer: str = "") -> Dict[str, Any]:
    """
    Classifies a certification into Tier 1 (Industry Standard) or Tier 2 (Coursework).
    """
    combined = f"{title} {issuer}".lower()
    
    # 1. Check for Tier 1 matches
    for kw in TIER_1_KEYWORDS:
        if kw in combined:
            return {
                "title": title,
                "tier": "Industry-Standard",
                "tier_code": 1,
                "weight": 1.0,
                "reasoning": "Recognized enterprise credential or proctored exam."
            }

    # 2. Check for Tier 2 matches
    for kw in TIER_2_KEYWORDS:
        if kw in combined:
            return {
                "title": title,
                "tier": "Course-Completion",
                "tier_code": 2,
                "weight": 0.2,
                "reasoning": "Online learning course completion certificate."
            }

    # Default fallback: Treat unverified certs as Course-Completion
    return {
        "title": title,
        "tier": "Course-Completion",
        "tier_code": 2,
        "weight": 0.2,
        "reasoning": "General certificate of study without enterprise proctoring."
    }

def evaluate_certifications_suitability(parsed_resume: Dict[str, Any]) -> Dict[str, Any]:
    """
    Evaluates candidate certifications deterministically.
    Tier 2 course completions never dominate or inflate scores.
    """
    raw_certs = parsed_resume.get("certifications", [])
    if not raw_certs:
        # Check flat certification names
        raw_certs = [{"title": name} for name in parsed_resume.get("certification_names", [])]

    if not raw_certs:
        return {
            "score": 50,
            "reasoning": "No certifications cataloged on resume.",
            "classifications": [],
            "tier1_count": 0,
            "tier2_count": 0
        }

    classifications = []
    tier1_count = 0
    tier2_count = 0

    for c in raw_certs:
        title = ""
        issuer = ""
        if isinstance(c, dict):
            title = c.get("title", "")
            issuer = c.get("issuer", "")
        elif isinstance(c, str):
            title = c
            
        if not title:
            continue
            
        res = classify_certification(title, issuer)
        classifications.append(res)
        if res["tier_code"] == 1:
            tier1_count += 1
        else:
            tier2_count += 1

    # Scoring logic: Tier 1 certs provide high boost; Tier 2 caps out at 60 max score
    if tier1_count > 0:
        cert_score = min(100, 75 + (tier1_count * 15))
        reasoning = f"Validated {tier1_count} Industry-Standard enterprise certification(s)."
    elif tier2_count > 0:
        cert_score = 60  # Capped: Coursework indicates study interest but no hard gate bypass
        reasoning = f"Cataloged {tier2_count} course-completion certificate(s). Capped score as coursework."
    else:
        cert_score = 50
        reasoning = "Certifications parsed but authority tier unverified."

    return {
        "score": cert_score,
        "reasoning": reasoning,
        "classifications": classifications,
        "tier1_count": tier1_count,
        "tier2_count": tier2_count
    }
