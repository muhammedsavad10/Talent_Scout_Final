"""
Multi-Domain Classification & Experience-Aware Domain Alignment Module.
Computes candidate multi-domain profiles with evidence and smooth penalty multipliers.
Eliminates single-label classification bottlenecks and rigid hard-cap cliffs.
"""
import re
from typing import Dict, Any, List

DOMAIN_TAXONOMY = {
    "data_science": {
        "display_name": "Data Science",
        "keywords": [
            "data scientist", "data science", "statistics", "statistical modeling",
            "predictive modeling", "scikit-learn", "pandas", "numpy", "feature engineering", "r", "eda", "experiment design"
        ]
    },
    "machine_learning": {
        "display_name": "Machine Learning",
        "keywords": [
            "ml engineer", "machine learning engineer", "deep learning", "pytorch",
            "tensorflow", "transformers", "llm", "llms", "vector search", "qdrant",
            "pinecone", "faiss", "cuda", "mlops", "onnx", "computer vision", "nlp"
        ]
    },
    "data_engineering": {
        "display_name": "Data Engineering",
        "keywords": [
            "data engineer", "data engineering", "etl", "spark", "airflow",
            "snowflake", "bigquery", "hadoop", "kafka", "data pipeline", "dbt", "redshift"
        ]
    },
    "backend_engineering": {
        "display_name": "Backend Engineering",
        "keywords": [
            "backend engineer", "backend developer", "python backend", "fastapi",
            "django", "flask", "java", "spring boot", "postgresql", "mysql",
            "rest api", "microservices", "sqlalchemy", "golang", "software engineer",
            "software developer", "software dev"
        ]
    },
    "frontend_engineering": {
        "display_name": "Frontend Engineering",
        "keywords": [
            "frontend engineer", "frontend developer", "react", "vue", "angular",
            "next.js", "tailwind", "redux", "ui engineer", "web design"
        ]
    },
    "fullstack_mern": {
        "display_name": "Full Stack / MERN",
        "keywords": [
            "full stack", "fullstack", "mern", "express", "mongodb", "node.js",
            "node", "react", "javascript", "typescript", "web developer"
        ]
    },
    "devops_cloud": {
        "display_name": "DevOps / Cloud",
        "keywords": [
            "devops", "sre", "kubernetes", "docker", "terraform", "aws",
            "azure", "gcp", "ci/cd", "ansible", "linux", "cloud engineer"
        ]
    },
    "mobile_development": {
        "display_name": "Mobile Development",
        "keywords": [
            "ios", "android", "flutter", "react native", "swift", "kotlin", "mobile developer"
        ]
    },
    "cybersecurity": {
        "display_name": "Cybersecurity",
        "keywords": [
            "security engineer", "penetration testing", "cissp", "soc", "siem", "cybersecurity"
        ]
    },
    "non_technical": {
        "display_name": "Non-Technical / Other",
        "keywords": [
            "graphic designer", "accountant", "accounting", "school teacher", "teacher",
            "mechanical engineer", "marketing manager", "sales representative", "hr specialist",
            "recruiter", "store manager", "customer service"
        ]
    }
}

ALIGNMENT_MATRIX = {
    ("data_science", "data_science"): 1.0,
    ("machine_learning", "machine_learning"): 1.0,
    ("data_engineering", "data_engineering"): 1.0,
    ("backend_engineering", "backend_engineering"): 1.0,
    ("frontend_engineering", "frontend_engineering"): 1.0,
    ("fullstack_mern", "fullstack_mern"): 1.0,
    ("devops_cloud", "devops_cloud"): 1.0,
    ("mobile_development", "mobile_development"): 1.0,
    ("cybersecurity", "cybersecurity"): 1.0,
    ("non_technical", "non_technical"): 1.0,

    # Empirical / Evidence-Driven Transition Weights
    ("data_science", "machine_learning"): 0.88,
    ("machine_learning", "data_science"): 0.88,

    ("data_science", "data_engineering"): 0.75,
    ("data_engineering", "data_science"): 0.75,

    ("machine_learning", "data_engineering"): 0.75,
    ("data_engineering", "machine_learning"): 0.75,

    ("data_science", "backend_engineering"): 0.60,
    ("backend_engineering", "data_science"): 0.60,

    ("machine_learning", "backend_engineering"): 0.65,
    ("backend_engineering", "machine_learning"): 0.65,

    ("fullstack_mern", "backend_engineering"): 0.75,
    ("backend_engineering", "fullstack_mern"): 0.75,

    ("devops_cloud", "backend_engineering"): 0.75,
    ("backend_engineering", "devops_cloud"): 0.75,

    ("fullstack_mern", "frontend_engineering"): 0.85,
    ("frontend_engineering", "fullstack_mern"): 0.85,

    # Cross Domains (Far)
    ("fullstack_mern", "data_science"): 0.25,
    ("data_science", "fullstack_mern"): 0.25,

    ("fullstack_mern", "machine_learning"): 0.30,
    ("machine_learning", "fullstack_mern"): 0.30,

    ("frontend_engineering", "data_science"): 0.20,
    ("data_science", "frontend_engineering"): 0.20,

    ("mobile_development", "data_science"): 0.20,
    ("data_science", "mobile_development"): 0.20,

    # Non-Technical Domain Gap
    ("non_technical", "data_science"): 0.05,
    ("data_science", "non_technical"): 0.05,
    ("non_technical", "backend_engineering"): 0.05,
    ("backend_engineering", "non_technical"): 0.05,
}

