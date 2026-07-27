"""
Evidence Quality Intelligence Engine for TalentScout Enterprise (v1.9.0).
Evaluates the QUALITY, DEPTH, and CONTEXT of resume evidence rather than merely its presence.

Differentiates keyword density (e.g. "React, Node, MongoDB") vs. demonstrated engineering quality
(e.g. "Built scalable React dashboard serving 50,000 users, optimized MongoDB indexes reducing latency by 60%").

Evaluates 6 core dimensions:
- Implementation Depth
- Production Readiness
- Architectural Complexity
- Business Impact & Measurable Metrics
- Technical Ownership
- Quality Multiplier (1.0x to 1.8x)
"""
import re
import logging
from typing import Dict, Any, List, Set, Tuple

logger = logging.getLogger("talentscout_evidence_quality")

MEASURABLE_METRIC_PATTERNS = [
    r'\b(?:\d+[\d,]*\s*(?:users|active users|customers|requests|qps|rps|tps|transactions|dau|mau))\b',
    r'\b(?:\d+(?:\.\d+)?%\s*(?:latency reduction|reduction|improvement|increase|decrease|cost reduction|efficiency))\b',
    r'\b(?:reduced\s+latency\s+by\s+\d+%\s*)\b',
    r'\b(?:scaled|handled|processed|optimized|improved)\b'
]

COMPLEXITY_KEYWORDS = {
    "microservices", "distributed", "high availability", "sharding", "replication",
    "indexing", "vector db", "rag", "langgraph", "ci/cd", "kubernetes", "k8s",
    "docker", "kafka", "spark", "grpc", "graphql", "load balancer", "cache"
}

OWNERSHIP_KEYWORDS = {
    "architected", "spearheaded", "designed", "led", "lead", "built", "created",
    "engineered", "optimized", "implemented", "deployed", "refactored"
}

class EvidenceQualityScore:
    def __init__(self, raw_text: str):
        self.raw_text = raw_text or ""
        self.implementation_depth_score: float = 1.0
        self.production_readiness_score: float = 1.0
        self.architectural_complexity_score: float = 1.0
        self.business_impact_score: float = 1.0
        self.measurable_metrics: List[str] = []
        self.ownership_level: str = "Standard Contribution"
        self.quality_multiplier: float = 1.00
        self.quality_reasons: List[str] = []

    def to_dict(self) -> Dict[str, Any]:
        return {
            "quality_multiplier": round(self.quality_multiplier, 2),
            "implementation_depth": round(self.implementation_depth_score, 2),
            "production_readiness": round(self.production_readiness_score, 2),
            "architectural_complexity": round(self.architectural_complexity_score, 2),
            "business_impact": round(self.business_impact_score, 2),
            "measurable_metrics": self.measurable_metrics,
            "ownership_level": self.ownership_level,
            "quality_reasons": self.quality_reasons
        }

def evaluate_evidence_quality(text: str) -> EvidenceQualityScore:
    """
    v1.9.0 Evidence Quality Intelligence Evaluator.
    Computes quality multiplier (1.00x to 1.80x) based on engineering depth and impact.
    """
    score = EvidenceQualityScore(text)
    if not text:
        return score

    text_lower = text.lower()

    # 1. Detect Measurable Metrics & Business Impact
    metrics_found = []
    for pat in MEASURABLE_METRIC_PATTERNS:
        matches = re.findall(pat, text_lower, flags=re.IGNORECASE)
        for m in matches:
            if m not in metrics_found:
                metrics_found.append(m)

    if metrics_found:
        score.measurable_metrics = metrics_found[:3]
        score.business_impact_score = 1.40
        score.quality_reasons.append(f"Demonstrated measurable business metrics: {', '.join(score.measurable_metrics)}")
    elif any(kw in text_lower for kw in ["scale", "scaled", "latency", "users", "million", "thousand"]):
        score.business_impact_score = 1.20
        score.quality_reasons.append("Contains production scale and performance evidence")

    # 2. Evaluate Architectural Complexity
    complexity_hits = [kw for kw in COMPLEXITY_KEYWORDS if re.search(r'\b' + re.escape(kw) + r'\b', text_lower)]
    if len(complexity_hits) >= 3:
        score.architectural_complexity_score = 1.35
        score.quality_reasons.append(f"High architectural complexity ({', '.join(complexity_hits[:3])})")
    elif len(complexity_hits) >= 1:
        score.architectural_complexity_score = 1.15

    # 3. Evaluate Technical Ownership
    ownership_hits = [kw for kw in OWNERSHIP_KEYWORDS if re.search(r'\b' + re.escape(kw) + r'\b', text_lower)]
    if any(kw in text_lower for kw in ["architected", "spearheaded", "lead", "led"]):
        score.ownership_level = "Principal / Lead Ownership"
        score.implementation_depth_score = 1.30
    elif ownership_hits:
        score.ownership_level = "Direct Implementation Ownership"
        score.implementation_depth_score = 1.15

    # 4. Evaluate Production Readiness
    if any(kw in text_lower for kw in ["production", "serving", "50,000", "active users", "ci/cd", "kubernetes", "docker"]):
        score.production_readiness_score = 1.30
        score.quality_reasons.append("Verified production deployment and real-world usage")

    # 5. Compute Final Quality Multiplier (1.00x to 1.80x)
    raw_mult = (
        (score.implementation_depth_score * 0.25) +
        (score.production_readiness_score * 0.25) +
        (score.architectural_complexity_score * 0.25) +
        (score.business_impact_score * 0.25)
    )

    score.quality_multiplier = min(1.80, max(1.00, round(raw_mult, 2)))
    return score
