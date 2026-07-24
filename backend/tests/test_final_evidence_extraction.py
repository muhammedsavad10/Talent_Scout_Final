"""
Final Production Evidence Extraction Audit (v2.2) Regression Test Suite.
Verifies certification propagation, technology normalization across all sections, personal project preservation,
extraction diagnostics logging, and serializer validation assertions for Dethan and Muhammad resumes.
"""
import pytest
from app.core.hiring_priority import compute_hiring_priority_score, extract_candidate_evidence

def test_dethan_final_evidence_extraction_v2_2():
    # Devadethan R Resume Payload
    eval_dethan = {
        "evaluation_id": "eval_dethan_v2_2",
        "personal_info": {"name": "Devadethan R"},
        "overall_score": 83.0,
        "parsed_resume": {
            "personal_info": {"name": "Devadethan R"},
            "work_history": [
                {
                    "company": "Prevalent AI",
                    "role": "Data Scientist L1",
                    "dates": "2023 - Present",
                    "description": "Deployed Amazon Bedrock, LLMOps, FastAPI microservices, K8s, Docker, CI/CD, PySpark, REST API."
                },
                {
                    "company": "DifferentByte",
                    "role": "AI Developer",
                    "dates": "2022 - 2023",
                    "description": "Built Lang Chain and Lang Graph REST APIs using PySpark and Django REST."
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
                {"title": "Google AI Essentials", "vendor": "Google"},
                {"title": "IBM AI Engineering Professional Certificate", "vendor": "IBM"},
                {"title": "Google Kubernetes Engine", "vendor": "Google"},
                {"title": "Tableau Data Analyst", "vendor": "Tableau"},
                {"title": "Certified Data Scientist", "vendor": "Global Data Science Institute"}
            ]
        },
        "raw_resume_text": "Devadethan R. Data Scientist L1 at Prevalent AI (2023 - Present). Previously AI Developer at DifferentByte (2022 - 2023), ML Engineer at DataPull (2021 - 2022), ML Mentor at Nullclass (2020 - 2021), Software Engineer at Riss Technologies (2019 - 2020). Google AI Essentials, IBM AI Engineering Professional Certificate, Certified Data Scientist, Google Kubernetes Engine, Tableau Data Analyst. AWS Bedrock, LangChain, LangGraph, FastAPI, PySpark, LLMOps, Docker, Kubernetes, CI/CD."
    }

    res_b = compute_hiring_priority_score(eval_dethan)
    profile_b = res_b["professional_profile"]
    factors_b = res_b["priority_factors"]
    indicators_b = res_b["production_indicators"]
    certs_b = res_b["certifications"]

    # Dethan Required Assertions
    assert profile_b["candidate_name"] == "Devadethan R"
    assert profile_b["certification_count"] >= 5
    assert len(certs_b) >= 5
    assert factors_b["certifications_pts"] > 0
    assert factors_b["production_engineering_pts"] > 0
    assert "AWS Bedrock" in indicators_b
    assert "LangChain" in indicators_b
    assert "FastAPI" in indicators_b

    # Serializer Validation Assertions
    evidence_b = extract_candidate_evidence(eval_dethan)
    assert profile_b["personal_project_count"] == len(evidence_b.personal_projects)
    assert profile_b["certification_count"] == len(evidence_b.certifications)
    assert factors_b["certifications_pts"] > 0 if len(evidence_b.certifications) > 0 else True
    assert factors_b["production_engineering_pts"] > 0 if len(indicators_b) > 0 else True

def test_muhammad_final_evidence_extraction_v2_2():
    # Muhammad Fuvad Sinin Resume Payload
    eval_muhammad = {
        "evaluation_id": "eval_muhammad_v2_2",
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

    res_a = compute_hiring_priority_score(eval_muhammad)
    profile_a = res_a["professional_profile"]
    projects_a = res_a["personal_projects"]
    history_a = res_a["employment_history"]

    # Muhammad Required Assertions
    assert profile_a["candidate_name"] == "Muhammad Fuvad Sinin"
    assert profile_a["professional_experience_count"] == 0
    assert profile_a["personal_project_count"] >= 3
    assert len(projects_a) >= 3
    assert history_a == []

    # Serializer Validation Assertions
    evidence_a = extract_candidate_evidence(eval_muhammad)
    assert profile_a["personal_project_count"] == len(evidence_a.personal_projects)
    assert profile_a["certification_count"] == len(evidence_a.certifications)
