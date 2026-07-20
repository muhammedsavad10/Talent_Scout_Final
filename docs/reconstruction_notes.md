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
*(To be populated as work progresses)*
