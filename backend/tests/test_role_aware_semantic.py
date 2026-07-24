"""
Unit tests & CI Behavioral Ranking Calibration Benchmark for Role-Aware, Section-Aware Semantic Engine.
Ensures behavioral ranking chain & strict score ranges across technical & non-technical candidate profiles:
1. Senior Data Scientist (90-98%)
2. Junior Data Scientist (70-85%)
3. Python Backend Developer (25-65%)
4. Junior MERN Stack Developer (<= 30%)
5. Accountant / Non-Technical Candidate (<= 5%)
"""
import pytest
from unittest.mock import patch
from app.agents.stage1_evaluation import run_stage1_evaluation
from app.core.domain_classifier import classify_multi_domain_profile, compute_multi_domain_alignment
from app.core.section_similarity import compute_section_aware_semantic_similarity

def test_multi_domain_classification_and_evidence():
    hybrid_text = """
    Senior AI & Backend Engineer with 5+ years experience.
    Engineered PyTorch LLM models, vector search pipelines, and FastAPI microservices with PostgreSQL and Docker.
    """
    profiles = classify_multi_domain_profile(hybrid_text, "AI & Backend Engineer")
    
    domain_names = [p["domain"] for p in profiles]
    assert "Machine Learning" in domain_names
    assert "Backend Engineering" in domain_names
    assert len(profiles[0]["evidence"]) > 0

    align = compute_multi_domain_alignment(profiles, "data_science", years_experience=5.0)
    assert align["best_matching_domain"] in ["Data Science", "Machine Learning"]
    assert align["alignment_score"] >= 70

def test_ci_behavioral_ranking_calibration_benchmark():
    jd_text = """
    We are seeking a Data Scientist to design, build, and deploy predictive machine learning models.
    Key requirements: Python, PyTorch, Scikit-Learn, Feature Engineering, Statistics, SQL.
    Responsibilities: Model development, statistical modeling, feature engineering pipelines.
    """
    required_skills = ["Python", "PyTorch", "Scikit-Learn", "Feature Engineering", "Statistics", "SQL"]

    senior_ds = {
        "personal_info": {"name": "Dr. Alice Smith", "title": "Senior Data Scientist"},
        "hard_skills": ["Python", "PyTorch", "Scikit-Learn", "Feature Engineering", "Statistics", "SQL"],
        "work_history": [{"role": "Senior Data Scientist", "company": "AI Labs", "description": "Designed predictive machine learning models."}],
        "projects": [{"title": "Predictive ML Pipeline", "description": "Built feature engineering and PyTorch models."}],
        "raw_resume_text": "Dr. Alice Smith Senior Data Scientist (6+ years experience) Built predictive ML models using PyTorch, TensorFlow, Scikit-Learn."
    }

    junior_ds = {
        "personal_info": {"name": "David Miller", "title": "Junior Data Scientist"},
        "hard_skills": ["Python", "Pandas", "NumPy", "Scikit-Learn", "SQL"],
        "work_history": [{"role": "Junior Data Scientist", "company": "Analytics Inc", "description": "Baseline Scikit-Learn models and EDA."}],
        "projects": [{"title": "Churn Model", "description": "Built baseline classification models with Scikit-Learn."}],
        "raw_resume_text": "David Miller Junior Data Scientist (1 year experience) Baseline classification with Scikit-Learn."
    }

    backend_dev = {
        "personal_info": {"name": "Bob Jones", "title": "Senior Python Backend Engineer"},
        "hard_skills": ["Python", "FastAPI", "Django", "PostgreSQL", "Docker", "SQL"],
        "work_history": [{"role": "Senior Backend Engineer", "company": "CloudTech", "description": "Architected microservices using FastAPI and Django."}],
        "projects": [{"title": "Microservices", "description": "Built FastAPI gateway with Docker."}],
        "raw_resume_text": "Bob Jones Senior Python Backend Engineer (5+ years experience) FastAPI Django PostgreSQL microservices."
    }

    mern_dev = {
        "personal_info": {"name": "Charlie Brown", "title": "Junior MERN Stack Developer"},
        "hard_skills": ["React", "Node.js", "Express", "MongoDB", "JavaScript"],
        "work_history": [{"role": "Junior MERN Developer", "company": "WebStudio", "description": "Built React and Node.js web apps."}],
        "projects": [{"title": "E-Commerce", "description": "React Express online store."}],
        "raw_resume_text": "Charlie Brown Junior MERN Stack Developer (1 year experience) React Node.js Express MongoDB."
    }

    non_tech = {
        "personal_info": {"name": "Emma Watson", "title": "Senior Accountant"},
        "hard_skills": ["Financial Auditing", "Bookkeeping", "Microsoft Excel", "Tax Preparation"],
        "work_history": [{"role": "Senior Accountant", "company": "Finance Group", "description": "Financial auditing and tax preparation."}],
        "projects": [{"title": "Audit Automation", "description": "Excel tax formulas."}],
        "raw_resume_text": "Emma Watson Senior Accountant Financial auditing tax preparation Excel."
    }

    s_sr_ds = compute_section_aware_semantic_similarity(senior_ds, jd_text, "Data Scientist", required_skills)["overall_semantic_similarity"]
    s_jr_ds = compute_section_aware_semantic_similarity(junior_ds, jd_text, "Data Scientist", required_skills)["overall_semantic_similarity"]
    s_be = compute_section_aware_semantic_similarity(backend_dev, jd_text, "Data Scientist", required_skills)["overall_semantic_similarity"]
    s_mern = compute_section_aware_semantic_similarity(mern_dev, jd_text, "Data Scientist", required_skills)["overall_semantic_similarity"]
    s_non_tech = compute_section_aware_semantic_similarity(non_tech, jd_text, "Data Scientist", required_skills)["overall_semantic_similarity"]

    # Behavioral Ranking Chain Verification
    assert s_sr_ds > s_jr_ds, f"Senior DS ({s_sr_ds}%) should be > Junior DS ({s_jr_ds}%)"
    assert s_jr_ds > s_be, f"Junior DS ({s_jr_ds}%) should be > Backend Dev ({s_be}%)"
    assert s_be > s_mern, f"Backend Dev ({s_be}%) should be > MERN Dev ({s_mern}%)"
    assert s_mern >= s_non_tech, f"MERN Dev ({s_mern}%) should be >= Non-Tech ({s_non_tech}%)"

    # Calibrated Expected Range Assertions
    assert 90 <= s_sr_ds <= 98, f"Senior DS score ({s_sr_ds}%) should be in range 90-98%"
    assert 70 <= s_jr_ds <= 85, f"Junior DS score ({s_jr_ds}%) should be in range 70-85%"
    assert 25 <= s_be <= 65, f"Backend Dev score ({s_be}%) should be in range 25-65%"
    assert s_mern <= 30, f"MERN Dev score ({s_mern}%) should be <= 30%"
    assert s_non_tech <= 5, f"Non-Tech Accountant score ({s_non_tech}%) should be <= 5%"

