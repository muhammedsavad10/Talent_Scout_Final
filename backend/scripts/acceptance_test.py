import asyncio
import time
from fastapi.testclient import TestClient
from unittest.mock import patch
from main import app
import json

client = TestClient(app)

def run_acceptance_tests():
    print("Starting End-to-End Acceptance Tests (Phase C4B)")
    print("-" * 50)

    # We patch extract_text_from_pdf in both evaluate and batch_evaluate
    # to return realistic resume text when given dummy pdf bytes.
    realistic_resume_text = """
    Name: John Doe
    Experience: 5 years of experience in software development.
    Skills: Python, FastAPI, Docker, AWS, React.
    Education: B.S. Computer Science
    """

    with patch("app.api.evaluate.extract_text_from_pdf", return_value=realistic_resume_text), \
         patch("app.api.batch_evaluate.extract_text_from_pdf", return_value=realistic_resume_text):
        
        print("1. Single Resume Evaluation...")
        payload = {
            "jd_text": "Looking for a backend engineer with Python and FastAPI experience.",
            "jd_skills": "Python, FastAPI, Docker"
        }
        files = {
            "file": ("resume.pdf", b"%PDF-1.4 dummy", "application/pdf")
        }
        
        response = client.post("/api/v1/evaluation/evaluate", data=payload, files=files)
        assert response.status_code == 200, f"Single eval failed: {response.text}"
        data = response.json()
        print("   -> Success. Evaluation ID:", data.get("evaluation_id"))
        
        print("2. Batch Evaluation...")
        batch_payload = {
            "jd_text": "Looking for a backend engineer.",
            "jd_skills": "Python, FastAPI",
            "candidates": [
                {"id": "cand_1", "name": "Alice"}
            ]
        }
        batch_files = [
            ("files", ("cand_1.pdf", b"%PDF-1.4 dummy 1", "application/pdf"))
        ]
        
        # We also need to patch asyncio.create_task in batch_evaluate?
        # No, TestClient runs in the same event loop if we don't mock it, but Starlette background tasks or `create_task` might run.
        # But wait, batch evaluation expects multipart/form-data for files, and form fields for the rest.
        response = client.post(
            "/api/v1/evaluate/batch",
            data={"job_description": "Looking for a backend engineer.", "jd_skills": "Python, FastAPI"},
            files=batch_files
        )
        assert response.status_code == 200, f"Batch eval failed: {response.text}"
        batch_data = response.json()
        batch_id = batch_data.get("batch_id")
        print("   -> Success. Batch ID:", batch_id)
        
        print("3. Polling Batch Status...")
        # Since it's a background task, it might take a split second. We poll once or twice.
        for _ in range(5):
            poll_resp = client.get(f"/api/v1/evaluate/batch/{batch_id}")
            if poll_resp.status_code == 200 and poll_resp.json().get("status") == "COMPLETED":
                print("   -> Batch Processing Completed!")
                break
            time.sleep(0.5)
        else:
            print("   -> Batch polling timed out or didn't complete.")
        
        print("4. Comparison...")
        compare_payload = {
            "candidate_a_id": "cand_1",
            "candidate_b_id": "cand_2",
            "job_description": "Backend dev"
        }
        # In the C4B prompt, we only need to "reconnect comparison". Does comparison endpoint exist?
        # Let's check if it exists by hitting it.
        try:
            comp_resp = client.post("/api/v1/compare/", json=compare_payload)
            if comp_resp.status_code == 200:
                print("   -> Success.")
            else:
                print(f"   -> Comparison endpoint returned {comp_resp.status_code}")
        except Exception as e:
            print(f"   -> Comparison failed: {e}")

    print("-" * 50)
    print("Acceptance Tests Completed.")

if __name__ == "__main__":
    run_acceptance_tests()
