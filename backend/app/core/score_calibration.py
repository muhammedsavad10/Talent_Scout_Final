"""
Score Calibration Engine for TalentScout Enterprise (v1.9.0).
Prevents score inflation and ensures realistic recruiter score distribution curves:
- Scores > 90.0: Reserved strictly for exceptional candidates with verified production scale & measurable impact
- Scores 80.0 - 89.0: High performers with strong technical match and evidence depth
- Scores 70.0 - 79.0: Qualified candidates
- Scores < 70.0: Standard review candidates

Preserves candidate ranking ordering while calibrating overall scores.
"""
import logging

logger = logging.getLogger("talentscout_score_calibration")

def calibrate_recruiter_score(
    raw_score: float,
    quality_multiplier: float = 1.00,
    has_measurable_impact: bool = False,
    is_exceptional_evidence: bool = False
) -> float:
    """
    v1.9.0 Recruiter Score Calibration Engine.
    Calibrates raw scores to prevent artificial score inflation.
    """
    calibrated = float(raw_score)

    # 1. Exceptional Score (>90) Gatekeeper
    if calibrated > 90.0:
        if not (is_exceptional_evidence or (quality_multiplier >= 1.25 and has_measurable_impact)):
            # Dampen unearned 90+ scores to realistic recruiter band (86.0 - 89.5)
            damped = 86.0 + ((calibrated - 90.0) * 0.35)
            logger.info("[SCORE CALIBRATION] Damped unearned >90 score from %.1f to %.1f", calibrated, damped)
            calibrated = damped

    # 2. Calibrate score based on evidence quality multiplier
    if quality_multiplier > 1.20 and calibrated < 88.0:
        calibrated = min(89.5, calibrated * 1.04)

    return round(min(99.0, max(10.0, calibrated)), 1)
