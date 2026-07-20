"""
Enterprise Multi-Agent Recruitment System - Week 3 Swarm Visualizer
Run this script to demonstrate the autonomous LangGraph pipeline to reviewers.
"""
import os
import json
from app.agents.orchestrator import run_evaluation_pipeline

def run_live_reviewer_demo():
    print("=" * 70)
    print("🚀 TALENTSCOUT ENTERPRISE MULTI-AGENT SWARM VISUALIZER")
    print("=" * 70)
    
    # 1. Prepare Mock PDF Bytes (Simulating an uploaded resume)
    # Note: For this demo script, we use text-based bytes that pypdf can read.
    mock_pdf_bytes = b"%PDF-1.4 ... Fake PDF Header ... \n" + \
                     b"Muhammed Sajad\n" + \
                     b"Education: B.Tech in Computer Science, KTU University\n" + \
                     b"Experience: Software Engineer Intern at TechCorp (1 year)\n" + \
                     b"Hard Skills: Python, FastAPI, PostgreSQL, Git, Docker, JavaScript\n"
                     
    # 2. Define the Recruiter's Job Description and Required Explicit Skills
    target_jd = "Looking for a Backend Developer proficient in Python, FastAPI, and Qdrant Vector DB."
    required_skills = ["Python", "FastAPI", "Qdrant", "Kubernetes"]
    
    print(f"\n[📥 Input] Target Job Description:\n👉 \"{target_jd}\"")
    print(f"[📥 Input] Explicit Skills Tracked: {required_skills}\n")
    print("🔄 Initializing LangGraph Stateful Engine... Orchestrating 4 Agents...\n")
    
    # 3. Trigger the LangGraph Multi-Agent Swarm
    try:
        final_state = run_evaluation_pipeline(
            pdf_bytes=mock_pdf_bytes, 
            jd_text=target_jd, 
            jd_skills=required_skills
        )
        
        # Check if an internal node caught an error
        if final_state.get("error"):
            print(f"❌ Swarm Execution Stopped due to node error: {final_state['error']}")
            return

        print("✅ [SWARM PIPELINE COMPLETE] - Final State Extracted Successfully.\n")
        print("-" * 70)
        print("🧠 AGENT 1: INGESTION AGENT (LLM Structured Parser)")
        print("-" * 70)
        print(json.dumps(final_state["parsed_data"], indent=2))
        
        print("\n" + "-" * 70)
        print("🔍 AGENT 2: SEMANTIC SCOUT AGENT (Vector Search Engine)")
        print("-" * 70)
        print(f"🔹 Qdrant Vector Search Match Score: {final_state['semantic_score']:.4f}")
        
        print("\n" + "-" * 70)
        print("📊 AGENT 3: XAI SCORER AGENT (Transparent Set Mathematics)")
        print("-" * 70)
        metrics = final_state["xai_metrics"]
        print(f"🔹 Jaccard Explicit Overlap Score: {metrics['jaccard_score']:.4f}")
        print(f"🔹 Composite Weighted Fit Score:   {metrics['weighted_score']:.4f}")
        print(f"🟢 Matched Skills Extracted:        {metrics['matched_skills']}")
        print(f"🔴 Detected Skill Gaps (Missing):  {metrics['missing_skills']}")
        
        print("\n" + "-" * 70)
        print("✉️ AGENT 4: STRATEGY AGENT (Empathetic Career Coach)")
        print("-" * 70)
        print(final_state["feedback_report"])
        
    except Exception as e:
        print(f"❌ Critical Pipeline Failure: {e}")
        print("💡 Tip: Verify your .env file has valid GROQ_API_KEY and QDRANT credentials!")

if __name__ == "__main__":
    run_live_reviewer_demo()