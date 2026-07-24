"""
Pydantic schemas for data validation and LLM output enforcement.
"""
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from enum import Enum

class JobProfile(str, Enum):
    ML_ENGINEER = "ml_engineer"
    BACKEND_ENGINEER = "backend_engineer"
    DATA_ANALYST = "data_analyst"
    GENERAL = "general"

class IndustryProfile(str, Enum):
    FINTECH = "fintech"
    HEALTHCARE = "healthcare"
    CYBERSECURITY = "cybersecurity"
    GENERAL = "general"

class EvaluationEngineMetadata(BaseModel):
    engine: str = "Business Decision Engine"
    version: str = "1.2.0"
    config_version: str = Field(..., description="Configuration files weights version")
    policy_version: str = Field(default="1.0.0", description="Hiring policy configuration version")
    generated_at: str = Field(..., description="Timestamp when evaluation was executed")
    deterministic: bool = True
    weights_fingerprint: str = Field(..., description="SHA256 fingerprint of the configuration weights.yaml")

class DimensionMetadata(BaseModel):
    score: int = Field(..., ge=0, le=100)
    confidence: int = Field(..., ge=0, le=100)
    weight: float = Field(..., ge=0.0, le=1.0)
    evidence: List[str] = Field(default_factory=list)
    status: Optional[str] = None
    sources: Optional[List[str]] = None
    health: Optional[Dict] = None
    sub_metrics: Optional[Dict[str, Any]] = None

class DecisionEngineOutput(BaseModel):
    decision_engine_version: str = "1.2.7"
    weights_version: str
    rules_version: str
    ontology_version: str
    decision_stability: float = Field(default=1.0, description="Stability reliability factor metric")
    overall_score: int = Field(..., ge=0, le=100)
    dimension_scores: Dict[str, DimensionMetadata]
    positive_signals: List[str]
    risk_factors: List[str]
    score_contributions: List[str]
    score_contribution: Optional[Dict[str, float]] = None
    experience_metrics: Optional[Dict[str, Any]] = None
    decision_trace: List[str]
    recommendation: str
    suitability_score: Optional[int] = None
    competitiveness_score: Optional[int] = None
    recommendation_stability: Optional[str] = None
    hiring_intelligence_signals: Optional[List[str]] = None
    decision_validation: Optional[Dict] = None

class PolicyResult(BaseModel):
    recommendation: str
    policy_rule_triggered: str
    hard_gate_failed: bool
    critical_missing_skills: List[str]
    critical_contradicted_skills: List[str]
    required_fail_rate: float
    positive_signals: List[str]
    risk_signals: List[str]
    decision_reasoning: str

class SkillsStructured(BaseModel):
    """Structured breakdown of technical skills, tools, and concepts."""
    programming_languages: List[str] = Field(default_factory=list, description="Programming languages like Python, JS, etc.")
    frameworks: List[str] = Field(default_factory=list, description="Frameworks like FastAPI, Django, React, etc.")
    libraries: List[str] = Field(default_factory=list, description="Libraries like NumPy, PyTorch, LangChain, etc.")
    cloud_platforms: List[str] = Field(default_factory=list, description="Cloud platforms like AWS, GCP, Azure, etc.")
    databases: List[str] = Field(default_factory=list, description="Databases like PostgreSQL, MongoDB, Qdrant, etc.")
    ml_algorithms: List[str] = Field(default_factory=list, description="ML algorithms like Classification, Clustering, etc.")
    ml_workflows: List[str] = Field(default_factory=list, description="ML workflows like Feature Engineering, MLOps, RAG, etc.")
    statistics_concepts: List[str] = Field(default_factory=list, description="Statistics and math concepts.")
    devops_tools: List[str] = Field(default_factory=list, description="DevOps tools like Docker, Kubernetes, CI/CD, etc.")
    visualization_tools: List[str] = Field(default_factory=list, description="Visualization tools like Tableau, Matplotlib, etc.")
    technical_concepts: List[str] = Field(default_factory=list, description="General technical concepts like NLP, Computer Vision, etc.")
    other: List[str] = Field(default_factory=list, description="Any other technical or domain-specific skills.")

