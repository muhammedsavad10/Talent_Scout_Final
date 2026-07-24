export interface ContactInfo {
  email?: string;
  phone?: string;
  links?: string[];
}

export interface PersonalInfo {
  name?: string;
  email?: string;
  phone?: string;
}

export interface RecommendationInfo {
  hiring_recommendation: string;
  rationale_bullets: string[];
  candidate_summary: string[];
  candidate_highlights: string[];
  disclaimer: string;
}

export interface RecommendationBasis {
  strengths: string[];
  weaknesses: string[];
  critical_missing_skills: string[];
  domain_alignment: string;
  decision_reasoning: string;
}

export interface SkillEvidence {
  context?: string;
  confidence?: string;
  sentence?: string;
}

export interface TimelineMilestone {
  year?: string;
  role?: string;
  company?: string;
  description?: string;
}

export interface BusinessImpactItem {
  category: string;
  description: string;
}

export interface EvidenceInfo {
  skills_evidence?: Record<string, SkillEvidence>;
  business_impact?: BusinessImpactItem[];
  career_timeline?: TimelineMilestone[];
  timeline_title?: string;
}

export interface InterviewInfo {
  interview_questions?: Record<string, string[]> | string[] | any;
}

export interface RecruiterConfidence {
  skill_extraction?: string;
  reasoning?: string;
  learnability?: string;
  evidence_justification?: string;
}

export interface RecruiterInfo {
  confidence?: RecruiterConfidence;
  resume_feedback: string[];
  recruiter_notes: string;
}

export interface DimensionMetadata {
  score: number;
  confidence: number;
  weight: number;
  evidence: string[];
  status?: string;
  sources?: string[];
}

export interface DecisionEngineOutput {
  policy_eligible?: boolean;
  logic_trace?: any[];
  dimension_scores?: Record<string, DimensionMetadata>;
}

export interface LearningCurveItem {
  skill: string;
  difficulty: string;
  reason: string;
}

export interface OnboardingInfo {
  estimated_ramp_up: string;
  rationale_factors: string[];
  learning_curve: LearningCurveItem[];
}

export interface DebugPayload {
  raw_weighted_score: number;
  raw_semantic_similarity: number;
  raw_containment_score: number;
  matched_tokens: string[];
  processing_ms: number;
  agent_logs: string[];
  pipeline_node_transitions: string[];
}

export interface CandidateEvaluationResult {
  evaluation_id: string;
  status: string;
  personal_info: PersonalInfo;
  contacts?: ContactInfo;
  matched_skills: string[];
  missing_skills: string[];
  overall_score: number;
  recommendation: RecommendationInfo;
  recommendation_basis: RecommendationBasis;
  evidence: EvidenceInfo;
  interview: InterviewInfo;
  recruiter: RecruiterInfo;
  decision_engine?: DecisionEngineOutput;
  candidate_facts?: {
    current_employer?: string | null;
    policy_eligible?: boolean;
  };
  certification_suitability?: {
    score: number;
    reasoning: string;
    classifications: Array<{ title: string; tier: string }>;
  };
  onboarding?: OnboardingInfo;
  debug?: DebugPayload;
}

export interface CandidateEvaluationPayload {
  evaluation_id: string;
  filename: string;
  status: string;
  result: CandidateEvaluationResult;
}
