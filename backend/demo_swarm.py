"""
Enterprise Multi-Agent Recruitment System - Week 3 Swarm Visualizer
Run this script to demonstrate the autonomous LangGraph pipeline to reviewers.
"""
import os
import json
from app.agents.orchestrator import run_evaluation_pipeline

def run_live_reviewer_demo():
    print("=" * 70)
    print("[SWARM] TALENTSCOUT ENTERPRISE MULTI-AGENT SWARM VISUALIZER")
    print("=" * 70)
    
    # 1. Prepare Mock PDF Bytes (Simulating an uploaded resume)
    mock_pdf_bytes = b"%PDF-1.4 ... Fake PDF Header ... \n" + \
                     b"Muhammed Sajad\n" + \
                     b"Education: B.Tech in Computer Science, KTU University\n" + \
                     b"Experience: Software Engineer Intern at TechCorp (1 year)\n" + \
                     b"Hard Skills: Python, FastAPI, PostgreSQL, Git, Docker, JavaScript\n"
                     
    # 2. Define the Recruiter's Job Description and Required Explicit Skills
    target_jd = "Looking for a Backend Developer proficient in Python, FastAPI, and Qdrant Vector DB."
    required_skills = ["Python", "FastAPI", "Qdrant", "Kubernetes"]
    
    print(f"\n[INPUT] Target Job Description:\n-> \"{target_jd}\"")
    print(f"[INPUT] Explicit Skills Tracked: {required_skills}\n")
    print("[RUNNING] Initializing LangGraph Stateful Engine... Orchestrating 4 Agents...\n")
    
    # 3. Trigger the LangGraph Multi-Agent Swarm
    try:
        import asyncio
        pdf_text = mock_pdf_bytes.decode("utf-8")
        
        final_state = asyncio.run(run_evaluation_pipeline(
            text=pdf_text,
            candidate_id="demo_candidate_id",
            required_skills=required_skills
        ))
        
        # Check if an internal node caught an error
        if final_state.get("status") == "error":
            print(f"[ERROR] Swarm Execution Stopped due to node error: {final_state.get('message')}")
            return

        print("[SUCCESS] [SWARM PIPELINE COMPLETE] - Final State Extracted Successfully.\n")
        print("-" * 70)
        print("AGENT 1: INGESTION AGENT (LLM Structured Parser)")
        print("-" * 70)
        print(json.dumps(final_state.get("personal_info", {}), indent=2))
        print(json.dumps(final_state.get("contacts", {}), indent=2))
        
        print("\n" + "-" * 70)
        print("AGENT 2: SEMANTIC SCOUT AGENT (Vector Search Engine)")
        print("-" * 70)
        print(f"[-] Qdrant Vector Search Match Score: {final_state.get('debug', {}).get('raw_semantic_similarity', 0.0):.4f}")
        
        print("\n" + "-" * 70)
        print("AGENT 3: XAI SCORER AGENT (Transparent Set Mathematics)")
        print("-" * 70)
        print(f"[-] Composite Weighted Fit Score:   {final_state.get('overall_score', 0)}/100")
        print(f"[MATCHED] Matched Skills Extracted:        {final_state.get('matched_skills', [])}")
        print(f"[MISSING] Detected Skill Gaps (Missing):  {final_state.get('missing_skills', [])}")
        
        print("\n" + "-" * 70)
        print("AGENT 4: STRATEGY AGENT (Empathetic Career Coach)")
        print("-" * 70)
        print(f"Hiring Tier Recommendation: {final_state.get('recommendation', {}).get('hiring_recommendation')}")
        print(f"Reasoning:\n{final_state.get('recommendation_basis', {}).get('reasoning')}")
        
    except Exception as e:
        print(f"[ERROR] Critical Pipeline Failure: {e}")
        print("[TIP] Tip: Verify your .env file has valid GROQ_API_KEY and QDRANT credentials!")

if __name__ == "__main__":
    run_live_reviewer_demo()