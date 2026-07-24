"""
Job Criticality Engine.
Deterministically classifies Job Description seniority level (Junior, Professional, Senior)
and defines calibrated recommendation interpretation thresholds.
Stage 1 scores remain 100% untouched.
"""
from typing import Dict, Any

CRITICALITY_THRESHOLDS = {
    "Junior": {
        "strong_hire": 85,
        "hire": 70,
        "interview": 55,
        "review": 40,
        "reject": 40
    },
    "Professional": {
        "strong_hire": 90,
        "hire": 75,
        "interview": 60,
        "review": 45,
        "reject": 45
    },
    "Senior": {
        "strong_hire": 92,
        "hire": 80,
        "interview": 65,
        "review": 50,
        "reject": 50
    }
}

def determine_job_criticality(jd_text: str, target_role: str = "") -> Dict[str, Any]:
    combined = f"{target_role} {jd_text}".lower()

    senior_indicators = [
        "senior", "lead", "principal", "staff", "architect", "head",
        "director", "vp", "chief", "5+ years", "6+ years", "7+ years",
        "8+ years", "10+ years", "expert", "specialist"
    ]
    junior_indicators = [
        "junior", "entry", "associate", "intern", "trainee", "graduate",
        "0-1 years", "1-2 years", "fresh"
    ]

    is_senior = any(k in combined for k in senior_indicators)
    is_junior = any(k in combined for k in junior_indicators)

    if is_senior and not is_junior:
        level = "Senior"
        display = "Senior Level / Lead Role"
    elif is_junior and not is_senior:
        level = "Junior"
        display = "Junior Level / Entry Role"
    else:
        level = "Professional"
        display = "Professional / Mid-Level Role"

    return {
        "criticality_level": level,
        "display_name": display,
        "thresholds": CRITICALITY_THRESHOLDS[level]
    }
