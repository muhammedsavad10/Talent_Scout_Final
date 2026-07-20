# TalentScout Enterprise - Reconstruction Assumptions & Notes

## Phase A: Backend Startup
*   **Missing Dependencies**: Replaced missing `sentence-transformers` instantiation with a safe fallback `DummyEmbeddingModel` when `DEVELOPMENT_MODE=True`, so the backend can start in constrained environments without crashing.
*   **Orchestrator Import**: Added a minimal stub for `run_evaluation_pipeline` because `evaluate.py` directly imports it, preventing a successful FastApi boot.

## Phase B: Services
*   **EvaluationStore / CacheService Interfaces**: The specific database interaction logic from Phase 5 was permanently lost due to a `git clean -fdx` wiping untracked files. Stubs were implemented exposing generic CRUD signatures (save/get evaluations and batches) compatible with standard Supabase/Dict tracking.
*   **Configuration**: Re-linked `evaluation_store.py` to the surviving `supabase_db` client.

## Phase C1: Foundation
*   **Ontology Configuration Missing**: Due to missing YAML configs, we implemented an in-memory `DEFAULT_ALIASES` dict as a fallback for alias resolution (e.g. `fast-api` -> `FastAPI`).
*   **Parser Validation**: Schemas are rigorously mapped to the surviving `schemas.py::ParserValidationReport`. Validation logic applies basic deterministic existence checks for standard sections (education, experience, skills).

## Phase C2: Scoring & Comparator
*   **Dimensional Weights:** Hardcoded in `scorer.py` as `skill_match` (0.40), `experience_quantity` (0.20), `experience_relevance` (0.25), and `experience_quality` (0.15) due to missing `weights.yaml`.
*   **Comparator Fallbacks:** Comparator was built to defensively extract fields using a `safe_get` helper so that both legacy dicts and pydantic models map to rankable Candidate rows.

## Phase C3: Decision Layer
*   **Policy Engine Config Missing:** Implemented a fallback `DEFAULT_POLICY_CONFIG` in `policy_engine.py` mimicking a hypothetical `hiring_policy.yaml`. It enforces minimum scores (overall >= 60, skill >= 50) and critical skill validation.
*   **Strategy Tiers:** Hardcoded logic mapped to 5 tiers: Strong Hire, Hire, Interview, Hold, Reject based on Policy Engine boolean flags and Score bands.