class WorkExperienceEntry(BaseModel):
    company: Optional[str] = Field(default="", description="Name of company")
    role: Optional[str] = Field(default="", description="Job title / role")
    dates: Optional[str] = Field(default="", description="Start Date - End Date / Years")
    description: Optional[str] = Field(default="", description="Key duties and achievements")

class ProjectEntry(BaseModel):
    title: Optional[str] = Field(default="", description="Name of project")
    role: Optional[str] = Field(default="", description="Role in project")
    dates: Optional[str] = Field(default="", description="Project dates")
    description: Optional[str] = Field(default="", description="Project description")

class PersonalInfo(BaseModel):
    name: Optional[str] = Field(default=None, description="Full name of candidate")
    email: Optional[str] = Field(default=None, description="Email address")
    phone: Optional[str] = Field(default=None, description="Phone number")
    links: List[str] = Field(default_factory=list, description="Links like GitHub, LinkedIn, etc.")

class RepairReason(BaseModel):
    section: str
    reason: str
    trigger: str
    method: str

class ValidationSectionStatus(BaseModel):
    status: str = "PASS"
    confidence: int = 100
    expected: int = 0
    parsed: int = 0
    completeness: float = 1.0
    evidence_quality: float = 1.0
    section_score: float = 100.0
    repair_threshold: int = 0
    reason: Optional[RepairReason] = None

class ParserValidationReport(BaseModel):
    overall_score: float = 100.0
    sections: Dict[str, ValidationSectionStatus] = Field(default_factory=dict)
    repair_performed: bool = False
    repair_sections: List[str] = Field(default_factory=list)

class ParserHistoryEntry(BaseModel):
    attempt: int
    overall_score: float
    repair: bool

class SkillEntry(BaseModel):
    name: str
    category: str
    sources: List[str] = Field(default_factory=list)
    confidence: int = 100
    method: str = "deterministic"

class CertificationEntry(BaseModel):
    title: str
    issuer: str = ""
    year: str = ""
    credential_type: str = "Certification"
    confidence: int = 100

class ParserMetrics(BaseModel):
    parser_version: str = "v2.0"
    
    # Parser Quality Metrics
    extraction_completeness: float = 100.0
    garbage_rate: float = 0.0
    duplicate_rate: float = 0.0
    structure_quality: float = 100.0
    overall_score: float = 100.0
    
    # Execution Stats
    deterministic_items: int = 0
    llm_items: int = 0
    repaired_items: int = 0
    duplicates_removed: int = 0
    garbage_removed: int = 0
    repair_triggered: bool = False
    repair_latency_ms: int = 0
    repair_calls: int = 0
    llm_repairs: int = 0
    sections_repaired: List[str] = Field(default_factory=list)
    section_scores: Dict[str, float] = Field(default_factory=dict)

class OntologySuggestion(BaseModel):
    unknown_skill: str
    seen_in_resumes: int = 1
    average_confidence: float
    suggested_category: str = "Needs Review"
    recommended_aliases: List[str] = Field(default_factory=list)

class OntologyMetrics(BaseModel):
    ontology_version: str = "v1.1"
    coverage: float = 100.0
    matched: int = 0
    unknown: int = 0
    ontology_suggestions: List[OntologySuggestion] = Field(default_factory=list)

