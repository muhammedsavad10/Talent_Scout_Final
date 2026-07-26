"""
TalentScout Enterprise v1.7.1 — Employment Intelligence Root Cause Fix Test Suite.
Validates:
1. Muhammad:
   - employment_history == []
   - Delay2Decision and FairCrop AI exist ONLY under projects.
   - career_progression == []
   - professional_experience_count == 0
   - total_professional_years == 0
   - Recruiter explanation explicitly states: "Strong portfolio of technically advanced personal AI projects demonstrating production engineering capability, but limited or no verified professional employment."
2. Devadethan:
   - current_company == "Prevalent AI", current_role == "Data Scientist L1"
   - professional_experience_count >= 1, total_professional_years > 0
3. Shadin:
   - current_company == "Bridgeon Solutions", current_role == "Data Analyst"
4. Adhil:
   - Certifications contain only genuine credentials (zero action verbs).
5. Benchmark candidate ranking preservation: Devadethan > Muhammad > Shadin > Adhil.
"""
import pytest
import asyncio
from app.agents.orchestrator import run_evaluation_pipeline
from app.core.consistency_validator import validate_final_api_response
from app.core.hiring_priority import compute_hiring_priority_score
from app.agents.comparator import compare_candidates
from app.core.experience_calculator import calculate_professional_experience

MUHAMMAD_RESUME = """
Muhammad Fuvad Sinin
Email: fuvad@example.com | Phone: +91 9876543210
SUMMARY
Senior AI Engineer experienced in scalable systems.

PROJECTS
Delay2Decision
- Designed and developed a dynamic decision-support system using LangChain and Qdrant.
FairCrop AI
- Crop yield prediction platform.

CERTIFICATIONS
AWS Certified Solutions Architect
"""

DEVADETHAN_RESUME = """
Devadethan R
Email: dethan@example.com | Phone: +91 9876543210
EXPERIENCE
Data Scientist L1 at Prevalent AI (2023 - Present)
- Developed RAG systems and FastAPI microservices.
AI Developer at DifferentByte (2022 - 2023)
ML Engineer at DataPull (2021 - 2022)

PROJECTS
Delay2Decision Agent
- Built multi-agent decision system using LangGraph and Qdrant.

CERTIFICATIONS
Google AI Essentials
IBM AI Engineering Professional Certificate
"""

SHADIN_RESUME = """
Shadin K
Email: shadin@example.com
EXPERIENCE
Data Analyst at Bridgeon Solutions (2022 - Present)
- Data visualization and SQL analytics.

PROJECTS
ETL Ingestion Pipeline
- High-throughput data ingestion using PySpark.
"""

ADHIL_RESUME = """
Adhil Kumar
Email: adhil@example.com
EXPERIENCE
Python Engineer at DataPull (2020 - Present)

PROJECTS
Built microservices on AWS Docker Kubernetes
Designed AWS infrastructure for production LLMs
Implemented live pipeline auditing

CERTIFICATIONS
AWS Certified Developer
"""

@pytest.mark.asyncio
async def test_muhammad_v1_7_1_employment_intelligence():
    res = await run_evaluation_pipeline(MUHAMMAD_RESUME, "eval_muhammad_v171", required_skills=["Python"])
    final_json = validate_final_api_response(res)
    
    # 1. employment_history must be empty
    hp_data = final_json.get("hiring_priority", {})
    assert final_json.get("employment_history", []) == [] or final_json.get("employment_history") is None
    assert hp_data.get("employment_history", []) == []
    
    # 2. Delay2Decision and FairCrop AI exist ONLY under projects
    inner_eval = final_json.get("evaluation", {})
    parsed_res = inner_eval.get("parsed_resume", {})
    project_titles = [p.get("title") for p in parsed_res.get("projects", [])]
    assert "Delay2Decision" in project_titles or "FairCrop AI" in project_titles
    
    for emp in hp_data.get("employment_history", []):
        assert emp.get("company") not in ["Delay2Decision", "FairCrop AI"]

    # 3. career_progression must be empty
    assert hp_data.get("career_progression", []) == []

    # 4. professional_experience_count and total_professional_years must be 0
    prof_profile = hp_data.get("professional_profile", {})
    assert prof_profile.get("professional_experience_count") == 0
    assert prof_profile.get("total_professional_years") == 0.0

    # 5. Recruiter explanation must mention project portfolio instead of false company tenure
    reasons = hp_data.get("priority_reasons", [])
    assert any("portfolio of technically advanced personal AI projects" in r for r in reasons)

def test_experience_calculator_module():
    fake_projects_as_work = [
        {"company": "Delay2Decision", "role": "Designed AI System", "dates": "2023 - 2024"},
        {"company": "FairCrop AI", "role": "Crop yield prediction", "dates": "2022 - 2023"}
    ]
    calc_out = calculate_professional_experience(fake_projects_as_work)
    assert calc_out["professional_experience_count"] == 0
    assert calc_out["total_professional_years"] == 0.0
    assert calc_out["current_company"] == "Unknown"
    assert calc_out["current_role"] == "Unknown"