@pytest.mark.asyncio
async def test_role_aware_semantic_benchmark_ranking():
    jd_text = """
    We are seeking a Senior Data Scientist to design and deploy predictive machine learning models.
    Key requirements: Python, PyTorch, Scikit-Learn, Feature Engineering, Statistics, SQL.
    Responsibilities: Model development, statistical modeling, feature engineering pipelines.
    """

    required_skills = ["Python", "PyTorch", "Feature Engineering", "Statistics", "SQL"]

    # Candidate 1: Senior Data Scientist
    ds_resume = """
    Dr. Alice Smith
    Senior Data Scientist (6+ years experience)
    Built predictive machine learning models and deep learning pipelines using PyTorch, TensorFlow, and Scikit-Learn.
    Engineered automated feature engineering systems and conducted statistical modeling for experiment design.
    Proficient in Python, R, and SQL.
    """

    # Candidate 2: Python Backend Developer
    backend_resume = """
    Bob Jones
    Senior Python Backend Engineer (5+ years experience)
    Architected high-throughput microservices using FastAPI, Django, and PostgreSQL.
    Designed REST APIs, database schemas, Docker containers, and CI/CD pipelines.
    Proficient in Python, SQL, Git, and AWS.
    """

    # Candidate 3: Junior MERN Stack Developer
    mern_resume = """
    Charlie Brown
    Junior MERN Stack Developer (1 year experience)
    Built responsive web applications using React, Node.js, Express, and MongoDB.
    Implemented RESTful APIs and UI components with Tailwind CSS and JavaScript.
    Proficient in JavaScript, Node.js, Express, MongoDB, Git.
    """

    eval_ds = await run_stage1_evaluation(
        text=ds_resume, candidate_id="cand_ds", required_skills=required_skills, jd_text=jd_text
    )

    eval_be = await run_stage1_evaluation(
        text=backend_resume, candidate_id="cand_be", required_skills=required_skills, jd_text=jd_text
    )

    parsed_mern = {
        "personal_info": {"name": "Charlie Brown", "email": "charlie@example.com", "phone": "123-456-7890", "title": "Junior MERN Stack Developer"},
        "hard_skills": ["React", "Node.js", "Express", "MongoDB", "JavaScript", "Git", "Tailwind CSS"],
        "skills": {"frontend": ["React", "JavaScript"], "backend": ["Node.js", "Express"], "database": ["MongoDB"]},
        "work_history": [{"role": "Junior MERN Stack Developer", "company": "Tech Corp", "dates": "2023", "description": "Built React and Node.js web apps with MongoDB."}],
        "projects": [{"title": "Web App", "description": "Built responsive React and Express applications."}],
        "education": ["BS Computer Science"],
        "experience": ["Junior MERN Stack Developer"],
        "certifications": [],
        "raw_resume_text": mern_resume
    }

    with patch("app.agents.stage1_evaluation.parse_resume_to_json", return_value=parsed_mern):
        eval_mern = await run_stage1_evaluation(
            text=mern_resume, candidate_id="cand_mern", required_skills=required_skills, jd_text=jd_text
        )

    assert eval_ds["status"] == "success"
    assert eval_be["status"] == "success"
    assert eval_mern["status"] == "success"

    score_ds = eval_ds["semantic_similarity_score"]
    score_be = eval_be["semantic_similarity_score"]
    score_mern = eval_mern["semantic_similarity_score"]

    assert score_ds >= 80, f"Senior Data Scientist score ({score_ds}%) should be >= 80%"
    assert 25 <= score_be <= 65, f"Python Backend Dev score ({score_be}%) should be in range 25-65%"
    assert score_mern <= 35, f"Junior MERN Stack Dev score ({score_mern}%) should be <= 35%"

    # Verify exact ranking order: Data Scientist > Backend Dev > MERN Dev
    assert score_ds > score_be > score_mern

    # Verify multi-domain breakdown structure is exposed
    breakdown_mern = eval_mern.get("semantic_similarity_breakdown", {})
    assert breakdown_mern.get("domain_alignment") is not None
    assert breakdown_mern.get("candidate_domains") is not None
    assert breakdown_mern.get("domain_evidence") is not None
    assert breakdown_mern.get("best_matching_domain") is not None
