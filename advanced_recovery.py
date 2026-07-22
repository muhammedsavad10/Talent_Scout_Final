import os
import json
import shutil
from pathlib import Path
from urllib.parse import unquote

appdata = os.environ.get('APPDATA')
history_dir = Path(appdata) / 'Code' / 'User' / 'History'
workspace_dir = Path('c:/Users/Muhammed Savad T M/Desktop/Brototype/FINAL PROJECT/talent_scout_enterprise')

# List of deleted paths (relative to workspace_dir)
deleted_files = [
    "backend/app/agents/comparator.py",
    "backend/app/agents/decision_engine.py",
    "backend/app/agents/deterministic_extractor.py",
    "backend/app/agents/normalization.py",
    "backend/app/agents/orchestrator.py",
    "backend/app/agents/parser_validation.py",
    "backend/app/agents/policy_engine.py",
    "backend/app/agents/scorer.py",
    "backend/app/agents/scout.py",
    "backend/app/agents/strategy.py",
    "backend/app/api/batch_evaluate.py",
    "backend/app/api/evaluate.py",
    "backend/app/core/config.py",
    "backend/app/ontology.py",
    "backend/app/services/cache_service.py",
    "backend/app/services/evaluation_store.py",
    "backend/capture_baselines.py",
    "backend/capture_baselines_api.py",
    "backend/debug_eval.py",
    "backend/demo_swarm.py",
    "backend/detailed_profiler.py",
    "backend/generate_test_pdf.py",
    "backend/live_eval.py",
    "backend/profiler.py",
    "backend/test_api.py",
    "backend/test_api_client.py",
    "backend/test_multi_provider.py",
    "backend/test_parse.py",
    "backend/test_parse2.py",
    "backend/test_parse3.py",
    "backend/test_scorer_crash.py",
    "backend/tests/calibration_dataset.py",
    "backend/tests/e2e_ui_test.py",
    "backend/tests/run_real_resumes.py",
    "backend/tests/simulate_trace.py",
    "backend/tests/test_batch_api.py",
    "backend/tests/test_batch_rate_limits.py",
    "backend/tests/test_benchmarks.py",
    "backend/tests/test_comparator.py",
    "backend/tests/test_decision_engine_advanced.py",
    "backend/tests/test_evaluate.py",
    "backend/tests/test_evaluation_intelligence.py",
    "backend/tests/test_experience_realism_run.py",
    "backend/tests/test_final_optimizations.py",
    "backend/tests/test_ingestion_repair.py",
    "backend/tests/test_orchestrator.py",
    "backend/tests/test_parser_production.py",
    "backend/tests/test_partial_success_regression.py",
    "backend/tests/test_phase_2.py",
    "backend/tests/test_pipeline_e2e.py",
    "backend/tests/test_policy_engine.py",
    "backend/tests/test_regression.py",
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

print(f"Searching in {history_dir} for missing files...")
found_count = 0

for entry_dir in history_dir.iterdir():
    if not entry_dir.is_dir(): continue
    entries_file = entry_dir / 'entries.json'
    if not entries_file.exists(): continue
    
    try:
        with open(entries_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        resource = data.get('resource', '')
        decoded_path = unquote(resource)
        # normalize slashes
        decoded_path = decoded_path.replace('\\', '/')
        
        for relative_path in deleted_files:
            if relative_path in decoded_path:
                dest_file = workspace_dir / relative_path
                if dest_file.exists():
                    continue # already restored
                
                entries = data.get('entries', [])
                if not entries: continue
                
                # Get the most recent entry
                last_entry = entries[-1]
                source_file = entry_dir / last_entry['id']
                
                if source_file.exists():
                    dest_file.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(source_file, dest_file)
                    print(f"Restored: {relative_path}")
                    found_count += 1
                
    except Exception as e:
        pass

print(f"Total files restored: {found_count}")
