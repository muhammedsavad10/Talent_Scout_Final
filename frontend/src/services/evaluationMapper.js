/**
 * evaluationMapper.js
 *
 * Centralized evaluation response adapter.
 * Takes raw JSON from backend endpoints (POST /evaluate, POST /evaluate/batch, GET /status/:id)
 * and maps properties 1-to-1 to a clean, normalized model for UI components.
 *
 * STRICT RULES:
 * 1. NO legacy schema fallbacks (res.debug.* removed).
 * 2. NO UI title formatting (keeps raw keys pure for presentation layer).
 * 3. Modularized into focused, testable extraction and normalization functions.
 * 4. Runtime schema validation flags invalid or unexpected backend schemas.
 */

export function validateEvaluationResponse(raw) {
  if (!raw) {
    console.error("❌ [EvaluationMapper] Raw evaluation payload is null or undefined.");
    return false;
  }
  const res = raw.result || raw;
  if (!res.decision_engine && !res.evaluation_id) {
    console.warn("⚠️ [EvaluationMapper] Schema warning: missing decision_engine object in backend payload.", raw);
  }
  return true;
}

export function normalizeScore(rawScore) {
  if (rawScore === null || rawScore === undefined) return 0;
  if (typeof rawScore === 'number') {
    return rawScore <= 1.0 ? Math.round(rawScore * 100) : Math.round(rawScore);
  }
  return 0;
}

export function normalizeRecommendation(rec, recBasis) {
  const tier = typeof rec === 'string'
    ? rec
    : (rec?.hiring_recommendation || 'Review Before Interview');

  return {
    tier,
    reasoning: recBasis?.reasoning || recBasis?.decision_reasoning || '',
    strengths: recBasis?.strengths || rec?.candidate_highlights || [],
    weaknesses: recBasis?.weaknesses || [],
    criticalMissingSkills: recBasis?.critical_missing_skills || []
  };
}

export function normalizeEvidenceStates(evidenceStates = {}) {
  return {
    matched: Array.isArray(evidenceStates.MATCHED) ? evidenceStates.MATCHED : [],
    inferred: Array.isArray(evidenceStates.INFERRED) ? evidenceStates.INFERRED : [],
    missing: Array.isArray(evidenceStates.MISSING) ? evidenceStates.MISSING : [],
    contradicted: Array.isArray(evidenceStates.CONTRADICTED) ? evidenceStates.CONTRADICTED : []
  };
}

export function normalizeDimensionScores(dimensionScores = {}) {
  return Object.entries(dimensionScores).map(([key, meta]) => ({
    key,
    score: meta?.score ?? 0,
    confidence: meta?.confidence ?? 100,
    weight: meta?.weight ?? 0,
    evidence: meta?.evidence || []
  }));
}

export function mapEvaluationResponse(raw) {
  validateEvaluationResponse(raw);
  if (!raw) return null;

  const res = raw.result || raw;
  const decision = res.decision_engine || {};
  const rec = decision.recommendation || res.recommendation || {};
  const recBasis = rec.recommendation_basis || res.recommendation_basis || {};
  const evidenceStates = decision.evidence_states || res.evidence_states || {};
  const dimensionScores = decision.dimension_scores || {};

  const mapped = {
    evaluationId: res.evaluation_id || raw.evaluation_id || '',
    filename: res.filename || raw.filename || 'resume.pdf',
    status: res.status || raw.status || 'COMPLETED',
    backendVersion: raw.version || decision.decision_engine_version || '1.2.7',

    overallScore: normalizeScore(decision.overall_score ?? res.overall_score ?? raw.overall_score),

    // Direct Policy Flags (No Legacy Fallbacks)
    policyEligible: decision.policy_eligible ?? res.policy_eligible ?? false,
    policyFlags: decision.policy_flags || res.policy_flags || [],

    recommendation: normalizeRecommendation(rec, recBasis),
    evidenceStates: normalizeEvidenceStates(evidenceStates),
    dimensionScores: normalizeDimensionScores(dimensionScores),

    skillsEvidence: res.evidence?.skills_evidence || [],
    businessImpact: res.evidence?.business_impact || [],
    careerTimeline: res.evidence?.career_timeline || [],
    onboarding: res.onboarding || null,
    interview: res.interview || null,

    rawPayload: raw
  };

  if (import.meta.env.DEV) {
    console.group("💡 [Evaluation Mapping]");
    console.log("Raw Response Payload:", raw);
    console.log("Normalized Model Output:", mapped);
    console.groupEnd();
  }

  return mapped;
}
