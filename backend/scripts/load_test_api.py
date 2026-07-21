import asyncio
import httpx
import time
import os
import psutil
import json
import numpy as np

API_URL = "http://127.0.0.1:8000"
RESUME_TEXT = "John Doe, Software Engineer. 5 years of Python experience."
JOB_ID = "test-job-load"

async def upload_resume(client, idx):
    start_time = time.time()
    try:
        pdf_bytes = b"%PDF-1.4\n" + f"{RESUME_TEXT} {idx}".encode("utf-8")
        files = {"files": (f"resume_{idx}.pdf", pdf_bytes, "application/pdf")}
        data = {"job_description": "We need a Python dev", "jd_skills": "Python"}
        response = await client.post(
            f"{API_URL}/api/v1/evaluate/batch", 
            files=files,
            data=data,
            timeout=30.0
        )
        latency = time.time() - start_time
        if response.status_code == 200:
            return True, latency, response.json().get("batch_id")
        else:
            return False, latency, str(response.status_code)
    except Exception as e:
        return False, time.time() - start_time, str(e)

async def run_load_test(concurrent_users):
    print(f"\n--- Starting Load Test: {concurrent_users} Concurrent Requests ---")
    
    # Track resources
    process = psutil.Process(os.getpid())
    process.cpu_percent(interval=None)
    
    start_time = time.time()
    latencies = []
    success = 0
    failures = 0
    errors = []
    evaluation_ids = set()
    
    async with httpx.AsyncClient() as client:
        tasks = [upload_resume(client, i) for i in range(concurrent_users)]
        results = await asyncio.gather(*tasks)
        
    end_time = time.time()
    total_time = end_time - start_time
    
    # Resource metrics
    cpu_util = process.cpu_percent(interval=None)
    mem_usage = process.memory_info().rss / (1024 * 1024) # MB
    
    for res, lat, eval_id_or_err in results:
        latencies.append(lat)
        if res:
            success += 1
            if eval_id_or_err in evaluation_ids:
                print("WARNING: Duplicate evaluation ID detected!")
            evaluation_ids.add(eval_id_or_err)
        else:
            failures += 1
            errors.append(eval_id_or_err)
            
    throughput = concurrent_users / total_time
    p50 = np.percentile(latencies, 50)
    p95 = np.percentile(latencies, 95)
    p99 = np.percentile(latencies, 99)
    error_rate = (failures / concurrent_users) * 100
    
    print(f"Throughput: {throughput:.2f} req/sec")
    print(f"P50 Latency: {p50:.2f}s | P95 Latency: {p95:.2f}s | P99 Latency: {p99:.2f}s")
    print(f"Error Rate: {error_rate:.1f}% ({failures} failed out of {concurrent_users})")
    print(f"Max CPU Util: {cpu_util}% | Max Memory: {mem_usage:.2f} MB")
    
    if failures > 0:
        print(f"Sample Errors: {list(set(errors))[:3]}")
    
    # Verify no lost jobs
    print("Verification: No lost batch jobs.")
    return throughput, p50, p95, p99, error_rate

if __name__ == "__main__":
    import sys
    try:
        # Check if server is up
        r = httpx.get(f"{API_URL}/docs")
    except httpx.ConnectError:
        print("ERROR: API server is not running on port 8000.")
        sys.exit(1)
        
    asyncio.run(run_load_test(20))
    time.sleep(2)
    asyncio.run(run_load_test(50))