class ParsedResume(BaseModel):
    """Strict schema for the LLM to follow when parsing a resume."""
    education: List[str] = Field(description="List of degrees and universities")
    experience: List[str] = Field(description="List of job titles and companies")
    work_history: List[WorkExperienceEntry] = Field(default_factory=list, description="Structured work experience details")
    projects: List[ProjectEntry] = Field(default_factory=list, description="Structured project details")
    certifications: List[CertificationEntry] = Field(default_factory=list, description="List of structured certifications")
    certification_names: List[str] = Field(default_factory=list, description="Flat list of certification names for backwards compatibility")
    skills: SkillsStructured = Field(default_factory=SkillsStructured, description="Structured categorized skills")
    hard_skills: List[str] = Field(default_factory=list, description="List of explicit technical skills, tools, and frameworks")
    detailed_skills: List[SkillEntry] = Field(default_factory=list, description="List of detailed skill objects with source and confidence")
    unknown_skills: List[str] = Field(default_factory=list, description="Skills not mapped to ontology")
    raw_resume_text: Optional[str] = Field(default=None, description="Optional raw text extracted from resume PDF")
    personal_info: Optional[PersonalInfo] = Field(default=None, description="Personal contact info")
    languages: List[str] = Field(default_factory=list, description="Languages spoken")
    awards: List[str] = Field(default_factory=list, description="Awards/Honors")
    parser_validation: ParserValidationReport = Field(default_factory=lambda: ParserValidationReport())
    parser_history: List[ParserHistoryEntry] = Field(default_factory=list)
    parser_metrics: Optional[ParserMetrics] = None
    ontology_metrics: Optional[OntologyMetrics] = None

# --- Recruiter Business Insights Schemas ---

class RecommendationSection(BaseModel):
    hiring_recommendation: str = Field(..., description="Recommended for Interview, Review Before Interview, Keep as Backup, Not Suitable for this Role")
    rationale_bullets: List[str] = Field(..., description="Why this recommendation was reached bullets")
    candidate_summary: List[str] = Field(..., description="Maximum 3 bullet points suitability summary")
    candidate_highlights: List[str] = Field(..., description="AI Candidate Highlights of the strongest qualifications")
    disclaimer: str = Field(
        default="This assessment is based only on information present in the submitted resume. Skills or experience not mentioned may not be reflected in the evaluation."
    )

class BusinessImpactItem(BaseModel):
    category: str = Field(..., description="Performance, Cost, Automation, Revenue, or General")
    description: str = Field(..., description="Quantitative outcome details")

class CareerTimelineItem(BaseModel):
    year: Optional[str] = None
    role: str
    company: str
    details: str

class SkillEvidenceItem(BaseModel):
    skill: str
    evidence_snippet: Optional[str] = Field(None, description="Exact matching sentence context from resume")
    project_name: Optional[str] = Field(None, description="Project context title")
    role_held: Optional[str] = Field(None, description="Role held")
    status: str = Field(..., description="MATCHED, INFERRED, MISSING, or CONTRADICTED")
    proficiency: Optional[str] = Field(None, description="Foundational, Advanced, or Expert")
    match_confidence: Optional[int] = Field(None, description="Confidence in explicit match")
    inference_confidence: Optional[int] = Field(None, description="Confidence in inference")
    match_origin: Optional[str] = Field(None, description="Origin of the match (e.g. Work History, Prerequisite Graph)")
    evidence_signals: List[str] = Field(default_factory=list, description="Other skills driving the inference")
    evidence_strength: str = Field(..., description="High, Medium, or Low")
    reasoning: Optional[str] = Field(None, description="Explainability reasoning string")

class EvidenceSection(BaseModel):
    skills_evidence: List[SkillEvidenceItem] = Field(..., description="Evidence maps for JD requirements")
    business_impact: List[BusinessImpactItem] = Field(..., description="Dynamic list of impact outcomes")
    career_timeline: List[CareerTimelineItem] = Field(..., description="Vertical work experiences timeline list")

class LearningCurveItem(BaseModel):
    skill: str
    difficulty: str = Field(..., description="Easy, Moderate, Steeper Learning Curve")
    reason: str = Field(..., description="Adjacent technology transition context")

class OnboardingSection(BaseModel):
    estimated_ramp_up: str = Field(..., description="Timeline: e.g. 2-4 weeks")
    rationale_factors: List[str] = Field(..., description="upskilling justification factors")
    learning_curve: List[LearningCurveItem] = Field(..., description="Adjacent skills mapping matrix list")

class DifficultyGradedQuestions(BaseModel):
    easy: List[str]
    medium: List[str]
    advanced: List[str]

class InterviewSection(BaseModel):
    verify_during_interview: List[str] = Field(..., description="Focus areas and verification tasks for the interview")
    interview_questions: DifficultyGradedQuestions = Field(..., description="Difficulty-graded questions checklist")

