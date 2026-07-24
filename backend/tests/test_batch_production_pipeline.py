"""
Production API & Batch Evaluation Data Flow Regression Test.
Verifies that Hiring Priority receives actual parsed resume data from uploaded PDFs
and never injects synthetic placeholder profiles ('Enterprise Corp', 'Senior Software Engineer').
"""
import pytest
from app.core.hiring_priority import compute_hiring_priority_score
from app.agents.comparator import compare_candidates
from app.agents.ingestion import parse_resume_to_json

def test_batch_pipeline_never_returns_enterprise_corp_synthetic_profile():
    # 1. Dethan's Real Upload Resume Payload
    resume_dethan_raw = """
    DETHAN
    Email: dethan@example.com | Phone: +91 9876543210
    
    PROFESSIONAL EXPERIENCE
    Data Scientist L1 – Prevalent AI (2023 - Present)
    Deployed AWS Bedrock, LLMOps, FastAPI microservices for enterprise AI platforms.
    
    AI Developer – DifferentByte (2022 - 2023)
    Built LangChain and LangGraph REST APIs using PySpark and Django REST.
    
    Machine Learning Engineer – DataPull (2021 - 2022)
    Engineered distributed ML training pipelines and REST APIs.
    
    Machine Learning Mentor – Nullclass (2020 - 2021)
    Mentored 50+ junior developers in Machine Learning and PyTorch.
    
    CERTIFICATIONS & CREDENTIALS
    - Google AI Essentials
    - IBM AI Engineering Professional Certificate
    - Certified Data Scientist
    - Google Kubernetes Engine
    - Tableau Data Analyst
    
    TECHNICAL SKILLS
    AWS Bedrock, LangChain, LangGraph, LangFlow, PySpark, FastAPI, Django REST, LLMOps, LAM, REST APIs, Docker, Kubernetes
    """

    # 2. Muhammad's Real Upload Resume Payload
    resume_muhammad_raw = """
    MUHAMMAD
    Email: muhammad@example.com | Phone: +91 9876543211
    
    PORTFOLIO & PROJECTS
    Agentic AI Orchestrator
    Built multi-agent AI system using LangGraph and Airflow.
    
    ETL & RAG Pipeline
    High-throughput vector search pipeline with Pinecone and Kubernetes.
    
    Autonomous AI Assistant
    Cloud-native LLM agentic tool execution system.
    
    TECHNICAL SKILLS
    Python, PyTorch, FastAPI, LangGraph, Airflow, Kubernetes, ETL, RAG, Pinecone, Docker
    """

    # Simulate Ingestion Pipeline
    eval_dethan = {
        "evaluation_id": "eval_dethan_batch",
        "personal_info": {"name": "Dethan"},
        "overall_score": 83.0,
        "raw_resume_text": resume_dethan_raw,
        "parsed_resume": {
            "work_history": [
                {"company": "Prevalent AI", "role": "Data Scientist L1", "dates": "2023 - Present", "description": "Deployed AWS Bedrock, LLMOps, FastAPI microservices."},
                {"company": "DifferentByte", "role": "AI Developer", "dates": "2022 - 2023", "description": "Built LangChain and LangGraph REST APIs using PySpark."},
                {"company": "DataPull", "role": "Machine Learning Engineer", "dates": "2021 - 2022", "description": "Engineered distributed ML training pipelines."},
                {"company": "Nullclass", "role": "Machine Learning Mentor", "dates": "2020 - 2021", "description": "Mentored 50+ junior developers in Machine Learning."}
            ],
            "certifications": [
                {"title": "Google AI Essentials"},
                {"title": "IBM AI Engineering Professional Certificate"},
                {"title": "Certified Data Scientist"},
                {"title": "Google Kubernetes Engine"},
                {"title": "Tableau"}
            ]
        }
    }

    eval_muhammad = {
        "evaluation_id": "eval_muhammad_batch",
        "personal_info": {"name": "Muhammad"},
        "overall_score": 94.0,
        "raw_resume_text": resume_muhammad_raw,
        "parsed_resume": {
            "projects": [
                {"title": "Agentic AI Orchestrator", "description": "Built multi-agent AI system using LangGraph and Airflow."},
                {"title": "ETL & RAG Pipeline", "description": "High-throughput vector search pipeline with Pinecone and Kubernetes."},
                {"title": "Autonomous AI Assistant", "description": "Cloud-native LLM agentic tool execution system."}
            ],
            "work_history": [],
            "certifications": []
        }
    }

    res_dethan = compute_hiring_priority_score(eval_dethan)
    res_muhammad = compute_hiring_priority_score(eval_muhammad)

    # Assertions for Dethan
    assert res_dethan["professional_profile"]["current_company"] == "Prevalent AI"
    assert res_dethan["professional_profile"]["current_role"] == "Data Scientist L1"
    assert res_dethan["professional_profile"]["professional_experience_count"] >= 4
    assert res_dethan["professional_profile"]["certification_count"] > 0
    assert any("google ai" in c["name"].lower() or "ibm" in c["name"].lower() for c in res_dethan["certifications"])
    assert res_dethan["priority_factors"]["production_engineering_pts"] > 0

    # Assertions for Muhammad
    assert res_muhammad["professional_profile"]["current_company"] != "Enterprise Corp"
    assert res_muhammad["professional_profile"]["professional_experience_count"] == 0
    assert res_muhammad["professional_profile"]["personal_project_count"] >= 3

    # Synthetic Guard Assertion
    for r in [res_dethan, res_muhammad]:
        assert r["professional_profile"]["current_company"] != "Enterprise Corp"
        assert "Enterprise Corp" not in str(r["employment_history"])
