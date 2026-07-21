import { describe, it, expect } from 'vitest';
import {
  mapEvaluationResponse,
  normalizeScore,
  normalizeRecommendation,
  normalizeEvidenceStates,
  validateEvaluationResponse
} from './evaluationMapper';

describe('evaluationMapper.js', () => {
  // Test 1: Normal backend response maps correctly
  it('maps a normal backend response correctly', () => {
    const rawResponse = {
      evaluation_id: 'eval_test_123',
      filename: 'sample_resume.pdf',
      status: 'COMPLETED',
      version: '1.2.7',
      decision_engine: {
        overall_score: 75,
        policy_eligible: true,
        policy_flags: [],
        dimension_scores: {
          skill_match: { score: 80, confidence: 100, weight: 0.4, evidence: ['Matched 4 skills'] }
        },
        evidence_states: {
          MATCHED: ['Python', 'SQL', 'FastAPI'],
          INFERRED: [],
          MISSING: ['Docker'],
          CONTRADICTED: []
        },
        recommendation: {
          hiring_recommendation: 'Shortlist',
          recommendation_basis: {
            strengths: ['Strong API background'],
            weaknesses: [],
            critical_missing_skills: []
          }
        }
      }
    };

    const mapped = mapEvaluationResponse(rawResponse);

    expect(mapped.evaluationId).toBe('eval_test_123');
    expect(mapped.filename).toBe('sample_resume.pdf');
    expect(mapped.overallScore).toBe(75);
    expect(mapped.policyEligible).toBe(true);
    expect(mapped.backendVersion).toBe('1.2.7');
    expect(mapped.recommendation.tier).toBe('Shortlist');
    expect(mapped.evidenceStates.matched).toEqual(['Python', 'SQL', 'FastAPI']);
    expect(mapped.evidenceStates.missing).toEqual(['Docker']);
  });

  // Test 2: Missing optional fields defaults safely
  it('defaults safely when optional fields are missing', () => {
    const rawResponse = {
      evaluation_id: 'eval_minimal',
      decision_engine: {
        overall_score: 50
      }
    };

    const mapped = mapEvaluationResponse(rawResponse);

    expect(mapped.evaluationId).toBe('eval_minimal');
    expect(mapped.filename).toBe('resume.pdf');
    expect(mapped.overallScore).toBe(50);
    expect(mapped.evidenceStates.matched).toEqual([]);
    expect(mapped.evidenceStates.missing).toEqual([]);
    expect(mapped.dimensionScores).toEqual([]);
    expect(mapped.onboarding).toBeNull();
    expect(mapped.interview).toBeNull();
  });

  // Test 3: Invalid payload triggers schema validation warning/error
  it('handles null/invalid payloads gracefully via validation helper', () => {
    expect(validateEvaluationResponse(null)).toBe(false);
    expect(mapEvaluationResponse(null)).toBeNull();
  });

  // Test 4: Overall score normalization (54 -> 54, 0.54 -> 54)
  it('normalizes integer and float scores correctly', () => {
    expect(normalizeScore(54)).toBe(54);
    expect(normalizeScore(0.54)).toBe(54);
    expect(normalizeScore(1.0)).toBe(100);
    expect(normalizeScore(0)).toBe(0);
    expect(normalizeScore(null)).toBe(0);
  });

  // Test 5: Evidence states 1-to-1 matching
  it('preserves evidence states 1-to-1 without modification or synthetic text', () => {
    const states = {
      MATCHED: ['Python', 'SQL'],
      INFERRED: [],
      MISSING: ['TensorFlow', 'Qdrant'],
      CONTRADICTED: []
    };

    const normalized = normalizeEvidenceStates(states);

    expect(normalized.matched).toEqual(['Python', 'SQL']);
    expect(normalized.missing).toEqual(['TensorFlow', 'Qdrant']);
    expect(normalized.inferred).toEqual([]);
    expect(normalized.contradicted).toEqual([]);
  });

  // Test 6: Recommendation extraction is 1-to-1
  it('extracts hiring recommendation tier 1-to-1 from backend', () => {
    const rec = { hiring_recommendation: 'Reject' };
    const recBasis = { reasoning: 'Failed policy gate' };

    const normalized = normalizeRecommendation(rec, recBasis);

    expect(normalized.tier).toBe('Reject');
    expect(normalized.reasoning).toBe('Failed policy gate');
  });
});