@pytest.mark.asyncio
async def test_devadethan_v1_7_1_no_regression():
    res = await run_evaluation_pipeline(DEVADETHAN_RESUME, "eval_devadethan_v171", required_skills=["Python"])
    final_json = validate_final_api_response(res)
    
    assert final_json.get("current_company") == "Prevalent AI"
    assert final_json.get("current_role") == "Data Scientist L1"
    
    prof_profile = final_json.get("hiring_priority", {}).get("professional_profile", {})
    assert prof_profile.get("professional_experience_count") >= 1
    assert prof_profile.get("total_professional_years") > 0.0

@pytest.mark.asyncio
async def test_shadin_v1_7_1_no_regression():
    res = await run_evaluation_pipeline(SHADIN_RESUME, "eval_shadin_v171", required_skills=["Python"])
    final_json = validate_final_api_response(res)
    
    assert final_json.get("current_company") == "Bridgeon Solutions"
    assert final_json.get("current_role") == "Data Analyst"

@pytest.mark.asyncio
async def test_adhil_v1_7_1_no_certification_regression():
    res = await run_evaluation_pipeline(ADHIL_RESUME, "eval_adhil_v171", required_skills=["Python"])
    final_json = validate_final_api_response(res)
    
    certs = final_json.get("certifications") or final_json.get("evaluation", {}).get("certifications", [])
    assert len(certs) > 0
    action_verbs = ("Built", "Designed", "Implemented", "Developed", "Created", "Engineered", "Integrated", "Optimized", "Deployed")
    for c in certs:
        title = c.get("title") or c.get("name") if isinstance(c, dict) else str(c)
        assert not title.startswith(action_verbs)

def test_v1_7_1_benchmark_candidate_ranking_preservation():
    cand_devadethan = {
        "overall_score": 96.0,
        "evaluation_id": "cand_devadethan",
        "personal_info": {"name": "Devadethan"},
        "parsed_resume": {
            "personal_info": {"name": "Devadethan"},
            "work_history": [{"company": "Prevalent AI", "role": "Data Scientist L1", "dates": "2023 - Present"}],
            "projects": [{"title": "RAG Agent", "description": "Agentic system"}],
            "certifications": [{"vendor": "Google", "title": "Google AI Essentials"}],
            "hard_skills": ["Python", "PyTorch", "NLP", "Qdrant"]
        }
    }

    cand_muhammad = {
        "overall_score": 92.0,
        "evaluation_id": "cand_muhammad",
        "personal_info": {"name": "Muhammad Fuvad"},
        "parsed_resume": {
            "personal_info": {"name": "Muhammad Fuvad"},
            "work_history": [],
            "projects": [{"title": "FairCrop AI", "description": "Yield predictor"}],
            "certifications": [{"vendor": "AWS", "title": "AWS Certified Solutions Architect"}],
            "hard_skills": ["Python", "FastAPI", "Docker", "Qdrant"]
        }
    }

    cand_shadin = {
        "overall_score": 85.0,
        "evaluation_id": "cand_shadin",
        "personal_info": {"name": "Shadin"},
        "parsed_resume": {
            "personal_info": {"name": "Shadin"},
            "work_history": [{"company": "Bridgeon Solutions", "role": "Data Analyst", "dates": "2022 - Present"}],
            "projects": [{"title": "ETL Pipeline", "description": "Data ingestion"}],
            "certifications": [],
            "hard_skills": ["Python", "Django", "PostgreSQL"]
        }
    }

    cand_adhil = {
        "overall_score": 75.0,
        "evaluation_id": "cand_adhil",
        "personal_info": {"name": "Adhil"},
        "parsed_resume": {
            "personal_info": {"name": "Adhil"},
            "work_history": [{"company": "DataPull", "role": "Python Engineer", "dates": "2020 - Present"}],
            "projects": [{"title": "Dashboard", "description": "Web dashboard"}],
            "certifications": [],
            "hard_skills": ["Python", "Flask"]
        }
    }

    for cand in [cand_devadethan, cand_muhammad, cand_shadin, cand_adhil]:
        cand["hiring_priority"] = compute_hiring_priority_score(cand)

    ranked = compare_candidates([cand_devadethan, cand_muhammad, cand_shadin, cand_adhil])

    assert len(ranked) == 4
    assert ranked[0]["candidate_name"] == "Devadethan"
    assert ranked[1]["candidate_name"] == "Muhammad Fuvad"
    assert ranked[2]["candidate_name"] == "Shadin"
    assert ranked[3]["candidate_name"] == "Adhil"
