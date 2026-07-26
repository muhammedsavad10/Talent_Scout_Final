"""
Experience Calculator Module for TalentScout Enterprise (v1.7.1 Final AI Core Release).
Computes professional experience metrics ONLY from validated employment, internships, and freelance.
Projects are NEVER passed into or processed by this module.
"""
import re
import logging
from typing import Dict, Any, List, Tuple

logger = logging.getLogger("talentscout_experience_calculator")

KNOWN_PROJECT_TITLES = {
    "delay2decision", "faircrop ai", "sentineldocs", "skillconnect", "iuml",
    "etl ingestion pipeline", "delay2decision agent", "faircrop"
}

def calculate_professional_experience(
    employment_history: List[Dict[str, Any]],
    internships: List[Dict[str, Any]] = None,
    freelance: List[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    v1.7.1 Dedicated Experience Calculator.
    Calculates:
    - total_professional_years
    - professional_experience_count
    - current_company
    - current_role
    - company_diversity

    Guarantees:
    - Ignores Personal Projects, Academic Projects, Portfolio Projects, Hackathons, Coursework.
    - Projects are never passed into this function.
    """
    if internships is None:
        internships = []
    if freelance is None:
        freelance = []

    # 1. Filter out any accidental project entries
    valid_employment = []
    for item in (employment_history or []):
        if not isinstance(item, dict):
            continue
        comp = str(item.get("company") or item.get("employer") or "").strip()
        role = str(item.get("role") or item.get("title") or "").strip()
        if comp.lower() in KNOWN_PROJECT_TITLES:
            logger.warning("[EXPERIENCE CALCULATOR] Rejected project '%s' from employment history", comp)
            continue
        if comp or role:
            valid_employment.append(item)

    prof_count = len(valid_employment)
    
    # 2. Company Diversity (Unique Employers)
    seen_companies = set()
    company_diversity = []
    for item in valid_employment + (freelance or []):
        comp = str(item.get("company") or item.get("employer") or "").strip()
        if comp and comp.lower() not in ["independent / consultant", "unknown", "none", "n/a"] and comp.lower() not in KNOWN_PROJECT_TITLES:
            if comp.lower() not in seen_companies:
                seen_companies.add(comp.lower())
                company_diversity.append(comp)

    # 3. Calculate Total Professional Years strictly from Employment & Freelance
    total_years = 0.0
    current_year = 2026

    for item in valid_employment + (freelance or []):
        dates_str = str(item.get("dates") or item.get("duration") or "").lower()
        years = [int(y) for y in re.findall(r'\b(19\d{2}|20\d{2})\b', dates_str)]
        is_current = item.get("current") or any(w in dates_str for w in ["present", "current", "now", "ongoing"])

        if len(years) >= 2:
            start_year, end_year = years[0], years[1]
            total_years += max(0.5, float(end_year - start_year))
        elif len(years) == 1:
            start_year = years[0]
            end_year = current_year if is_current else start_year
            total_years += max(0.5, float(end_year - start_year))
        elif is_current:
            total_years += 1.0

    total_years = max(0.0, round(total_years, 1))

    # 4. Current Company & Current Role Determination
    current_company = "Unknown"
    current_role = "Unknown"

    if valid_employment:
        primary = valid_employment[0]
        current_company = str(primary.get("company") or primary.get("employer") or "Unknown").strip()
        current_role = str(primary.get("role") or primary.get("title") or "Unknown").strip()

    return {
        "total_professional_years": total_years,
        "professional_experience_count": prof_count,
        "current_company": current_company,
        "current_role": current_role,
        "company_diversity": company_diversity,
        "valid_employment": valid_employment
    }
