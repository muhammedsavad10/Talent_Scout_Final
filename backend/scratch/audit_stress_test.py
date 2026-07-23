import os
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from fastapi.testclient import TestClient

# Add backend to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import app

client = TestClient(app)

import io
from reportlab.pdfgen import canvas

def create_pdf(text):
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer)
    c.drawString(100, 750, text)
    c.save()
    buffer.seek(0)
    return buffer.read()

def submit_eval(index):
    # Generates a unique text for parsing
    pdf_text = (
        f"Name: Candidate {index}\n"
        f"Email: candidate{index}@example.com\n"
        f"Education: Bachelor of Science, Computer Science University ({2010+index}-{2014+index})\n"
        f"Experience: Software Developer at TechCompany {index} (3 years)\n"
        f"Developed applications using Python and FastAPI in AWS.\n"
        f"Skills: Python, FastAPI"
    )
    pdf_data = create_pdf(pdf_text)
    files = {"file": (f"candidate_{index}.pdf", pdf_data, "application/pdf")}
    data = {
        "jd_text": "Looking for backend engineer with python skills.",
        "jd_skills": "Python, FastAPI"
    }
    
    start_time = time.time()
    try:
        response = client.post("/api/v1/evaluation/evaluate", files=files, data=data)
        latency = (time.time() - start_time) * 1000
        return index, response.status_code, latency, response.json().get("status")
    except Exception as e:
        latency = (time.time() - start_time) * 1000
        return index, 500, latency, str(e)

def run_stress_test():
    print("=" * 80)
    print("RUNNING CONCURRENT EVALUATION AND ASYNC STRESS TEST")
    print("=" * 80)
    
    concurrency_limit = 10
    print(f"\n[+] Spawning {concurrency_limit} concurrent evaluation requests via ThreadPoolExecutor...")
    
    latencies = []
    successes = 0
    failures = 0
    
    with ThreadPoolExecutor(max_workers=concurrency_limit) as executor:
        futures = [executor.submit(submit_eval, i) for i in range(concurrency_limit)]
        
        for f in futures:
            idx, code, lat, status = f.result()
            latencies.append(lat)
            print(f"   Candidate {idx:2d} | Status Code: {code} | Latency: {lat:7.2f} ms | Status: {status}")
            if code == 200:
                successes += 1
            else:
                failures += 1
                
    avg_latency = sum(latencies) / len(latencies)
    print(f"\n[+] Results:")
    print(f"    Successful Requests : {successes}")
    print(f"    Failed Requests     : {failures}")
    print(f"    Average Latency     : {avg_latency:.2f} ms")
    print(f"    Min Latency         : {min(latencies):.2f} ms")
    print(f"    Max Latency         : {max(latencies):.2f} ms")
    
    print("\n" + "=" * 80)
    print("CONCURRENT EVALUATION AND ASYNC STRESS TEST COMPLETED")
    print("=" * 80)

if __name__ == "__main__":
    run_stress_test()
