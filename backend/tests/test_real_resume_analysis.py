"""
Regression test suite for Real Resume Analysis & Evidence Extraction Pipeline.
Verifies that Stage 2 Hiring Priority Engine correctly extracts candidate names, structured certifications,
preserves distinct company names and dates for each role, detects production engineering indicators,
and populates personal projects for Muhammad and professional experience for Dethan.
"""
import pytest
from app.core.hiring_priority import compute_hiring_priority_score, extract_candidate_evidence

def test_real_resume_evidence_extraction_and_differentiation():
    # Candidate A – Muhammad Fuvad Sinin: Strong AI/ML project portfolio, 0 formal company roles
    eval_a = {
        "evaluation_id": "eval_muhammad_real",
        "personal_info": {"name": "Muhammad Fuvad Sinin"},
        "overall_score": 94.0,
        "parsed_resume": {
            "personal_info": {"name": "Muhammad Fuvad Sinin"},
            "projects": [
                {"title": "Agentic AI Orchestrator", "description": "Built multi-agent AI system using LangGraph and Airflow."},
                {"title": "ETL & RAG Pipeline", "description": "High-throughput vector search pipeline with Pinecone and Kubernetes."},
                {"title": "Autonomous AI Assistant", "description": "Cloud-native LLM agentic tool execution system."}
            ],
            "work_history": [],
            "certifications": []
        },
        "raw_resume_text": "Muhammad Fuvad Sinin. Portfolio of Advanced Agentic AI projects using LangGraph, Airflow, Kubernetes, ETL, RAG, and Pinecone."
    }

    # Candidate B – Devadethan R: Multiple formal AI roles with distinct companies & dates, multiple certs (Google AI, IBM AI, Tableau, GKE)
    eval_b = {
        "evaluation_id": "eval_dethan_real",
        "personal_info": {"name": "Devadethan R"},
        "overall_score": 83.0,
        "parsed_resume": {
            "personal_info": {"name": "Devadethan R"},
            "work_history": [
                {
                    "company": "Prevalent AI",
                    "role": "Data Scientist L1",
                    "dates": "2023 - Present",
                    "description": "Deployed AWS Bedrock, LLMOps, FastAPI microservices, Docker, Kubernetes, CI/CD, PySpark."
                },
                {
                    "company": "DifferentByte",
                    "role": "AI Developer",
                    "dates": "2022 - 2023",
                    "description": "Built LangChain and LangGraph REST APIs using PySpark and Django REST."
                },
                {
                    "company": "DataPull",
                    "role": "Machine Learning Engineer",
                    "dates": "2021 - 2022",
                    "description": "Engineered distributed ML training pipelines and REST APIs."
                },
                {
                    "company": "Nullclass",
                    "role": "Machine Learning Mentor",
                    "dates": "2020 - 2021",
                    "description": "Mentored 50+ junior developers in Machine Learning and PyTorch."
                },
                {
                    "company": "Riss Technologies",
                    "role": "Software Engineer",
                    "dates": "2019 - 2020",
                    "description": "Built backend services."
                }
            ],
            "certifications": [
                {"title": "Google AI Essentials", "issuer": "Google"},
                {"title": "IBM AI Engineering Professional Certificate", "issuer": "IBM"},
                {"title": "Certified Data Scientist", "issuer": "Global Data Science Institute"},
                {"title": "Google Kubernetes Engine", "issuer": "Google Cloud"},
                {"title": "Tableau", "issuer": "Tableau"}
            ]
        },
        "raw_resume_text": "Devadethan R. Data Scientist L1 at Prevalent AI (2023 - Present). Previously AI Developer at DifferentByte (2022 - 2023), ML Engineer at DataPull (2021 - 2022), ML Mentor at Nullclass (2020 - 2021), Software Engineer at Riss Technologies (2019 - 2020). Google AI Essentials, IBM AI Engineering Professional Certificate, Certified Data Scientist, Google Kubernetes Engine, Tableau. AWS Bedrock, LangChain, LangGraph, FastAPI, PySpark, LLMOps, Docker, Kubernetes, CI/CD."
    }

    # 1. Execute Stage 2 Priority Analysis
    res_a = compute_hiring_priority_score(eval_a)
    res_b = compute_hiring_priority_score(eval_b)

    # 2. Assert Candidate Names
    assert res_a["professional_profile"]["candidate_name"] == "Muhammad Fuvad Sinin"
    assert res_b["professional_profile"]["candidate_name"] == "Devadethan R"
    assert "Expert HR" not in res_a["professional_profile"]["candidate_name"]
    assert "Expert HR" not in res_b["professional_profile"]["candidate_name"]

    # 3. Assert Certifications
    assert len(res_b["certifications"]) >= 4
    assert res_b["priority_factors"]["certifications_pts"] > 0
    assert any("google ai" in c["name"].lower() or "ibm" in c["name"].lower() or "tableau" in c["name"].lower() for c in res_b["certifications"])

    # 4. Assert Employment History & Distinct Company Names (No Prevalent AI duplication across all roles)
    dethan_companies = [e["company"] for e in res_b["employment_history"]]
    assert dethan_companies.count("Prevalent AI") == 1
    assert "DifferentByte" in dethan_companies
    assert "DataPull" in dethan_companies
    assert "Nullclass" in dethan_companies
    assert "Riss Technologies" in dethan_companies

    # 5. Assert Preserved Employment Dates (Not replacing every role with 2020)
    dethan_dates = [e["dates"] for e in res_b["employment_history"]]
    assert "2023 - Present" in dethan_dates or "2023" in str(dethan_dates)
    assert any("2022" in d for d in dethan_dates)
    assert any("2021" in d for d in dethan_dates)

    # 6. Assert Company Diversity
    assert len(res_b["professional_profile"]["company_diversity"]) >= 4
    assert "DifferentByte" in res_b["professional_profile"]["company_diversity"]

    # 7. Assert Production Engineering Technologies
    assert res_b["priority_factors"]["production_engineering_pts"] > 0
    prod_reason = res_b["fine_grained_evidence"]["production_engineering"]["reason"]
    assert any(tech in prod_reason.lower() for tech in ["aws bedrock", "langchain", "langgraph", "fastapi", "pyspark", "llmops", "docker", "kubernetes", "ci/cd"])

    # 8. Assert Muhammad's Personal Projects Preserved
    assert res_a["professional_profile"]["personal_project_count"] == 3
    assert res_a["professional_profile"]["professional_experience_count"] == 0
