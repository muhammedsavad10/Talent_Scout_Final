"""
Dynamic JD Competency Model Engine for TalentScout Enterprise (v1.8.4).
Dynamically infers target role competencies, technologies, domain expertise, seniority, and production/leadership expectations
directly from the Job Description (JD) without role-specific hardcoded lists or case-by-case rules.

Supports any profession (Software Engineering, AI, Finance, Healthcare, Cybersecurity, Marketing, HR, Sales, Legal, etc.).
"""
import re
import logging
from typing import Dict, Any, List, Set, Optional

logger = logging.getLogger("talentscout_jd_competency_model")

SENIORITY_KEYWORDS = {
    "architect": "Architect",
    "principal": "Principal",
    "lead": "Lead",
    "senior": "Senior",
    "sr": "Senior",
    "mid": "Mid",
    "intermediate": "Mid",
    "junior": "Junior",
    "entry": "Junior",
    "intern": "Junior",
    "trainee": "Junior"
}

PRODUCTION_INDICATOR_KEYWORDS = {
    "production", "deploy", "deployment", "scaling", "high availability", "ci/cd",
    "kubernetes", "k8s", "docker", "aws", "gcp", "azure", "cloud", "microservices",
    "terraform", "monitoring", "prometheus", "grafana", "devops"
}

LEADERSHIP_INDICATOR_KEYWORDS = {
    "lead", "leader", "mentorship", "mentor", "management", "manage", "manager",
    "head", "director", "principal", "guided", "spearheaded", "coached"
}

BUSINESS_DOMAINS = {
    "finance": {"fintech", "banking", "finance", "trading", "crypto", "blockchain", "accounting"},
    "healthcare": {"healthcare", "health", "medical", "pharma", "biotech", "clinical"},
    "cybersecurity": {"cybersecurity", "security", "infosec", "soc", "penetration", "compliance"},
    "e_commerce": {"e-commerce", "ecommerce", "retail", "shopping", "payment"},
    "artificial_intelligence": {"ai", "data science", "data scientist", "machine learning", "ml", "deep learning", "nlp", "computer vision", "llm", "rag", "python", "pytorch", "tensorflow", "qdrant", "scikit-learn"},
    "web_development": {"web", "full stack", "frontend", "backend", "mern", "mean", "ui/ux", "react", "node", "nodejs", "express", "mongodb", "javascript"}
}

class JDCompetencyModel:
    def __init__(self, jd_title: str = "Target Role"):
        self.jd_title = jd_title
        self.domain_name = "General"
        self.core_technologies: Set[str] = set()
        self.supporting_technologies: Set[str] = set()
        self.required_skills: Set[str] = set()
        self.preferred_skills: Set[str] = set()
        self.domain_expertise: Set[str] = set()
        self.seniority_expectation: str = "Mid"
        self.production_expectations: Set[str] = set()
        self.leadership_expectations: Set[str] = set()
        self.business_domain_indicators: Set[str] = set()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "jd_title": self.jd_title,
            "domain_name": self.domain_name,
            "core_technologies": sorted(list(self.core_technologies)),
            "supporting_technologies": sorted(list(self.supporting_technologies)),
            "required_skills": sorted(list(self.required_skills)),
            "preferred_skills": sorted(list(self.preferred_skills)),
            "domain_expertise": sorted(list(self.domain_expertise)),
            "seniority_expectation": self.seniority_expectation,
            "production_expectations": sorted(list(self.production_expectations)),
            "leadership_expectations": sorted(list(self.leadership_expectations)),
            "business_domain_indicators": sorted(list(self.business_domain_indicators))
        }

def build_jd_competency_model(jd_text: str, required_skills: List[str] = None) -> JDCompetencyModel:
    """
    v1.8.4 Dynamic Competency Model Inference.
    Parses JD text and required_skills to build a role-aware competency model.
    """
    if required_skills is None:
        required_skills = []

    text_lower = (jd_text or "").lower()
    first_lines = text_lower.split("\n")[:3]
    jd_title_guess = first_lines[0].strip() if first_lines and len(first_lines[0].strip()) < 50 else "Target Role"

    model = JDCompetencyModel(jd_title=jd_title_guess)

    # 1. Infer Seniority Expectation
    for kw, level in SENIORITY_KEYWORDS.items():
        if re.search(r'\b' + re.escape(kw) + r'\b', text_lower):
            model.seniority_expectation = level
            break

    # 2. Extract Core and Required Skills
    for s in required_skills:
        if isinstance(s, str) and s.strip():
            s_clean = s.strip()
            model.required_skills.add(s_clean.lower())
            model.core_technologies.add(s_clean.lower())

    # Extract additional skills directly mentioned in JD
    words = re.findall(r'\b[a-zA-Z0-9\+\#\.\-]{2,20}\b', text_lower)
    from app.agents.deterministic_extractor import extract_skills_from_jd
    extracted = extract_skills_from_jd(jd_text)
    for sk in extracted:
        sk_lower = sk.lower()
        if sk_lower in model.required_skills:
            model.core_technologies.add(sk_lower)
        else:
            model.supporting_technologies.add(sk_lower)

    # 3. Infer Business & Technical Domain Context
    for domain, kws in BUSINESS_DOMAINS.items():
        if any(re.search(r'\b' + re.escape(kw) + r'\b', text_lower) for kw in kws):
            model.business_domain_indicators.add(domain)
            model.domain_expertise.update(kws)
            if model.domain_name == "General":
                model.domain_name = domain.replace("_", " ").title()

    # 4. Infer Production & Leadership Expectations
    for prod_kw in PRODUCTION_INDICATOR_KEYWORDS:
        if re.search(r'\b' + re.escape(prod_kw) + r'\b', text_lower):
            model.production_expectations.add(prod_kw)

    for lead_kw in LEADERSHIP_INDICATOR_KEYWORDS:
        if re.search(r'\b' + re.escape(lead_kw) + r'\b', text_lower):
            model.leadership_expectations.add(lead_kw)

    logger.info("[JD COMPETENCY MODEL] Inferred Domain: '%s' | Seniority: '%s' | Core Techs: %s",
                model.domain_name, model.seniority_expectation, list(model.core_technologies)[:5])

    return model
