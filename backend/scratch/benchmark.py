import os
import sys
import time
import tracemalloc
import asyncio

# Add backend to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.agents.orchestrator import run_evaluation_pipeline

async def run_benchmark():
    print("=" * 80)
    print("STARTING BACKEND PERFORMANCE BENCHMARK PROFILE")
    print("=" * 80)

    mock_resume = (
        "Name: Benchmark Candidate\n"
        "Email: benchmark@example.com\n"
        "Education: BS in Computer Engineering, State University (2015-2019)\n"
        "Experience: Software Engineer at DevCorp (3 years)\n"
        "Built FastAPI backends and managed Postgres databases.\n"
        "Skills: Python, FastAPI, Docker, SQL"
    )
    required_skills = ["Python", "FastAPI"]

    # Start memory tracing
    tracemalloc.start()
    
    latencies = []
    runs = 3 # 3 runs to get a stable average without hitting Groq limits
    
    print(f"\n[+] Running {runs} iterations of the evaluation pipeline...")
    
    for i in range(runs):
        start_time = time.perf_counter()
        
        # We run the pipeline
        result = await run_evaluation_pipeline(
            text=mock_resume,
            candidate_id=f"bench_{i}",
            required_skills=required_skills
        )
        
        latency = (time.perf_counter() - start_time) * 1000
        latencies.append(latency)
        
        # Check memory
        current, peak = tracemalloc.get_traced_memory()
        print(f"    Run {i+1} | Latency: {latency:7.2f} ms | RAM Current: {current/(1024*1024):.2f} MB | Peak: {peak/(1024*1024):.2f} MB | Status: {result.get('status')}")
        
        # Short sleep to prevent rate limiting
        await asyncio.sleep(2)
        
    tracemalloc.stop()
    
    avg_latency = sum(latencies) / len(latencies)
    print("\n" + "=" * 80)
    print("BENCHMARK METRICS SUMMARY")
    print("=" * 80)
    print(f"Average Pipeline Latency : {avg_latency:.2f} ms")
    print(f"Minimum Pipeline Latency : {min(latencies):.2f} ms")
    print(f"Maximum Pipeline Latency : {max(latencies):.2f} ms")
    print(f"Peak Memory Allocation   : {peak/(1024*1024):.2f} MB")
    print("=" * 80)

if __name__ == "__main__":
    asyncio.run(run_benchmark())
