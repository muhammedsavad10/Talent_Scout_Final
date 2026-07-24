"""
Validation & Quality Gate Engine for TalentScout Certification Pipeline (v6.0 Production Polishing).
Performs zero-hallucination validation, canonical title cleanup, provider & issuer extraction,
date normalization, category normalization, quality scoring (30/20/20/15/15),
validation status tagging (VALID, PARTIAL, LOW_CONFIDENCE, INVALID), and dynamic confidence scoring.
"""
import re
import logging
from typing import Dict, Any, Optional, Tuple, List

logger = logging.getLogger("talentscout_cert_quality_gate")

KNOWN_PROVIDERS_MAP = {
    "coursera": "Coursera",
    "simplilearn": "Simplilearn",
    "nptel": "NPTEL",
    "udemy": "Udemy",
    "edx": "edX",
    "microsoft learn": "Microsoft Learn",
    "google skill boost": "Google Skill Boost",
    "devtown": "DevTown",
    "linkedin learning": "LinkedIn Learning",
    "pluralsight": "Pluralsight",
    "udacity": "Udacity",
    "nullclass": "Nullclass",
    "great learning": "Great Learning",
    "upgrad": "UpGrad"
}

KNOWN_ISSUERS_MAP = {
    "google": "Google",
    "ibm": "IBM",
    "microsoft": "Microsoft",
    "tableau": "Tableau / Salesforce",
    "redhat": "RedHat",
    "red hat": "RedHat",
    "iit roorkee": "IIT Roorkee",
    "iit madras": "IIT Madras",
    "devtown": "DevTown",
    "coursera": "Coursera",
    "simplilearn": "Simplilearn",
    "nptel": "NPTEL",
    "stanford": "Stanford",
    "aws": "AWS",
    "amazon": "AWS",
    "databricks": "Databricks",
    "snowflake": "Snowflake",
    "salesforce": "Salesforce",
    "oracle": "Oracle",
    "cisco": "Cisco",
    "cncf": "Google / CNCF",
    "global data science institute": "Global Data Science Institute"
}

SUMMARY_REJECT_KEYWORDS = [
    "optimizing", "workflows", "seeking", "opportunities", "proficient in", "worked on",
    "responsible for", "experienced in", "developing", "implementing", "spearheaded",
    "portfolio", "summary", "passionate", "enthusiastic", "skills include", "hands-on experience",
    "ctc", "lpa", "salary", "stipend", "compensation", "per month", "per annum", "l/month", "lakhs"
]

MONTH_MAP = {
    "jan": "Jan", "feb": "Feb", "mar": "Mar", "apr": "Apr",
    "may": "May", "jun": "Jun", "jul": "Jul", "aug": "Aug",
    "sep": "Sep", "oct": "Oct", "nov": "Nov", "dec": "Dec"
}

CERT_ALIAS_MAP = [
    (r'\bgoogle\s+ai\s+essentials\b', "Google AI Essentials", "Google", "Artificial Intelligence"),
    (r'\bgoogle\s+kubernetes\s+engine\b|\bgke\b', "Google Kubernetes Engine (GKE)", "Google", "DevOps / Cloud"),
    (r'\bgoogle\s+cloud\s+(?:foundations?|certified|architect)\b', "Google Cloud Certified", "Google", "DevOps / Cloud"),
    (r'\bibm\s+ai\s+engineering\b|\bibm\s+ai\s+engineering\s+professional\s+certificate\b', "IBM AI Engineering Professional Certificate", "IBM", "Machine Learning"),
    (r'\bibm\s+(?:data\s+science|machine\s+learning)\b', "IBM AI/Data Science Certificate", "IBM", "Machine Learning"),
    (r'\bcertified\s+data\s+scientist\b', "Certified Data Scientist", "Global Data Science Institute", "Machine Learning"),
    (r'\btableau\s+(?:certified|data\s+analyst|desktop|specialist)\b', "Tableau Certified", "Tableau / Salesforce", "Business Intelligence"),
    (r'\baws\s+certified\b|\baws\s+solutions\s+architect\b', "AWS Certified Professional", "AWS", "DevOps / Cloud"),
    (r'\bazure\s+certified\b|\bmicrosoft\s+azure\b', "Microsoft Azure Certified", "Microsoft", "DevOps / Cloud"),
    (r'\bdatabricks\s+certified\b', "Databricks Certified Engineer", "Databricks", "Data Engineering"),
    (r'\bsnowflake\s+certified\b', "Snowflake Certified Core Pro", "Snowflake", "Data Engineering")
]

