"""
Dual-Dimension Evidence Relevance & Confidence Engine for TalentScout Enterprise (v1.8.4).
Evaluates every extracted evidence item across two independent dimensions:
- Extraction Confidence (C in [0.0, 1.0])
- Role Relevance (R in [0.0, 1.0])

Contribution = Confidence x Relevance x BaseWeight.

Prevents unrelated expertise (e.g. AI skills for a MERN role) from inflating candidate scores,
and ensures low-confidence/corrupted extractions contribute minimally.
"""
import logging
from typing import Dict, Any, List, Optional
from app.core.jd_competency_model import JDCompetencyModel

logger = logging.getLogger("talentscout_evidence_relevance_engine")

class EvaluatedEvidenceItem:
    def __init__(
        self,
        name: str,
        category: str,
        confidence: float,
        relevance: float,
        base_weight: float = 1.0,
        evidence_quote: str = "",
        reason: str = ""
    ):
        self.name = name
        self.category = category
        self.confidence = min(1.0, max(0.0, round(confidence, 2)))
        self.relevance = min(1.0, max(0.0, round(relevance, 2)))
        self.base_weight = base_weight
        self.contribution = round(self.confidence * self.relevance * self.base_weight, 3)
        self.evidence_quote = evidence_quote
        self.reason = reason or f"Evidence '{name}' evaluated with C={self.confidence}, R={self.relevance}."

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "category": self.category,
            "confidence": self.confidence,
            "relevance": self.relevance,
            "base_weight": self.base_weight,
            "contribution": self.contribution,
            "evidence_quote": self.evidence_quote,
            "reason": self.reason
        }

def evaluate_skill_evidence(
    skill_name: str,
    competency_model: JDCompetencyModel,
    is_explicit_match: bool = False,
    is_inferred_match: bool = False,
    is_equivalent_match: bool = False,
    confidence: Optional[float] = None
) -> EvaluatedEvidenceItem:
    """
    Evaluates skill evidence against JD Competency Model.
    """
    sk_lower = skill_name.lower().strip()

    # Extraction Confidence
    if confidence is not None:
        conf = confidence
    elif is_explicit_match:
        conf = 1.00
    elif is_equivalent_match:
        conf = 0.90
    elif is_inferred_match:
        conf = 0.85
    else:
        conf = 1.00  # Default candidate skill extraction confidence is high (1.00)

    # Role Relevance Gating
    if sk_lower in competency_model.required_skills or sk_lower in competency_model.core_technologies:
        relevance = 1.00
        reason = f"Skill '{skill_name}' is a core required competency for {competency_model.jd_title}."
    elif sk_lower in competency_model.supporting_technologies:
        relevance = 0.75
        reason = f"Skill '{skill_name}' is a supporting technology for {competency_model.jd_title}."
    elif sk_lower in competency_model.domain_expertise:
        relevance = 0.75
        reason = f"Skill '{skill_name}' is related domain expertise for {competency_model.jd_title}."
    else:
        # Unrelated Skill Gating (e.g. AI skills when applying for MERN / Marketing / Finance role)
        relevance = 0.20
        reason = f"Skill '{skill_name}' is unrelated to target role '{competency_model.jd_title}' (Low Relevance)."

    return EvaluatedEvidenceItem(
        name=skill_name,
        category="SKILL",
        confidence=conf,
        relevance=relevance,
        base_weight=1.0,
        reason=reason
    )

def evaluate_work_history_evidence(
    work_item: Dict[str, Any],
    competency_model: JDCompetencyModel
) -> EvaluatedEvidenceItem:
    """
    Evaluates employment entry relevance against target JD Competency Model.
    """
    role_str = str(work_item.get("role") or work_item.get("title") or "").strip()
    company_str = str(work_item.get("company") or "").strip()
    desc_str = str(work_item.get("description") or "").strip()

    # Extraction Confidence
    if role_str and company_str and company_str != "Unknown Company":
        confidence = 0.98
    elif role_str:
        confidence = 0.85
    else:
        confidence = 0.60

    # Role Relevance Gating
    role_lower = role_str.lower()
    desc_lower = desc_str.lower()

    relevance = 0.50  # Base line work experience relevance
    matching_terms = []

    # Check title alignment with JD domain or JD title
    if competency_model.jd_title.lower() in role_lower or role_lower in competency_model.jd_title.lower():
        relevance = 1.00
        matching_terms.append("Direct Title Match")

    for req_tech in competency_model.core_technologies:
        if req_tech in role_lower or req_tech in desc_lower:
            relevance = min(1.00, relevance + 0.25)
            matching_terms.append(req_tech)

    for domain_kw in competency_model.domain_expertise:
        if domain_kw in role_lower or domain_kw in desc_lower:
            relevance = min(1.00, relevance + 0.15)
            matching_terms.append(domain_kw)

    if not matching_terms and relevance == 0.50:
        relevance = 0.30  # Damped relevance for unrelated work role

    reason = f"Role '{role_str}' at '{company_str}' evaluated with relevance {relevance:.2f} (Matches: {', '.join(matching_terms) if matching_terms else 'General Work Experience'})."

    return EvaluatedEvidenceItem(
        name=f"{role_str} at {company_str}",
        category="EMPLOYMENT",
        confidence=confidence,
        relevance=relevance,
        base_weight=1.5,
        evidence_quote=desc_str[:150],
        reason=reason
    )

def evaluate_project_evidence(
    project_item: Dict[str, Any],
    competency_model: JDCompetencyModel
) -> EvaluatedEvidenceItem:
    """
    Evaluates project entry relevance against target JD Competency Model.
    """
    title = str(project_item.get("canonical_title") or project_item.get("title") or "").strip()
    desc = str(project_item.get("summary") or project_item.get("description") or "").strip()
    techs = project_item.get("technologies") or []

    # Extraction Confidence
    confidence = float(project_item.get("merge_confidence") or 0.95)

    # Role Relevance Gating
    relevance = 0.40
    matched_skills = []

    for t in techs:
        t_lower = t.lower()
        if t_lower in competency_model.core_technologies:
            relevance = min(1.00, relevance + 0.30)
            matched_skills.append(t)
        elif t_lower in competency_model.supporting_technologies:
            relevance = min(1.00, relevance + 0.15)
            matched_skills.append(t)

    for domain_kw in competency_model.domain_expertise:
        if domain_kw in desc.lower() or domain_kw in title.lower():
            relevance = min(1.00, relevance + 0.20)
            matched_skills.append(domain_kw)

    reason = f"Project '{title}' evaluated with relevance {relevance:.2f} for role '{competency_model.jd_title}' (Matched Competencies: {', '.join(matched_skills) if matched_skills else 'General Technical Project'})."

    return EvaluatedEvidenceItem(
        name=title,
        category="PROJECT",
        confidence=confidence,
        relevance=relevance,
        base_weight=1.2,
        evidence_quote=desc[:150],
        reason=reason
    )
