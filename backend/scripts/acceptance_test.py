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

    realistic_resume_text = """
    Name: John Doe
    Experience: 5 years of experience in software development.
    Skills: Python, FastAPI, Docker, AWS, React.
    Education: B.S. Computer Science
    """

    with patch("app.api.evaluate.extract_text_from_pdf", return_value=realistic_resume_text), \
         patch("app.api.batch_evaluate.extract_text_from_pdf", return_value=realistic_resume_text):
        
        print("\n--- 1. Single Resume Evaluation ---")
        pdf_bytes = b"%PDF-1.4 dummy"
        
        print("HTTP POST /api/v1/evaluation/evaluate")
        print("Request Data: {'jd_text': 'Need a backend developer.', 'jd_skills': 'Python, API'}")
        response = client.post(
            "/api/v1/evaluation/evaluate",
            data={"jd_text": "Need a backend developer.", "jd_skills": "Python, API"},
            files={"file": ("resume.pdf", pdf_bytes, "application/pdf")}
        )
        assert response.status_code == 200, f"Single eval failed: {response.text}"
        result = response.json()
        print(f"Response Code: {response.status_code}")
        print(f"Response Body: {json.dumps(result, indent=2)}")
        eval_id = result.get("evaluation_id")
        
        print("\n--- 2. Batch Evaluation ---")
        batch_files = []
        for i in range(2):
            batch_files.append(
                ("files", (f"resume_{i}.pdf", pdf_bytes, "application/pdf"))
            )
        
        print("HTTP POST /api/v1/evaluate/batch")
        print("Request Data: {'job_description': 'Looking for a backend engineer.', 'jd_skills': 'Python, FastAPI'}")
        response = client.post(
            "/api/v1/evaluate/batch",
            data={"job_description": "Looking for a backend engineer.", "jd_skills": "Python, FastAPI"},
            files=batch_files
        )
        assert response.status_code == 200, f"Batch eval failed: {response.text}"
        batch_data = response.json()
        print(f"Response Code: {response.status_code}")
        print(f"Response Body: {json.dumps(batch_data, indent=2)}")
        batch_id = batch_data.get("batch_id")
        
        print("\n--- 3. Polling Batch Status & Comparison ---")
        max_retries = 10
        print(f"HTTP GET /api/v1/evaluate/batch/{batch_id}")
        for i in range(max_retries):
            response = client.get(f"/api/v1/evaluate/batch/{batch_id}")
            status_data = response.json()
            if status_data.get("status") in ["COMPLETED", "FAILED", "COMPLETED_WITH_ERRORS"]:
                print(f"Response Code: {response.status_code}")
                print(f"Response Body: {json.dumps(status_data, indent=2)}")
                break
            time.sleep(0.5)
        else:
            print("   -> Batch Processing did not complete in time.")
            
    print("-" * 50)
    print("Acceptance Tests Completed.")

if __name__ == "__main__":
    run_acceptance_tests()
