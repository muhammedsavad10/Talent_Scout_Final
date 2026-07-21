import requests
import json
import time
from reportlab.pdfgen import canvas
import io

def create_pdf(text):
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer)
    c.drawString(100, 750, text)
    c.save()
    buffer.seek(0)
    return buffer.read()

def test():
    files = [
        ("files", ("IDEAL.pdf", create_pdf("Name: Ideal Candidate\nI am a highly skilled engineer with 8 years of experience. My expertise includes Python, JavaScript, FastAPI, React, and Docker."), "application/pdf")),
        ("files", ("MISSING_MANDATORY.pdf", create_pdf("Name: Missing Mandatory\nExperienced developer with 5 years of experience building enterprise systems using Java and Spring."), "application/pdf")),
        ("files", ("JUNIOR.pdf", create_pdf("Name: Junior Candidate\nRecent graduate looking for a junior backend role. I have 2 years of experience working on university projects using Python."), "application/pdf")),
    ]
    data = {
        "job_description": "We need a senior backend developer with python and kubernetes.",
        "jd_skills": "python, kubernetes, fastapi"
    }

    res = requests.post("http://127.0.0.1:8000/api/v1/evaluate/batch", files=files, data=data)
    batch_id = res.json()["batch_id"]
    print("Batch ID:", batch_id)

    for _ in range(10):
        poll_res = requests.get(f"http://127.0.0.1:8000/api/v1/evaluate/batch/{batch_id}")
        status = poll_res.json()
        print(status["status"])
        if status["status"] in ["COMPLETED", "FAILED", "COMPLETED_WITH_ERRORS"]:
            print(json.dumps(status, indent=2))
            break
        time.sleep(1)

if __name__ == "__main__":
    test()
