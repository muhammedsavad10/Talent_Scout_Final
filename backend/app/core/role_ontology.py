"""
Deterministic Role Ontology Module.
Defines role taxonomy, alias mappings, core skill signatures, and deterministic role fit scoring.
"""
import re
import logging
from typing import Dict, Any, List, Optional

logger = logging.getLogger("talentscout_role_ontology")

ROLE_TAXONOMY: Dict[str, Dict[str, Any]] = {
    "data_scientist": {
        "display_name": "Data Scientist",
        "aliases": [
            "data scientist", "data science consultant", "ai research engineer",
            "data science specialist", "applied scientist", "lead data scientist",
            "senior data scientist", "principal data scientist"
        ],
        "core_skills": [
            "python", "statistics", "machine learning", "scikit-learn", "pytorch",
            "tensorflow", "pandas", "numpy", "feature engineering", "experiment design",
            "statistical modeling", "predictive modeling", "r"
        ],
        "secondary_skills": ["sql", "tableau", "power bi", "deep learning", "nlp", "fastapi", "bigquery"],
        "related_roles": ["ml_engineer", "data_analyst"]
    },
    "ml_engineer": {
        "display_name": "Machine Learning Engineer",
        "aliases": [
            "ml engineer", "machine learning engineer", "mlops engineer",
            "ai engineer", "deep learning engineer", "nlp engineer",
            "computer vision engineer", "ml infrastructure engineer"
        ],
        "core_skills": [
            "python", "pytorch", "tensorflow", "mlops", "model serving",
            "cuda", "transformers", "onnx", "docker", "kubeflow", "mlflow",
            "scikit-learn", "deep learning"
        ],
        "secondary_skills": ["fastapi", "kubernetes", "c++", "triton", "rag", "langchain", "aws"],
        "related_roles": ["data_scientist", "backend_developer"]
    },
    "backend_developer": {
        "display_name": "Backend Engineer",
        "aliases": [
            "backend engineer", "backend developer", "software engineer - backend",
            "python backend developer", "java developer", "server engineer",
            "api engineer", "python engineer", "node.js developer",
            "software engineer", "senior engineer", "software developer", "engineer", "developer"
        ],
        "core_skills": [
            "python", "fastapi", "django", "flask", "postgresql", "mysql",
            "rest api", "graphql", "docker", "redis", "sqlalchemy", "microservices",
            "node.js", "java", "spring boot", "react"
        ],
        "secondary_skills": ["kubernetes", "aws", "git", "ci/cd", "celery", "rabbitmq"],
        "related_roles": ["fullstack_engineer", "devops_engineer"]
    },
    "devops_engineer": {
        "display_name": "DevOps Engineer",
        "aliases": [
            "devops engineer", "sre", "site reliability engineer",
            "infrastructure engineer", "cloud engineer", "platform engineer",
            "systems engineer", "cloud architect"
        ],
        "core_skills": [
            "kubernetes", "docker", "terraform", "ci/cd", "aws", "gcp", "azure",
            "ansible", "linux", "bash", "prometheus", "grafana", "helm", "cloudformation"
        ],
        "secondary_skills": ["python", "golang", "networking", "security", "vault", "jenkins"],
        "related_roles": ["backend_developer"]
    },
    "data_analyst": {
        "display_name": "Data Analyst",
        "aliases": [
            "data analyst", "bi analyst", "business intelligence analyst",
            "analytics engineer", "reporting analyst", "data operations analyst"
        ],
        "core_skills": [
            "sql", "tableau", "power bi", "excel", "python", "eda",
            "data visualization", "a/b testing", "google analytics", "looker", "dashboarding"
        ],
        "secondary_skills": ["pandas", "statistics", "r", "dbt", "snowflake"],
        "related_roles": ["data_scientist"]
    },
    "fullstack_engineer": {
        "display_name": "Full Stack Engineer",
        "aliases": [
            "full stack engineer", "full stack developer", "fullstack engineer",
            "software engineer", "web developer", "senior engineer", "software developer"
        ],
        "core_skills": [
            "javascript", "typescript", "react", "node.js", "python",
            "html", "css", "postgresql", "rest api", "next.js"
        ],
        "secondary_skills": ["docker", "fastapi", "mongodb", "tailwind", "aws"],
        "related_roles": ["backend_developer"]
    }
}

