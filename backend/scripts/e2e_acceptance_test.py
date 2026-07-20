import sys
import os
import time
from fastapi.testclient import TestClient

# Add the parent directory to sys.path so we can import app
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import app
from app.services.evaluation_store import evaluation_store

client = TestClient(app)

def test_health():
    print("Testing / health check...")
    res = client.get("/")
    assert res.status_code == 200
    print("Health check passed.")

def test_batch_and_poll():
    print("Testing batch submission and polling...")
    
    # We create fake PDF files to submit. Since the stub parser uses filename, we use our golden keywords.
    files = [
        ("files", ("IDEAL.pdf", b"fake pdf data", "application/pdf")),
        ("files", ("MISSING_MANDATORY.pdf", b"fake pdf data", "application/pdf")),
        ("files", ("JUNIOR.pdf", b"fake pdf data", "application/pdf")),
    ]
    
    data = {
        "job_description": "We need a senior backend developer with python and kubernetes.",
        "jd_skills": "python, kubernetes, fastapi"
    }
    
    res = client.post("/api/v1/evaluate/batch", files=files, data=data)
    assert res.status_code == 200
    batch_id = res.json()["batch_id"]
    print(f"Batch submitted. ID: {batch_id}")
    
    # Poll until completed
    max_retries = 10
    for _ in range(max_retries):
        poll_res = client.get(f"/api/v1/evaluate/batch/{batch_id}")
        assert poll_res.status_code == 200
        status_data = poll_res.json()
        if status_data["status"] in ["COMPLETED", "FAILED", "COMPLETED_WITH_ERRORS"]:
            break
        time.sleep(1)
        
    assert status_data["status"] == "COMPLETED"
    assert status_data["completed"] == 3
    print("Batch completed successfully.")
    
    # Check comparison results
    ranked = status_data["results"]["ranked_candidates"]
    assert len(ranked) == 3
    print(f"Ranked candidates: {[r['filename'] for r in ranked]}")
    
    # Check that IDEAL is ranked better (lower rank number) than JUNIOR or MISSING_MANDATORY
    # Actually rank index 0 is best
    assert "IDEAL" in ranked[0]["filename"]
    
    # Test retrieving full evaluations for each
    for cand in ranked:
        eval_id = cand["evaluation_id"]
        eval_res = client.get(f"/api/v1/evaluation/status/{eval_id}")
        assert eval_res.status_code == 200
        eval_data = eval_res.json()
        assert eval_data["status"] == "COMPLETED"
        assert "result" in eval_data
        print(f"Verified full evaluation retrieval for {cand['filename']}")
        
    print("Batch and polling test passed.")

if __name__ == "__main__":
    t0 = time.time()
    try:
        # Trigger startup events
        with client:
            test_health()
            test_batch_and_poll()
    except Exception as e:
        print(f"Acceptance test failed: {e}")
        sys.exit(1)
        
    t1 = time.time()
    print(f"\nAll tests passed successfully in {t1 - t0:.2f}s!")
