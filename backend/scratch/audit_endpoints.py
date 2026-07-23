import os
import sys
import io
from fastapi.testclient import TestClient
from reportlab.pdfgen import canvas

# Add backend to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import app

client = TestClient(app)

def create_pdf(text, size_bytes=0):
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer)
    c.drawString(100, 750, text)
    c.save()
    buffer.seek(0)
    data = buffer.read()
    if size_bytes > len(data):
        data += b"0" * (size_bytes - len(data))
    return data

def run_audit():
    print("=" * 80)
    print("RUNNING ENDPOINT FUZZING & API CONTRACT AUDIT")
    print("=" * 80)
    
    # 1. Health Checks
    print("\n[+] Testing GET / health check...")
    res = client.get("/")
    print(f"Status Code: {res.status_code} | Body: {res.json()}")
    assert res.status_code == 200
    
    print("\n[+] Testing GET /health/databases check...")
    res = client.get("/health/databases")
    print(f"Status Code: {res.status_code} | Body: {res.json()}")
    # May fail if local connection is degraded, but TestClient handles it
    
    # 2. CORS check
    print("\n[+] Testing CORS headers on GET /...")
    res = client.get("/", headers={"Origin": "http://localhost:3000"})
    origin_header = res.headers.get('access-control-allow-origin')
    print(f"CORS Headers: Access-Control-Allow-Origin = {origin_header}")
    assert origin_header in ("*", "http://localhost:3000")
    
    # 3. Ingestion upload endpoint fuzzer
    print("\n[+] Testing Ingestion Upload Fuzzing (/api/v1/ingestion/upload)...")
    
    # 3a. Non-PDF upload
    print("   - Uploading txt file (expecting 400)...")
    res = client.post("/api/v1/ingestion/upload", files={"file": ("test.txt", b"plain text", "text/plain")})
    print(f"     Status Code: {res.status_code} | Detail: {res.json().get('detail')}")
    assert res.status_code == 400
    
    # 3b. Oversized upload > 5MB
    print("   - Uploading oversized PDF > 5MB (expecting 413)...")
    oversized_pdf = create_pdf("Huge File Content", 6 * 1024 * 1024)
    res = client.post("/api/v1/ingestion/upload", files={"file": ("oversized.pdf", oversized_pdf, "application/pdf")})
    print(f"     Status Code: {res.status_code} | Detail: {res.json().get('detail')}")
    assert res.status_code == 413
    
    # 3c. Non-genuine PDF (wrong magic bytes)
    print("   - Uploading non-genuine PDF without %PDF header (expecting 415)...")
    res = client.post("/api/v1/ingestion/upload", files={"file": ("fake.pdf", b"NOT-A-PDF", "application/pdf")})
    print(f"     Status Code: {res.status_code} | Detail: {res.json().get('detail')}")
    assert res.status_code == 415

    # 4. Evaluation endpoint validation
    print("\n[+] Testing Evaluation Validation (/api/v1/evaluation/evaluate)...")
    
    # 4a. Missing payload keys
    print("   - Posting with missing Form parameters (expecting 422)...")
    pdf_data = create_pdf("%PDF-1.4 header\nMuhammed Sajad\nPython Developer")
    res = client.post("/api/v1/evaluation/evaluate", files={"file": ("resume.pdf", pdf_data, "application/pdf")}, data={})
    print(f"     Status Code: {res.status_code} | JSON: {res.json().get('detail')}")
    assert res.status_code == 422
    
    # 4b. Valid evaluation and schema match
    print("   - Posting valid evaluation request (expecting 200)...")
    pdf_content = (
        "%PDF-1.4 header\n"
        "Muhammed Sajad\n"
        "Email: sajad@example.com\n"
        "Education: Bachelor of Science in Computer Science, KTU University (2018-2022)\n"
        "Experience:\n"
        "Software Engineer at TechCorp (2022-2024)\n"
        "Developed backend APIs using FastAPI and Python in a cloud environment.\n"
        "Skills: Python, FastAPI, Docker, PostgreSQL"
    )
    pdf_data = create_pdf(pdf_content)
    jd_text = "Backend engineer with Python experience."
    jd_skills = "Python, FastAPI"
    res = client.post(
        "/api/v1/evaluation/evaluate", 
        files={"file": ("resume.pdf", pdf_data, "application/pdf")}, 
        data={"jd_text": jd_text, "jd_skills": jd_skills}
    )
    print(f"     Status Code: {res.status_code}")
    assert res.status_code == 200
    eval_res = res.json()
    print("     Verifying keys in response:")
    for k in ["evaluation_id", "filename", "status", "result"]:
        print(f"       Contains '{k}': {k in eval_res}")
        assert k in eval_res
    print(f"     Evaluation Status: {eval_res['status']}")
    
    # 5. Batch endpoints
    print("\n[+] Testing Batch Submission and Status (/api/v1/evaluate/batch)...")
    files = [
        ("files", ("resume_1.pdf", pdf_data, "application/pdf")),
        ("files", ("resume_2.pdf", pdf_data, "application/pdf"))
    ]
    res = client.post(
        "/api/v1/evaluate/batch",
        files=files,
        data={"job_description": "Need developer", "jd_skills": "Python"}
    )
    print(f"     Batch Post Status Code: {res.status_code} | Response: {res.json()}")
    assert res.status_code == 200
    batch_id = res.json()["batch_id"]
    
    # Check status
    res = client.get(f"/api/v1/evaluate/batch/{batch_id}")
    print(f"     Batch Get Status Code: {res.status_code} | Status: {res.json().get('status')}")
    assert res.status_code == 200
    
    print("\n" + "=" * 80)
    print("ENDPOINT FUZZING & API CONTRACT AUDIT COMPLETED")
    print("=" * 80)

if __name__ == "__main__":
    run_audit()
