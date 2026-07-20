# TalentScout API Reconstruction Notes (Phase C4B)

## Final Assumptions
- The internal evaluation logic remains entirely asynchronous via LangGraph.
- Resume text extraction and scoring logic has been fully decoupled from the HTTP transport layer, utilizing the robust internal background task approach.
- Single node embeddings (`DummyEmbeddingModel`) and regex-based LLM stubs have been intentionally introduced as stable placeholders to isolate testing to the pipeline structure without external HTTP failures.

## Technical Debt
- `EvaluationStore` singleton relies on in-memory dictionary storage. All batch and evaluation records vanish upon API restart.
- Supabase configuration is loaded and initialized, but `talentscout_db` endpoints mock operations instead of executing SQL.
- `DummyEmbeddingModel` returns arbitrary vectors, rendering vector similarity searches non-functional.

## Deviations from Original Architecture
- The pipeline execution was heavily centralized into `run_evaluation_pipeline` from `batch_evaluate.py` to prevent logic duplication. Comparison is inherently tied to the batch endpoint now, replacing the need for an external `/compare` route in this phase.
- We added `sys.path` workarounds in our `conftest.py` and acceptance scripts since the `main.py` entrypoint wasn't natively in the module scope for `tests/`.

## Production Readiness
This state represents a structurally complete but synthetically intelligent system. The next phase (Phase 5 Completion) MUST implement:
1. Real Groq Llama 3 parsing.
2. Real SentenceTransformers embeddings (`all-MiniLM-L6-v2`) integrated with Qdrant.
3. Supabase data persistence.
