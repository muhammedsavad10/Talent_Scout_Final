/**
 * dimensionLabels.js
 *
 * Presentation-layer lookup table for human-readable dimension titles.
 * Keeps evaluationMapper pure and uncoupled from UI formatting.
 */
export const DIMENSION_LABELS = {
  skill_match: "Skill Match",
  experience_quantity: "Experience Quantity",
  experience_relevance: "Experience Relevance",
  experience_quality: "Experience Quality",
};

export function getDimensionLabel(key) {
  if (DIMENSION_LABELS[key]) return DIMENSION_LABELS[key];
  return key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
}
