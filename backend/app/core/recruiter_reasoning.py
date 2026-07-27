"""
Recruiter Reasoning Engine for TalentScout Enterprise (v1.9.0).
Simulates senior recruiter evaluation by asking and answering 6 core hiring questions:
1. Why interview this candidate? (Interview Pitch)
2. Why might I reject this candidate? (Rejection Factors)
3. What is the biggest hiring risk? (Hiring Risk Audit)
4. What evidence supports this conclusion? (Supporting Evidence Matrix)
5. What evidence contradicts it? (Contradictory Evidence Matrix)
6. What additional information would reduce uncertainty? (Uncertainty Reduction Audit)
"""
import logging
from typing import Dict, Any, List, Optional
from app.core.evidence_quality import EvidenceQualityScore
from app.core.project_intelligence import ProjectIntelligence
from app.core.employment_intelligence import EmploymentIntelligence

logger = logging.getLogger("talentscout_recruiter_reasoning")

class RecruiterReasoningAudit:
    def __init__(self, candidate_name: str = "Candidate"):
        self.candidate_name = candidate_name
        self.interview_pitch: str = ""
        self.rejection_risk: str = ""
        self.biggest_hiring_risk: str = ""
        self.supporting_evidence: List[str] = []
        self.contradictory_evidence: List[str] = []
        self.uncertainty_reduction: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "candidate_name": self.candidate_name,
            "interview_pitch": self.interview_pitch,
            "rejection_risk": self.rejection_risk,
            "biggest_hiring_risk": self.biggest_hiring_risk,
            "supporting_evidence": self.supporting_evidence,
            "contradictory_evidence": self.contradictory_evidence,
            "uncertainty_reduction": self.uncertainty_reduction
        }

def generate_recruiter_reasoning(
    candidate_name: str,
    stage1_score: float,
    hiring_priority_tier: str,
    work_history: List[Dict[str, Any]],
    projects: List[Dict[str, Any]],
    skills: List[str],
    missing_skills: List[str] = None
) -> RecruiterReasoningAudit:
    """
    v1.9.0 Recruiter Reasoning Simulator.
    Generates structured recruiter rationale for hiring decisions.
    """
    if missing_skills is None:
        missing_skills = []

    audit = RecruiterReasoningAudit(candidate_name=candidate_name)

    # 1. Interview Pitch (Why interview this candidate?)
    if stage1_score >= 85.0:
        audit.interview_pitch = (
            f"{candidate_name} demonstrates exceptional technical alignment ({stage1_score:.1f}% Stage 1 match) "
            f"with verified hands-on skills in {', '.join(skills[:4]) if skills else 'core competencies'}."
        )
    elif stage1_score >= 70.0:
        audit.interview_pitch = (
            f"{candidate_name} presents strong technical suitability ({stage1_score:.1f}% Stage 1 match) "
            f"and solid experience depth across {len(work_history)} employment roles."
        )
    else:
        audit.interview_pitch = (
            f"{candidate_name} meets baseline technical criteria ({stage1_score:.1f}% Stage 1 match) "
            f"with relevant background in {skills[0] if skills else 'the domain'}."
        )

    # 2. Rejection Risk & Biggest Hiring Risk
    if missing_skills:
        audit.rejection_risk = f"Missing explicit evidence for required competencies: {', '.join(missing_skills[:3])}."
        audit.biggest_hiring_risk = f"Technical gap in mandatory required skills ({missing_skills[0]})."
        audit.contradictory_evidence.append(f"Resume lacks explicit mention of required skill '{missing_skills[0]}'.")
    elif len(work_history) == 0:
        audit.rejection_risk = "Limited formal employment history detected."
        audit.biggest_hiring_risk = "Transition from academic/personal projects to enterprise production environment."
        audit.contradictory_evidence.append("No commercial employment records found on resume.")
    else:
        audit.rejection_risk = "Minor risk regarding depth of enterprise scalability experience."
        audit.biggest_hiring_risk = "Verifying high-concurrency production scale during technical interview."

    # 3. Supporting Evidence
    if work_history:
        first_role = work_history[0]
        role_title = first_role.get("role") or first_role.get("title") or "Developer"
        company = first_role.get("company") or "Company"
        audit.supporting_evidence.append(f"Demonstrated role experience as {role_title} at {company}.")

    if projects:
        first_proj = projects[0]
        proj_title = first_proj.get("canonical_title") or first_proj.get("title") or "Project"
        audit.supporting_evidence.append(f"Built technical project '{proj_title}'.")

    # 4. Uncertainty Reduction Audit
    if missing_skills:
        audit.uncertainty_reduction = f"Conduct a technical screening focusing on {missing_skills[0]} architecture and code implementation."
    else:
        audit.uncertainty_reduction = "Verify system design capabilities and team collaboration during behavioral interview."

    return audit