class SegmentedConfidence(BaseModel):
    skill_extraction: str = Field(..., description="High, Medium, Low")
    reasoning: str = Field(..., description="High, Medium, Low")
    learnability: str = Field(..., description="High, Medium, Low")
    evidence_justification: str

class ResumeFeedbackCheck(BaseModel):
    label: str = Field(..., description="Check: e.g. Add deployment links")
    status: str = Field(..., description="pass / warning")

class RecruiterSection(BaseModel):
    confidence: SegmentedConfidence = Field(..., description="Segmented confidence levels")
    resume_feedback: List[ResumeFeedbackCheck] = Field(..., description="Actionable checklist checks")
    recruiter_notes: str = Field(..., description="Notes field, read-only with Edit/Save actions")

class DebugPayload(BaseModel):
    raw_weighted_score: float
    raw_semantic_similarity: float
    raw_containment_score: float
    matched_tokens: List[str]
    processing_ms: float
    agent_logs: List[str]
    pipeline_node_transitions: List[str] = Field(..., description="Langsmith-style pipeline execution order")
    evidence_coverage_report: Optional[dict] = None
    decision_engine: Optional[DecisionEngineOutput] = None

class RecommendationBasis(BaseModel):
    strengths: List[str] = Field(default_factory=list, description="Candidate's top strengths based on evidence")
    weaknesses: List[str] = Field(default_factory=list, description="Candidate's primary weaknesses")
    critical_missing_skills: List[str] = Field(default_factory=list, description="Key required skills missing")
    domain_alignment: str = Field(default="Unknown", description="How well their past domains align")
    decision_reasoning: str = Field(default="", description="The core justification for the recommendation")

class RecruiterEvaluationResponse(BaseModel):
    schema_version: str = Field("1.0.0", description="API contract version")
    evaluation_id: str = Field(..., description="Unique UUID for audit trails")
    strategy_available: bool = Field(default=True, description="Indicates if AI strategy insights were successfully generated")
    candidate_id: str = Field(..., description="Candidate tracker ID")
    job_id: str = Field(..., description="Target Job Description ID")
    timestamp: str = Field(..., description="Evaluation timestamp")
    filename: str
    recommendation: RecommendationSection
    evidence: EvidenceSection
    onboarding: OnboardingSection
    interview: InterviewSection
    recruiter: RecruiterSection
    debug: Optional[DebugPayload] = None
    evaluation_engine: Optional[EvaluationEngineMetadata] = None
    decision_engine: Optional[DecisionEngineOutput] = None
    parser_metrics: Optional[ParserMetrics] = None
    recommendation_basis: Optional[RecommendationBasis] = None


class BatchEvaluationRequest(BaseModel):
    job_description: str
    job_profile: Optional[JobProfile] = None
    industry_profile: Optional[IndustryProfile] = None
    jd_skills: List[str] = Field(default_factory=list)

class CandidateComparisonRow(BaseModel):
    rank: int
    candidate_name: str
    filename: str
    recommendation_tier: str
    policy_eligible: bool
    overall_score: float
    skill_match: float
    experience_quantity: float
    experience_relevance: float
    experience_quality: float
    project_complexity: float
    critical_missing: List[str]
    required_missing: List[str]
    strengths: List[str]
    weaknesses: List[str]
    evaluation_id: str
    role_fit: Optional[float] = None
    technical_match: Optional[float] = None
    experience_alignment: Optional[float] = None
    project_relevance: Optional[float] = None
    evidence_confidence: Optional[float] = None

class BatchEvaluationResponse(BaseModel):
    batch_id: str
    total_candidates: int
    successfully_evaluated: int
    failed_evaluations: int
    average_score: float
    tier_counts: Dict[str, int]
    top_candidate_id: Optional[str] = None
    ranked_candidates: List[CandidateComparisonRow]

class BatchEvaluationStatusResponse(BaseModel):
    batch_id: str
    status: str
    total: int
    queued: int
    processing: int
    completed: int
    failed: int
    results: Optional[BatchEvaluationResponse] = None
