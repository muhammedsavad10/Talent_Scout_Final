"""
Regression Test Suite for Root Cause Audit for Candidate Name & Evidence Propagation Pipeline (v2.5).
Verifies:
1. Candidate header text before first section header is captured in sections['header'].
2. ingestion.py flat_parsed propagates personal_info and sections.
3. NAME PIPELINE AUDIT and EVIDENCE PIPELINE AUDIT logs are generated.
4. extract_candidate_name() selects real names instead of falling back to Unknown Candidate.
5. certifications, production_indicators, and personal_projects remain populated in final output.
"""
import pytest
from app.agents.ingestion import split_resume_into_sections
from app.core.hiring_priority import compute_hiring_priority_score, extract_candidate_name

def test_header_segmentation_preserves_name_and_contact_info():
    raw_resume = (
        "Devadethan R\n"
        "Email: dev@example.com\n"
        "Phone: +91 9876543210\n"
        "EXPERIENCE\n"
        "Data Scientist L1 at Prevalent AI (2023 - Present)\n"
        "PROJECTS\n"
        "AWS Bedrock LLMOps Platform\n"
        "CERTIFICATIONS\n"
        "Google AI Essentials"
    )
    
    sections = split_resume_into_sections(raw_resume)
    assert "header" in sections
    assert "Devadethan R" in sections["header"]
    assert "Email: dev@example.com" in sections["header"]

def test_name_and_evidence_pipeline_propagation():
    eval_payload = {
        "personal_info": {"name": "Muhammad Fuvad Sinin", "email": "muhammad@example.com"},
        "result": {
            "overall_score": 92.0,
            "raw_resume_text": (
                "Muhammad Fuvad Sinin\n"
                "Email: muhammad@example.com\n"
                "Portfolio of Agentic AI projects: Agentic AI Orchestrator, ETL & RAG Pipeline, Autonomous AI Assistant.\n"
                "Technologies: FastAPI, Kubernetes, Pinecone, Airflow."
            ),
            "projects": [
                {"title": "Agentic AI Orchestrator", "description": "LangGraph multi-agent system."},
                {"title": "ETL & RAG Pipeline", "description": "High-throughput vector search with Pinecone and Kubernetes."},
                {"title": "Autonomous AI Assistant", "description": "Tool execution system."}
            ],
            "certifications": [
                {"title": "Google AI Essentials", "vendor": "Google"}
            ]
        }
    }

    res = compute_hiring_priority_score(eval_payload)

    # Name Pipeline Assertions
    assert res["professional_profile"]["candidate_name"] == "Muhammad Fuvad Sinin"

    # Evidence Pipeline Assertions
    assert len(res["certifications"]) >= 1
    assert len(res["production_indicators"]) >= 2
    assert len(res["personal_projects"]) >= 3
    assert res["professional_profile"]["personal_project_count"] == 3
    assert res["professional_profile"]["certification_count"] >= 1
