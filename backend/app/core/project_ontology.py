"""
Deterministic Project Ontology Module.
Categorizes projects into domain taxonomies and computes role project relevance.
"""
import re
import logging
from typing import Dict, Any, List

logger = logging.getLogger("talentscout_project_ontology")

PROJECT_DOMAINS: Dict[str, Dict[str, Any]] = {
    "ML_DATA_SCIENCE": {
        "name": "Machine Learning & AI",
        "keywords": [
            "predict", "prediction", "churn", "fraud", "classification", "regression",
            "nlp", "computer vision", "llm", "rag", "pytorch", "tensorflow", "scikit-learn",
            "model", "deep learning", "neural network", "transformers", "opencv", "bert"
        ],
        "weight_multiplier": 1.0
    },
    "BACKEND_SYSTEMS": {
        "name": "Backend & Distributed Systems",
        "keywords": [
            "fastapi", "django", "flask", "microservices", "rest api", "graphql",
            "database", "postgresql", "redis", "orm", "sqlalchemy", "serverless",
            "kafka", "rabbitmq", "api gateway"
        ],
        "weight_multiplier": 1.0
    },
    "DEVOPS_INFRASTRUCTURE": {
        "name": "DevOps & Cloud Infrastructure",
        "keywords": [
            "kubernetes", "docker", "terraform", "ci/cd", "ansible", "cloudformation",
            "aws", "gcp", "azure", "helm", "pipeline", "infrastructure"
        ],
        "weight_multiplier": 1.0
    },
    "DATA_ANALYTICS": {
        "name": "Data Analytics & BI",
        "keywords": [
            "tableau", "power bi", "dashboard", "etl", "sql", "excel", "reporting",
            "data warehouse", "snowflake", "bigquery"
        ],
        "weight_multiplier": 0.8
    },
    "GENERIC_CRUD": {
        "name": "Generic CRUD / Starter Application",
        "keywords": [
            "crud", "inventory", "management system", "hospital management", "todo",
            "blog", "portfolio", "sample app", "starter project", "calculator"
        ],
        "weight_multiplier": 0.3
    }
}

ROLE_DOMAIN_EXPECTATIONS: Dict[str, Dict[str, float]] = {
    "data_scientist": {
        "ML_DATA_SCIENCE": 1.0,
        "DATA_ANALYTICS": 0.75,
        "BACKEND_SYSTEMS": 0.50,
        "DEVOPS_INFRASTRUCTURE": 0.40,
        "GENERIC_CRUD": 0.20
    },
    "ml_engineer": {
        "ML_DATA_SCIENCE": 1.0,
        "BACKEND_SYSTEMS": 0.70,
        "DEVOPS_INFRASTRUCTURE": 0.65,
        "DATA_ANALYTICS": 0.50,
        "GENERIC_CRUD": 0.20
    },
    "backend_developer": {
        "BACKEND_SYSTEMS": 1.0,
        "DEVOPS_INFRASTRUCTURE": 0.70,
        "FULLSTACK_WEB": 0.65,
        "DATA_ANALYTICS": 0.50,
        "ML_DATA_SCIENCE": 0.50,
        "GENERIC_CRUD": 0.30
    },
    "devops_engineer": {
        "DEVOPS_INFRASTRUCTURE": 1.0,
        "BACKEND_SYSTEMS": 0.70,
        "GENERIC_CRUD": 0.20
    },
    "data_analyst": {
        "DATA_ANALYTICS": 1.0,
        "ML_DATA_SCIENCE": 0.70,
        "GENERIC_CRUD": 0.30
    }
}

def classify_project_domain(title: str, description: str) -> str:
    """
    Classifies a project into a semantic domain category.
    """
    combined_text = f"{title} {description}".lower()
    
    # 1. Check for Generic CRUD triggers first if simple keywords present
    if any(kw in combined_text for kw in PROJECT_DOMAINS["GENERIC_CRUD"]["keywords"]):
        # Verify it doesn't contain advanced ML/DevOps terms overriding it
        if not any(kw in combined_text for kw in ["pytorch", "tensorflow", "kubernetes", "llm", "rag"]):
            return "GENERIC_CRUD"

    # 2. Match against specialized domain taxonomies
    domain_scores = {}
    for domain_id, meta in PROJECT_DOMAINS.items():
        if domain_id == "GENERIC_CRUD":
            continue
        matches = sum(1 for kw in meta["keywords"] if kw in combined_text)
        if matches > 0:
            domain_scores[domain_id] = matches
            
    if domain_scores:
        # Return domain with highest keyword matches
        best_domain = max(domain_scores, key=domain_scores.get)
        return best_domain

    return "BACKEND_SYSTEMS"  # Default generic technical fallback

def calculate_project_relevance_score(parsed_resume: Dict[str, Any], target_role_id: str) -> Dict[str, Any]:
    """
    Deterministically computes Project Relevance score (0-100%) against target role.
    """
    projects = parsed_resume.get("projects", [])
    if not projects:
        return {
            "score": 60,
            "confidence": 80,
            "reasoning": "No explicit project items cataloged on resume profile.",
            "classified_projects": []
        }

    domain_weights = ROLE_DOMAIN_EXPECTATIONS.get(target_role_id, ROLE_DOMAIN_EXPECTATIONS["backend_developer"])
    classified = []
    total_relevance = 0.0

    for p in projects:
        if not isinstance(p, dict):
            continue
        title = p.get("title", "Project")
        desc = p.get("description", "")
        domain_cat = classify_project_domain(title, desc)
        
        rel_factor = domain_weights.get(domain_cat, 0.40)
        proj_score = int(rel_factor * 100)
        
        classified.append({
            "title": title,
            "domain": PROJECT_DOMAINS[domain_cat]["name"],
            "domain_id": domain_cat,
            "score": proj_score
        })
        total_relevance += rel_factor

    # Average relevance score across candidate projects
    avg_relevance = int((total_relevance / max(1, len(projects))) * 100)
    avg_relevance = max(15, min(98, avg_relevance))

    reasoning = (
        f"Evaluated {len(projects)} project(s) against target role. "
        f"Classified project domains: {', '.join([c['domain'] for c in classified])}."
    )

    return {
        "score": avg_relevance,
        "confidence": 90,
        "reasoning": reasoning,
        "classified_projects": classified
    }
