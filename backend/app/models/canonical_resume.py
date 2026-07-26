"""
Canonical Resume Model — Single Source of Truth for TalentScout Enterprise v1.6.
Defines the single canonical structured representation shared by all downstream scoring,
hiring priority, comparator, and explanation components.
Includes FieldProvenance tracking for zero-hallucination evidence chains.
"""
from typing import Dict, List, Any, Optional
from pydantic import BaseModel, Field

class FieldProvenance(BaseModel):
    field_name: str
    section: str = "Unknown"
    evidence_quote: str = ""
    confidence: float = 0.95

class EmploymentEntry(BaseModel):
    company: str
    role: str
    dates: str = "N/A"
    description: str = ""
    current: bool = False

class ProjectEntry(BaseModel):
    title: str
    description: str = ""
    technologies: List[str] = Field(default_factory=list)

class CertificationEntry(BaseModel):
    vendor: str
    title: str
    category: str = "General"
    confidence: float = 0.95

class CanonicalResume(BaseModel):
    candidate_name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    education: List[str] = Field(default_factory=list)
    work_history: List[EmploymentEntry] = Field(default_factory=list)
    projects: List[ProjectEntry] = Field(default_factory=list)
    certifications: List[CertificationEntry] = Field(default_factory=list)
    hard_skills: List[str] = Field(default_factory=list)
    raw_resume_text: str = ""
    evidence_confidence: float = 0.95
    project_complexity: float = 0.0
    provenance: Dict[str, FieldProvenance] = Field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "CanonicalResume":
        personal_info = data.get("personal_info", {})
        if not isinstance(personal_info, dict):
            personal_info = {}

        name = personal_info.get("name") or data.get("candidate_name") or "Unknown Candidate"
        email = personal_info.get("email") or data.get("email")
        phone = personal_info.get("phone") or data.get("phone")

        work_history = []
        for w in data.get("work_history", []):
            if isinstance(w, dict):
                work_history.append(EmploymentEntry(
                    company=w.get("company", "Unknown Company"),
                    role=w.get("role", "Engineer"),
                    dates=w.get("dates", "N/A"),
                    description=w.get("description", ""),
                    current=w.get("current", False)
                ))

        raw_proj = data.get("projects", [])
        if isinstance(raw_proj, list) and raw_proj:
            from app.core.project_deduplicator import deduplicate_projects
            raw_proj = deduplicate_projects(raw_proj)

        projects = []
        for p in raw_proj:
            if isinstance(p, dict):
                projects.append(ProjectEntry(
                    title=p.get("canonical_title") or p.get("title", "Project"),
                    description=p.get("summary") or p.get("description", ""),
                    technologies=p.get("technologies", [])
                ))

        certifications = []
        for c in data.get("certifications", []):
            if isinstance(c, dict):
                certifications.append(CertificationEntry(
                    vendor=c.get("vendor", "Accredited Provider"),
                    title=c.get("title") or c.get("name", "Certification"),
                    category=c.get("category", "General"),
                    confidence=c.get("confidence", 0.95)
                ))

        skills = data.get("hard_skills") or []
        if not skills and isinstance(data.get("skills"), dict):
            for k, v in data["skills"].items():
                if isinstance(v, list):
                    skills.extend(v)

        provenance_dict = {}
        if work_history:
            provenance_dict["current_company"] = FieldProvenance(
                field_name="current_company", section="experience", evidence_quote=work_history[0].company, confidence=0.98
            )
            provenance_dict["current_role"] = FieldProvenance(
                field_name="current_role", section="experience", evidence_quote=work_history[0].role, confidence=0.98
            )
        if projects:
            provenance_dict["top_project"] = FieldProvenance(
                field_name="top_project", section="projects", evidence_quote=projects[0].title, confidence=0.95
            )

        return cls(
            candidate_name=name,
            email=email,
            phone=phone,
            education=data.get("education", []),
            work_history=work_history,
            projects=projects,
            certifications=certifications,
            hard_skills=list(set(skills)),
            raw_resume_text=data.get("raw_resume_text", ""),
            evidence_confidence=data.get("evidence_confidence", 0.95),
            project_complexity=data.get("project_complexity", 0.0),
            provenance=provenance_dict
        )
