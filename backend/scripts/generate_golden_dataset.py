import asyncio
import json
import time
import os
import sys

# Ensure backend directory is in path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.agents.orchestrator import run_evaluation_pipeline

RESUMES = {
    "ideal": "Name: Ideal Candidate\nI am a highly skilled engineer with 8 years of experience. My expertise includes Python, JavaScript, FastAPI, React, and Docker. Education: B.S. Computer Science.",
    "missing_mandatory": "Name: Missing Mandatory\nExperienced developer with 5 years of experience building enterprise systems using Java and Spring. Education: B.S. Computer Science.",
    "junior": "Name: Junior Candidate\nRecent graduate looking for a junior backend role. I have 2 years of experience working on university projects using Python. Education: B.S. Computer Science.",
    "duplicate": "Name: Duplicate Candidate\nI know Python python and PYTHON. I also know fast-api and FastAPI. I have 4 years of experience.",
    "malformed": "",
    "strong_missing_preferred": "Name: Strong Default\nStrong engineer with 6 years of experience in backend development. Skilled in Python and Django. Education: B.S. Computer Science."
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
