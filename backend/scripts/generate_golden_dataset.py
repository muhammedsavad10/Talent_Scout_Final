import asyncio
import json
import time
import os
import sys

# Ensure backend directory is in path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.agents.orchestrator import run_evaluation_pipeline

RESUMES = {
    "ideal": "This is an IDEAL candidate resume text. Contact candidate@example.com.",
    "missing_mandatory": "This is a MISSING_MANDATORY candidate text.",
    "junior": "This is a JUNIOR candidate.",
    "duplicate": "This DUPLICATE candidate text has Python python and PYTHON.",
    "malformed": "MALFORMED resume binary data.",
    "strong_missing_preferred": "I am a strong candidate with Django but missing preferred."
}
REQUIRED_SKILLS = ["Python", "FastAPI"]

async def main():
    print("Generating Golden Dataset...")
    results = {}
    
    start_time = time.time()
    
    for case, text in RESUMES.items():
        print(f"Running pipeline for {case}...")
        t0 = time.time()
        result = await run_evaluation_pipeline(text, f"id_{case}", required_skills=REQUIRED_SKILLS)
        t1 = time.time()
        
        # Capture metrics
        result["_metrics"] = {
            "execution_time_ms": round((t1 - t0) * 1000, 2)
        }
        results[case] = result
        
    total_time = time.time() - start_time
    try:
        import psutil
        process = psutil.Process(os.getpid())
        memory_info = f"{process.memory_info().rss / 1024 / 1024:.2f} MB"
    except ImportError:
        memory_info = "Unknown (psutil not installed)"
    
    print(f"\nCompleted in {total_time:.2f}s")
    print(f"Memory Footprint: {memory_info}")
    
    os.makedirs("tests/fixtures", exist_ok=True)
    with open("tests/fixtures/golden_dataset.json", "w") as f:
        json.dump(results, f, indent=2, default=str)
        
    print("Saved to tests/fixtures/golden_dataset.json")

if __name__ == "__main__":
    asyncio.run(main())