def is_valid_certification_text(text: str) -> Tuple[bool, str]:
    """
    Phase 1: Strict Certification Validator.
    Rejects summary paragraphs, contact information, URLs, emails, phone numbers, and sentence fragments.
    """
    if not isinstance(text, str) or not text.strip():
        return False, "Empty text"

    s = text.strip()

    words = s.split()
    if len(words) > 18 or len(s) > 140:
        return False, "Exceeds reasonable certification length"

    if "@" in s or ".com" in s.lower() or ".org" in s.lower() or "http" in s.lower() or "www." in s.lower():
        return False, "Contains email or URL"
    if "linkedin" in s.lower() or "github" in s.lower():
        return False, "Contains social link (LinkedIn/GitHub)"
    if any(term in s.lower() for term in ["phone", "+91", "mobile", "contact:"]):
        return False, "Contains contact info"

    s_lower = s.lower()
    for kw in SUMMARY_REJECT_KEYWORDS:
        if kw in s_lower:
            return False, f"Contains summary verb/keyword '{kw}'"

    if any(loc in s_lower for loc in ["trivandrum", "kochi", "bangalore", "chennai", "mumbai", "pincode"]):
        return False, "Contains location term"

    return True, "Valid certification candidate"

def normalize_date(raw_date: str) -> str:
    """
    Issue 7: Standardizes date formatting to 'MMM YYYY', 'MMM', or 'YYYY'.
    """
    if not raw_date or raw_date == "N/A":
        return "N/A"

    d = raw_date.strip("(), ")
    month_match = re.search(r'\b(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\b', d, re.IGNORECASE)
    year_match = re.search(r'\b(19\d\d|20\d\d)\b', d)

    norm_month = MONTH_MAP[month_match.group(1).lower()] if month_match else ""
    norm_year = year_match.group(1) if year_match else ""

    if norm_month and norm_year:
        return f"{norm_month} {norm_year}"
    elif norm_year:
        return norm_year
    elif norm_month:
        return norm_month
    return d

def normalize_category(title: str, existing_cat: str = "") -> str:
    """
    Issue 8: Deterministic Category Mapping.
    """
    t = title.lower()
    if any(k in t for k in ["neural networks", "keras", "deep learning", "ai", "intelligence", "llm", "generative"]):
        return "Artificial Intelligence"
    elif any(k in t for k in ["machine learning", "data science", "data scientist", "pytorch", "tensorflow"]):
        return "Machine Learning"
    elif any(k in t for k in ["cloud", "kubernetes", "gke", "aws", "azure", "docker", "devops"]):
        return "DevOps / Cloud"
    elif any(k in t for k in ["tableau", "power bi", "business intelligence", "analytics"]):
        return "Business Intelligence"
    elif any(k in t for k in ["databricks", "snowflake", "big data", "spark", "etl", "sql"]):
        return "Data Engineering"
    return existing_cat or "Technology"

def clean_canonical_name(raw_name: str) -> Tuple[str, str, str, str]:
    """
    Issue 1, 2, 6, 7: Title Cleanup, Provider/Issuer Extraction & Normalization.
    """
    text = raw_name.strip()
    provider = "N/A"
    issuer = "N/A"
    date_str = "N/A"

    # 1. Extract and normalize date
    date_match = re.search(r'\(?(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s*(?:\d{4})?\)?|\b(?:19\d\d|20\d\d)\b', text, re.IGNORECASE)
    if date_match:
        raw_d = date_match.group(0)
        date_str = normalize_date(raw_d)
        text = text.replace(raw_d, "").strip()

    # 2. Extract and normalize provider
    for p_key, p_val in KNOWN_PROVIDERS_MAP.items():
        if re.search(r'\b' + re.escape(p_key) + r'\b', text.lower()):
            provider = p_val
            text = re.sub(r'(?i),\s*' + re.escape(p_key) + r'\b', '', text).strip()
            break

    # 3. Extract and normalize issuer
    for i_key, i_val in KNOWN_ISSUERS_MAP.items():
        if re.search(r'\b' + re.escape(i_key) + r'\b', text.lower()):
            issuer = i_val
            break

    # 4. Clean Canonical Title (Strip unclosed parentheses, commas, issuer/provider fragments)
    cleaned = text
    # Strip unclosed trailing parentheses e.g. '(Jan' or '(May 2024'
    cleaned = re.sub(r'\([A-Za-z0-9\s]*$', '', cleaned).strip()
    # Strip trailing punctuation, delimiters, or trailing issuer/provider fragments
    cleaned = re.sub(r'[\s,\(\):\-]+$', '', cleaned).strip()
    for item in list(KNOWN_PROVIDERS_MAP.values()) + list(KNOWN_ISSUERS_MAP.values()) + ["ibm", "google", "microsoft"]:
        cleaned = re.sub(r'(?i),\s*' + re.escape(item) + r'\s*$', '', cleaned).strip()

    cleaned = re.sub(r'\s+', ' ', cleaned).strip("-,: ")
    final_title = cleaned or raw_name

    # 5. Alias Matching & Canonical Standardization
    for pattern, c_name, c_issuer, c_cat in CERT_ALIAS_MAP:
        if re.search(pattern, final_title.lower()) or re.search(pattern, raw_name.lower()):
            final_title = c_name
            if not issuer or issuer == "N/A" or issuer == "Industry Accredited":
                issuer = c_issuer
            break

    return final_title, provider, issuer, date_str