def get_canonical_role_id(title_or_role: str) -> Optional[str]:
    """
    Deterministically matches a role title string against the Role Ontology aliases.
    """
    if not title_or_role:
        return None
    
    clean_text = title_or_role.lower().strip()
    
    # 1. Exact or alias match
    for role_id, info in ROLE_TAXONOMY.items():
        for alias in info["aliases"]:
            if alias in clean_text or clean_text in alias:
                return role_id
                
    # 2. Token overlap fallback
    for role_id, info in ROLE_TAXONOMY.items():
        words = info["display_name"].lower().split()
        if all(w in clean_text for w in words):
            return role_id
            
    return None

def resolve_target_role(jd_text: str, target_role_hint: str = "") -> Dict[str, str]:
    """
    Deterministically resolves target role ID and clean display title.
    """
    if target_role_hint:
        role_id = get_canonical_role_id(target_role_hint)
        if role_id:
            return {"role_id": role_id, "display_name": ROLE_TAXONOMY[role_id]["display_name"]}
            
    # Try resolving from JD text
    if jd_text:
        role_id = get_canonical_role_id(jd_text[:300])
        if role_id:
            return {"role_id": role_id, "display_name": ROLE_TAXONOMY[role_id]["display_name"]}
            
        # Keyword sweep across JD
        jd_lower = jd_text.lower()
        for r_id, info in ROLE_TAXONOMY.items():
            if any(alias in jd_lower for alias in info["aliases"]):
                return {"role_id": r_id, "display_name": info["display_name"]}
                
    return {"role_id": "backend_developer", "display_name": "Software Engineer"}

def calculate_role_fit_score(parsed_resume: Dict[str, Any], target_role_id: str) -> Dict[str, Any]:
    """
    Calculates Role Fit (0-100%) deterministically using title history, core skill overlap, and duty signatures.
    """
    role_meta = ROLE_TAXONOMY.get(target_role_id)
    if not role_meta:
        role_meta = ROLE_TAXONOMY["backend_developer"]

    work_history = parsed_resume.get("work_history", [])
    candidate_skills = set()
    
    # Collect candidate skills
    if isinstance(parsed_resume.get("skills"), dict):
        for cat, slist in parsed_resume["skills"].items():
            if isinstance(slist, list):
                for s in slist:
                    candidate_skills.add(str(s).lower())
    if isinstance(parsed_resume.get("hard_skills"), list):
        for s in parsed_resume["hard_skills"]:
            candidate_skills.add(str(s).lower())

    # 1. Direct Title Match Score (weight: 50%)
    title_score = 60 if work_history else 40  # Baseline for candidate with work entries
    title_reasons = []
    
    for idx, w in enumerate(work_history):
        if not isinstance(w, dict):
            continue
        role_title = w.get("role", "").lower()
        matched_canonical = get_canonical_role_id(role_title)
        
        if matched_canonical == target_role_id:
            weight_bonus = 35 if idx == 0 else 25
            title_score = min(100, title_score + weight_bonus)
            title_reasons.append(f"Held direct title matching '{role_meta['display_name']}': {w.get('role')} at {w.get('company')}")
        elif matched_canonical in role_meta.get("related_roles", []):
            title_score = min(100, title_score + 20)
            title_reasons.append(f"Held related role: {w.get('role')}")

    # 2. Core Skill Signature Overlap (weight: 50%)
    core_skills = role_meta["core_skills"]
    matched_core = [s for s in core_skills if any(cs in s or s in cs for cs in candidate_skills)]
    if matched_core:
        skill_overlap_score = min(100, max(75, int((len(matched_core) / max(1, len(core_skills))) * 100 + 50)))
    else:
        skill_overlap_score = 40

    # 3. Final Deterministic Aggregation
    role_fit_score = int(0.50 * title_score + 0.50 * skill_overlap_score)
    role_fit_score = max(10, min(99, role_fit_score))

    reasoning = (
        f"Role Fit evaluated against target profession '{role_meta['display_name']}'. "
        f"Title Alignment Score: {title_score}%, Skill Signature Overlap: {len(matched_core)} matched core skills ({skill_overlap_score}%)."
    )

    return {
        "score": role_fit_score,
        "confidence": 95,
        "reasoning": reasoning,
        "title_matches": title_reasons,
        "matched_core_skills": matched_core
    }
