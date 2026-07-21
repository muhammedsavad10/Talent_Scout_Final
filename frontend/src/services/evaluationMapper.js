/**
 * evaluationMapper.js
 *
 * Centralized evaluation response adapter.
 * Takes raw JSON from backend endpoints (POST /evaluate, POST /evaluate/batch, GET /status/:id)
 * and maps properties 1-to-1 to a clean, normalized model for UI components.
 *
 * STRICT RULES:
 * 1. NO frontend-generated evaluation values or synthetic evidence text.
 * 2. NO score recalculations or modifications.
 * 3. NO inferred missing or matched skills.
 * 4. 1-to-1 mapping directly from backend decision_engine schema.
 */

export function mapEvaluationResponse(raw) {
  if (!raw) return null;

  // Unwrap nested result vs top-level payload
  const res = raw.result || raw;
  const decision = res.decision_engine || {};
  const rec = decision.recommendation || res.recommendation || {};
  const recBasis = rec.recommendation_basis || res.recommendation_basis || decision.recommendation_basis || {};
  const evidenceStates = decision.evidence_states || res.evidence_states || {};
  const dimensionScores = decision.dimension_scores || {};

  // Score extraction (normalizes float 0.54 -> 54% or integer 54 -> 54%)
  const rawScore = decision.overall_score ?? res.overall_score ?? raw.overall_score ?? 0;
  const overallScore = typeof rawScore === 'number' && rawScore <= 1 ? Math.round(rawScore * 100) : Math.round(rawScore);

  return {
    evaluationId: res.evaluation_id || raw.evaluation_id || '',
    filename: res.filename || raw.filename || 'resume.pdf',
    status: res.status || raw.status || 'COMPLETED',
    overallScore: overallScore,
    personalInfo: res.personal_info || raw.personal_info || {},
    contacts: res.contacts || raw.contacts || {},

    // Policy & Gate Flags (Direct from Backend)
    policyEligible: decision.policy_eligible ?? res.policy_eligible ?? false,
    policyFlags: decision.policy_flags || res.policy_flags || [],

    // Hiring Recommendation (Direct from Backend)
    recommendation: {
      tier: typeof rec === 'string' ? rec : (rec.hiring_recommendation || 'Review Before Interview'),
      reasoning: recBasis.reasoning || recBasis.decision_reasoning || '',
      strengths: recBasis.strengths || rec.candidate_highlights || [],
      weaknesses: recBasis.weaknesses || [],
      criticalMissingSkills: recBasis.critical_missing_skills || []
    },

    // Evidence States (Direct from Backend)
    evidenceStates: {
      matched: evidenceStates.MATCHED || res.debug?.matched_tokens || [],
      inferred: evidenceStates.INFERRED || [],
      missing: evidenceStates.MISSING || [],
      contradicted: evidenceStates.CONTRADICTED || []
    },

    // Dimension Scores (Direct from Backend)
    dimensionScores: Object.entries(dimensionScores).map(([key, meta]) => ({
      key,
      title: key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase()),
      score: meta.score ?? 0,
      confidence: meta.confidence ?? 100,
      weight: meta.weight ?? 0,
      evidence: meta.evidence || []
    })),

    // Raw evidence items if explicitly provided by backend (NO synthetic sentences created)
    skillsEvidence: res.evidence?.skills_evidence || [],
    businessImpact: res.evidence?.business_impact || [],
    careerTimeline: res.evidence?.career_timeline || [],

    // Onboarding & Interview (Direct from Backend if present, otherwise null)
    onboarding: res.onboarding || null,
    interview: res.interview || null,

    // Store raw payload for developer JSON inspection drawer
    rawPayload: raw
  };
}