def compute_quality_and_confidence(
    canonical_title: str,
    issuer: str,
    provider: str,
    date_str: str,
    evidence: str
) -> Tuple[float, float, str]:
    """
    Issue 3, 4, 5: Deterministic Quality Score (30/20/20/15/15), Confidence, and Validation Status.
    """
    # 1. Quality Score Breakdown
    t_score = 0.30 if len(canonical_title) >= 4 and not re.search(r'[\(\),]', canonical_title) else 0.15
    i_score = 0.20 if issuer != "N/A" and issuer != "Industry Accredited" else 0.10
    p_score = 0.20 if provider != "N/A" else 0.00
    d_score = 0.15 if date_str != "N/A" else 0.00
    n_score = 0.15 if any(re.search(pat, canonical_title.lower()) for pat, _, _, _ in CERT_ALIAS_MAP) else 0.10

    quality_score = round(t_score + i_score + p_score + d_score + n_score, 2)

    # 2. Validation Status Tagging
    if quality_score >= 0.85:
        validation_status = "VALID"
    elif quality_score >= 0.60:
        validation_status = "PARTIAL"
    elif quality_score >= 0.40:
        validation_status = "LOW_CONFIDENCE"
    else:
        validation_status = "INVALID"

    # 3. Dynamic Confidence Calculation
    if any(re.search(pat, canonical_title.lower()) for pat, _, _, _ in CERT_ALIAS_MAP):
        confidence = 1.00
    elif issuer != "Industry Accredited" and issuer != "N/A":
        confidence = 0.95
    elif provider != "N/A":
        confidence = 0.90
    else:
        confidence = 0.75

    return quality_score, confidence, validation_status

def validate_and_gate_certification(raw_entry: Any, line_index: int = 1) -> Optional[Dict[str, Any]]:
    """
    Issue 9: Final Validation Pipeline Stage.
    """
    if isinstance(raw_entry, dict):
        raw_name = str(raw_entry.get("name") or raw_entry.get("title") or "").strip()
        evidence = str(raw_entry.get("evidence") or raw_name).strip()
    else:
        raw_name = str(raw_entry or "").strip()
        evidence = raw_name

    valid, reason = is_valid_certification_text(evidence or raw_name)
    if not valid:
        logger.info("[CERT QUALITY GATE] Rejected invalid text: '%s' | Reason: %s", raw_name[:50], reason)
        return None

    canonical_title, provider, issuer, date_str = clean_canonical_name(raw_name)

    if not issuer or issuer == "N/A":
        title_lower = canonical_title.lower()
        if "google" in title_lower:
            issuer = "Google"
        elif "ibm" in title_lower:
            issuer = "IBM"
        elif "tableau" in title_lower:
            issuer = "Tableau / Salesforce"
        elif "aws" in title_lower or "amazon" in title_lower:
            issuer = "AWS"
        elif "microsoft" in title_lower or "azure" in title_lower:
            issuer = "Microsoft"
        elif "kubernetes" in title_lower or "gke" in title_lower:
            issuer = "Google / CNCF"
        elif "redhat" in title_lower or "red hat" in title_lower:
            issuer = "RedHat"
        elif "databricks" in title_lower:
            issuer = "Databricks"
        elif "snowflake" in title_lower:
            issuer = "Snowflake"
        else:
            issuer = "Industry Accredited"

    category = normalize_category(canonical_title)
    quality_score, confidence, validation_status = compute_quality_and_confidence(
        canonical_title, issuer, provider, date_str, evidence
    )

    if validation_status == "INVALID":
        logger.info("[CERT QUALITY GATE] Rejected INVALID object: '%s'", canonical_title)
        return None

    cert_obj = {
        "canonical_name": canonical_title,
        "original_name": raw_name,
        "issuing_organization": issuer,
        "training_provider": provider,
        "vendor": issuer,  # Issue 2: vendor strictly equals issuing_organization
        "issue_date": date_str,
        "category": category,
        "confidence": confidence,
        "quality_score": quality_score,
        "validation_status": validation_status,
        "evidence": evidence,
        "line_number": line_index,
        "section_heading": "Certifications",
        # Backward compatibility derived aliases:
        "name": canonical_title,
        "title": canonical_title
    }

    return cert_obj