def classify_text_domain(text: str, role_title_hint: str = "") -> str:
    profiles = classify_multi_domain_profile(text, role_title_hint)
    return profiles[0]["domain_id"] if profiles else "backend_engineering"

def classify_multi_domain_profile(text: str, candidate_roles_hint: str = "") -> List[Dict[str, Any]]:
    combined = f"{candidate_roles_hint} {text}".lower()

    profiles = []
    total_hits = 0

    for dom_id, dom_data in DOMAIN_TAXONOMY.items():
        hit_evidence = []
        for kw in dom_data["keywords"]:
            if kw == "r":
                matched = re.search(r"\br\b", combined) is not None
            else:
                matched = kw in combined
            if matched:
                hit_evidence.append(kw.title())
        
        hit_count = len(hit_evidence)
        if hit_count > 0:
            total_hits += hit_count
            profiles.append({
                "domain_id": dom_id,
                "domain": dom_data["display_name"],
                "raw_hits": hit_count,
                "evidence": hit_evidence[:5]
            })

    if not profiles:
        return [{
            "domain_id": "non_technical",
            "domain": "Non-Technical / Other",
            "confidence": 0.10,
            "evidence": ["Unclassified / Non-Technical Context"]
        }]

    # Normalize confidence scores relative to max hits
    max_hits = max(p["raw_hits"] for p in profiles)
    for p in profiles:
        p["confidence"] = round(min(0.98, max(0.20, p["raw_hits"] / max_hits)), 2)

    profiles.sort(key=lambda x: x["confidence"], reverse=True)
    return profiles

def compute_multi_domain_alignment(
    candidate_profiles: List[Dict[str, Any]],
    jd_domain: str,
    years_experience: float = 0.0
) -> Dict[str, Any]:
    primary_domain = candidate_profiles[0]["domain"]
    primary_domain_id = candidate_profiles[0]["domain_id"]

    best_match_domain = primary_domain
    best_match_id = primary_domain_id

    if primary_domain_id == jd_domain:
        best_alignment_ratio = 1.0
    else:
        best_alignment_ratio = ALIGNMENT_MATRIX.get((primary_domain_id, jd_domain), 0.05)
    best_evidence = candidate_profiles[0].get("evidence", [])

    # Candidate domain MUST have at least 0.45 confidence to be selected as best_matching_domain
    for p in candidate_profiles:
        cand_id = p["domain_id"]
        if p.get("confidence", 0) < 0.45 and cand_id != primary_domain_id:
            continue

        if cand_id == jd_domain:
            ratio = 1.0
            effective_ratio = 1.0
        else:
            ratio = ALIGNMENT_MATRIX.get((cand_id, jd_domain), 0.05)
            effective_ratio = ratio * p.get("confidence", 0.50)
        if effective_ratio > best_alignment_ratio:
            best_alignment_ratio = effective_ratio
            best_match_domain = p["domain"]
            best_match_id = cand_id
            best_evidence = p.get("evidence", [])

    # Experience-Aware Domain Boost (Only for adjacent technical domains)
    exp_boost = 0.0
    if years_experience >= 5 and best_alignment_ratio >= 0.55 and best_alignment_ratio < 1.0:
        exp_boost = 0.10
    elif years_experience >= 3 and best_alignment_ratio >= 0.55 and best_alignment_ratio < 1.0:
        exp_boost = 0.05

    penalty_multiplier = min(1.0, max(0.05, best_alignment_ratio + exp_boost))
    alignment_score = int(round(penalty_multiplier * 100))

    jd_display = DOMAIN_TAXONOMY.get(jd_domain, {}).get("display_name", jd_domain)

    if penalty_multiplier >= 0.85:
        match_type = f"Direct Multi-Domain Alignment ({best_match_domain} -> {jd_display})"
        domain_cap = 100
    elif penalty_multiplier >= 0.55:
        match_type = f"Adjacent Domain Alignment ({best_match_domain} -> {jd_display})"
        domain_cap = 75
    elif penalty_multiplier >= 0.20:
        match_type = f"Cross-Domain Gap ({best_match_domain} -> {jd_display})"
        domain_cap = 45
    else:
        match_type = f"Unrelated / Non-Technical Gap ({best_match_domain} -> {jd_display})"
        domain_cap = 15

    return {
        "primary_domain": primary_domain,
        "best_matching_domain": best_match_domain,
        "jd_domain": jd_display,
        "alignment_score": alignment_score,
        "penalty_multiplier": round(penalty_multiplier, 2),
        "match_type": match_type,
        "domain_cap": domain_cap,
        "candidate_domains": candidate_profiles,
        "domain_evidence": best_evidence
    }
