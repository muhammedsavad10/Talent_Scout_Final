import os
import json
import subprocess
from pathlib import Path

deleted_files = [
    'backend/app/agents/comparator.py',
    'backend/app/agents/decision_engine.py',
    'backend/app/agents/deterministic_extractor.py',
    'backend/app/agents/normalization.py',
    'backend/app/agents/orchestrator.py',
    'backend/app/agents/parser_validation.py',
    'backend/app/agents/policy_engine.py',
    'backend/app/agents/scorer.py',
    'backend/app/agents/scout.py',
    'backend/app/agents/strategy.py',
    'backend/app/api/batch_evaluate.py',
    'backend/app/api/evaluate.py',
    'backend/app/core/config.py',
    'backend/app/ontology.py',
    'backend/app/services/cache_service.py',
    'backend/app/services/evaluation_store.py',
    'backend/capture_baselines.py',
    'backend/capture_baselines_api.py',
    'backend/debug_eval.py',
    'backend/demo_swarm.py',
    'backend/detailed_profiler.py',
    'backend/generate_test_pdf.py',
    'backend/live_eval.py',
    'backend/profiler.py',
    'backend/test_api.py',
    'backend/test_api_client.py',
    'backend/test_multi_provider.py',
    'backend/test_parse.py',
    'backend/test_parse2.py',
    'backend/test_parse3.py',
    'backend/test_scorer_crash.py',
    'backend/tests/calibration_dataset.py',
    'backend/tests/e2e_ui_test.py',
    'backend/tests/run_real_resumes.py',
    'backend/tests/simulate_trace.py',
    'backend/tests/test_batch_api.py',
    'backend/tests/test_batch_rate_limits.py',
    'backend/tests/test_benchmarks.py',
    'backend/tests/test_comparator.py',
    'backend/tests/test_decision_engine_advanced.py',
    'backend/tests/test_evaluate.py',
    'backend/tests/test_evaluation_intelligence.py',
    'backend/tests/test_experience_realism_run.py',
    'backend/tests/test_final_optimizations.py',
    'backend/tests/test_ingestion_repair.py',
    'backend/tests/test_orchestrator.py',
    'backend/tests/test_parser_production.py',
    'backend/tests/test_partial_success_regression.py',
    'backend/tests/test_phase_2.py',
    'backend/tests/test_pipeline_e2e.py',
    'backend/tests/test_policy_engine.py',
    'backend/tests/test_regression.py',
    "backend/tests/test_regression_datasets.py",
    "backend/tests/test_response_validation.py",
    "backend/tests/test_route_contract.py",
    "backend/tests/test_scorer.py",
    "backend/tests/test_scout.py",
    "backend/tests/test_skill_matching_pipeline.py",
    "backend/tests/test_strategy.py",
    "backend/trace_full_view.py",
    "backend/trace_script.py"
]

results = []
for f in deleted_files:
    path = Path(f)
    if path.exists():
        stat = path.stat()
        tracked = False
        try:
            output = subprocess.check_output(['git', 'ls-files', f], text=True).strip()
            if output:
                tracked = True
        except:
            pass
        results.append({'file': f, 'exists': True, 'size': stat.st_size, 'modified': stat.st_mtime, 'tracked': tracked})
    else:
        results.append({'file': f, 'exists': False, 'tracked': False})

with open('rescan_results.json', 'w') as out:
    json.dump(results, out)
