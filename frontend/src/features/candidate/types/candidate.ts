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

export interface DecisionEngineOutput {
  policy_eligible?: boolean;
  logic_trace?: any[];
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
}

export interface CandidateEvaluationPayload {
  evaluation_id: string;
  filename: string;
  status: string;
  result: CandidateEvaluationResult;
}
