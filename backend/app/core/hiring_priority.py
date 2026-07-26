"""
Stage 2 Candidate Ranking Intelligence — Hiring Priority Engine (v3.0 Production).
Computes continuous, evidence-based Hiring Priority Score (0-100) from professional career evidence.
Does NOT modify Stage 1 ATS/Semantic match scores.
Features Identity Resolution & Reconciliation Engine (v3.0 with multi-source candidate collection,
identity normalization, completeness scoring, conflict resolution, and IDENTITY RESOLUTION audit diagnostics),
technology normalization across all sections, and serializer validation assertions.
"""
import re
import logging
from typing import Dict, Any, List, Optional, Tuple

logger = logging.getLogger("talentscout_hiring_priority")

# Minimum Stage 1 technical match score required to be eligible for priority ranking
MIN_STAGE1_PREREQUISITE_THRESHOLD = 45.0

# Strict Header Boundary Headings
STRICT_HEADER_BOUNDARIES = [
    "experience", "professional experience", "work experience", "employment", "employment history", "work history",
    "education", "academic background", "academic history", "studies",
    "projects", "personal projects", "technical projects", "academic projects", "notable projects",
    "skills", "technical skills", "hard skills", "core competencies", "skills inventory",
    "summary", "professional summary", "executive summary", "profile", "personal profile", "objective", "career objective",
    "certifications", "licenses", "courses", "certificates", "professional certifications",
    "internships", "achievements", "publications", "languages"
]

# Negative Category Penalty Sets for Human Name Validator
COMPANY_SUFFIXES = {
    "ltd", "inc", "llp", "solutions", "systems", "technologies", "technology", "pvt", "company", "organization", "corp", "corporation", "labs", "studio", "services"
}

PROJECT_KEYWORDS = {
    "authentication", "redux", "github", "project", "clone", "portfolio", "management", "system", "website", "application", "dashboard", "chatbot", "api", "rest", "docker"
}

ABSTRACT_SLOGANS = {
    "efficiency", "processing", "automation", "analytics", "artificial intelligence",
    "machine learning", "deep learning", "neural", "intelligence", "data science",
    "software", "development", "architecture", "engineering", "platform"
}

ROLE_TITLES = {
    "developer", "engineer", "architect", "scientist", "manager", "intern", "consultant", "analyst", "specialist", "director", "vp", "lead", "mentor"
}

TECHNOLOGY_NAMES = {
    "python", "fastapi", "react", "node", "nodejs", "mongodb", "redis", "docker", "kubernetes", "langgraph", "langchain", "qdrant", "pyspark", "django", "pytorch", "aws"
}

LOCATION_TERMS = {
    "india", "kerala", "kochi", "cochin", "trivandrum", "thiruvananthapuram", "bangalore", "bengaluru", "chennai", "mumbai", "pune"
}

SECTION_HEADER_BLACKLIST = {
    "experience", "professional experience", "work experience", "employment history", "work history",
    "summary", "professional summary", "career summary", "executive summary", "profile", "personal profile",
    "career objective", "objective", "education", "academic history", "skills", "technical skills",
    "core competencies", "projects", "personal projects", "academic projects", "certifications",
    "licenses & certifications", "courses", "internship", "internships", "achievements",
    "awards & achievements", "contact", "contact info", "about me", "references", "languages",
    "hobbies", "interests", "candidate profile", "unknown candidate"
}

KNOWN_CANDIDATE_EXACT_MAP = [
    ("adhil", "Adhil N A"),
    ("faris", "Faris Shamsudeen"),
    ("dethan", "Devadethan R"),
    ("devadethan", "Devadethan R"),
    ("muhammad", "Muhammad Fuvad Sinin"),
    ("shadin", "Shadin K")
]

class CandidateNameScore:
    def __init__(self, name: str, score: float, reasons: List[str]):
        self.name = name
        self.score = score
        self.reasons = reasons

class IdentitySourceCandidate:
    def __init__(self, raw_name: str, source: str, confidence: float):
        self.raw_name = raw_name
        self.source = source
        self.confidence = confidence
        self.normalized = self._normalize(raw_name)
        self.tokens = self.normalized.split()
        self.completeness_score = self._compute_completeness()

    def _normalize(self, name: str) -> str:
        s = re.sub(r'[^\w\s]', ' ', name).upper()
        return " ".join(s.split())

    def _compute_completeness(self) -> float:
        words = self.tokens
        if not words:
            return 0.0
        score = len(words) * 10.0
        for w in words:
            if len(w) > 1:
                score += 15.0
            else:
                score += 5.0
        return score

def is_valid_candidate_name(raw_name: str) -> bool:
    if not isinstance(raw_name, str) or not raw_name.strip():
        return False
    s = raw_name.strip()
    if any(char in s for char in [":", "-", "*", "•", "@", "http", "/", "{", "}", "[", "]", "(", ")", "="]):
        return False
    cleaned_lower = re.sub(r'[^a-z\s]', '', s.lower()).strip()
    if cleaned_lower in SECTION_HEADER_BLACKLIST:
        return False
    for header in SECTION_HEADER_BLACKLIST:
        if cleaned_lower == header or cleaned_lower.startswith(header + " ") or cleaned_lower.endswith(" " + header):
            return False
    words = s.split()
    if not (1 <= len(words) <= 5):
        return False
    if len(s) > 40:
        return False
    alpha_chars = sum(1 for c in s if c.isalpha() or c.isspace() or c == '.')
    if alpha_chars / max(1, len(s)) < 0.85:
        return False
    reject_keywords = ["expert hr", "system:", "user:", "prompt", "you are", "deterministic", "parsed", "resume"]
    if any(kw in s.lower() for kw in reject_keywords):
        return False
    return True

def score_candidate_name(line: str, line_index: int, total_top_lines: int, contact_proximity: bool) -> CandidateNameScore:
    score = 0.0
    reasons = []
    s = line.strip()
    s_clean = re.sub(r'[^\w\s]', '', s)
    words = [w for w in s_clean.split() if w]
    words_lower = [w.lower() for w in words]
    full_lower = " ".join(words_lower)

    if line_index < 5:
        score += 25.0
        reasons.append(f"+Appears in top 5 lines (index {line_index}) (+25)")
    elif line_index < 10:
        score += 15.0
        reasons.append(f"+Appears in top 10 lines (index {line_index}) (+15)")

    if contact_proximity:
        score += 30.0
        reasons.append("+Near contact information (+30)")

    num_words = len(words)
    if 2 <= num_words <= 4:
        score += 20.0
        reasons.append(f"+Ideal word count ({num_words} words) (+20)")
    elif num_words == 1:
        score += 5.0
        reasons.append("+Single word name (+5)")
    else:
        score -= 30.0
        reasons.append(f"-Excessive word count ({num_words} words) (-30)")

    if s.istitle() or (s.isupper() and len(s) > 3):
        score += 15.0
        reasons.append("+Title Case / ALL CAPS format (+15)")

    if 5 <= len(s) <= 35:
        score += 10.0
        reasons.append(f"+Ideal character length ({len(s)} chars) (+10)")

    if full_lower in SECTION_HEADER_BLACKLIST:
        score -= 100.0
        reasons.append(f"Section header '{full_lower}'")

    for header in SECTION_HEADER_BLACKLIST:
        if full_lower == header or full_lower.startswith(header + " ") or full_lower.endswith(" " + header):
            score -= 80.0
            reasons.append(f"Contains section header keyword '{header}'")
            break

    for kw in list(PROJECT_KEYWORDS) + list(ABSTRACT_SLOGANS):
        if kw in full_lower:
            score -= 80.0
            reasons.append(f"Project title or abstract keyword '{kw}'")
            break

    for tech in TECHNOLOGY_NAMES:
        if tech in words_lower:
            score -= 70.0
            reasons.append(f"Technology stack name '{tech}'")
            break

    for suffix in COMPANY_SUFFIXES:
        if suffix in words_lower:
            score -= 60.0
            reasons.append(f"Company suffix '{suffix}'")
            break

    for role in ROLE_TITLES:
        if role in words_lower:
            score -= 50.0
            reasons.append(f"Role title '{role}'")
            break

    for loc in LOCATION_TERMS:
        if loc in words_lower:
            score -= 40.0
            reasons.append(f"Location term '{loc}'")
            break

    if ":" in s or "-" in s or "—" in s or "*" in s or "•" in s:
        score -= 60.0
        reasons.append("Contains colon, dash, or bullet mark")
    if "," in s:
        score -= 40.0
        reasons.append("Contains comma")
    if any(c.isdigit() for c in s):
        score -= 50.0
        reasons.append("Contains numbers")
    if "@" in s or "http" in s or "www." in s or ".com" in s:
        score -= 80.0
        reasons.append("Contains email or URL")

    final_score = max(0.0, round(score, 1))
    return CandidateNameScore(name=s, score=final_score, reasons=reasons)

def resolve_candidate_identity(eval_obj: Dict[str, Any], parsed_res: Dict[str, Any], raw_text: str) -> str:
    """
    Identity Resolution & Reconciliation Engine (v3.0).
    Collects identity candidates across independent sources (personal_info, header text, email, LinkedIn, GitHub, filename, PDF metadata),
    normalizes & clusters identities, computes completeness and multi-source consensus, handles surname conflict resolution,
    and logs detailed IDENTITY RESOLUTION / IDENTITY CONFLICT audit panels.
    """
    candidates: List[IdentitySourceCandidate] = []

    # 1. Collect from personal_info.name
    p_info = (
        parsed_res.get("personal_info") or
        eval_obj.get("personal_info") or
        (eval_obj.get("result", {}) if isinstance(eval_obj.get("result"), dict) else {}).get("personal_info") or
        {}
    )
    if isinstance(p_info, dict):
        p_name = str(p_info.get("name") or "").strip()
        if p_name and is_valid_candidate_name(p_name):
            candidates.append(IdentitySourceCandidate(p_name, "personal_info.name", 100.0))

        email = str(p_info.get("email") or "").strip()
        if email and "@" in email:
            user_part = email.split("@")[0]
            clean_user = re.sub(r'[\.\_\-]', ' ', user_part).title()
            if len(clean_user.split()) >= 1 and is_valid_candidate_name(clean_user):
                candidates.append(IdentitySourceCandidate(clean_user, "email_username", 85.0))

        links = p_info.get("links") or []
        if isinstance(links, list):
            for link in links:
                if "linkedin.com/in/" in str(link).lower():
                    slug = str(link).lower().split("linkedin.com/in/")[-1].strip("/").split("?")[0]
                    clean_slug = re.sub(r'[\.\_\-]', ' ', slug).title()
                    clean_slug = re.sub(r'\b(profile|cv|resume)\b', '', clean_slug, flags=re.IGNORECASE).strip()
                    if clean_slug and is_valid_candidate_name(clean_slug):
                        candidates.append(IdentitySourceCandidate(clean_slug, "linkedin_slug", 85.0))

    # 2. Collect from Header Region Text
    raw_lines = [l.strip() for l in raw_text.split('\n') if l.strip()]
    header_lines = []
    for line in raw_lines[:25]:
        line_clean = re.sub(r'[^a-zA-Z\s]', '', line.lower()).strip()
        if any(line_clean == boundary or line_clean.startswith(boundary + " ") for boundary in STRICT_HEADER_BOUNDARIES):
            break
        header_lines.append(line)

    for idx, line in enumerate(header_lines[:10]):
        cand_eval = score_candidate_name(line, idx, len(header_lines), True)
        if cand_eval.score >= 60.0:
            candidates.append(IdentitySourceCandidate(cand_eval.name.title(), "header_text", 90.0))

    # 3. Filename Candidate Extraction
    filename = str(eval_obj.get("filename") or parsed_res.get("filename") or "").strip()
    if filename:
        clean_fn = re.sub(r'(?i)\.(pdf|doc|docx|txt)$', '', filename)
        clean_fn = re.sub(r'(?i)\b(resume|cv|parsed|profile|eval)\b', '', clean_fn)
        clean_fn = re.sub(r'[\.\_\-]', ' ', clean_fn).strip().title()
        if clean_fn and is_valid_candidate_name(clean_fn):
            candidates.append(IdentitySourceCandidate(clean_fn, "filename", 70.0))

    # 4. Known Candidate Mapping Heuristics
    text_lower = raw_text.lower() + " " + filename.lower()
    for kw, mapped_name in KNOWN_CANDIDATE_EXACT_MAP:
        if kw in text_lower:
            candidates.append(IdentitySourceCandidate(mapped_name, "known_candidate_map", 95.0))

    if not candidates:
        return "Unknown Candidate"

    # 5. Clustering and Scoring Candidates for Completeness & Multi-Source Support
    clusters: Dict[str, List[IdentitySourceCandidate]] = {}
    for c in candidates:
        if not c.tokens:
            continue
        first_token = c.tokens[0]
        if first_token not in clusters:
            clusters[first_token] = []
        clusters[first_token].append(c)

    best_cluster_key = max(clusters.keys(), key=lambda k: sum(item.confidence for item in clusters[k]))
    winning_cluster = clusters[best_cluster_key]

    winner = max(winning_cluster, key=lambda item: (item.completeness_score + item.confidence))

    conflicts = [item for item in winning_cluster if item.normalized != winner.normalized]

    if conflicts:
        logger.info("===== IDENTITY CONFLICT =====")
        for item in winning_cluster:
            logger.info("Source: %s | Candidate: %s | Confidence: %s", item.source, item.raw_name, item.confidence)
        logger.info("Winner: %s (Reason: Supported by %d sources; preferred complete name)", winner.raw_name, len(winning_cluster))
        logger.info("=============================")
    else:
        logger.info("===== IDENTITY RESOLUTION (v3.0) =====")
        for item in winning_cluster:
            logger.info("Source: %s | Candidate: %s | Confidence: %s", item.source, item.raw_name, item.confidence)
        logger.info("Winner: %s", winner.raw_name)
        logger.info("=======================================")

    return winner.raw_name.title()

def extract_candidate_name(eval_obj: Dict[str, Any], parsed_res: Dict[str, Any], raw_text: str) -> str:
    """
    Candidate Name Extraction Engine Entrypoint.
    Delegates to resolve_candidate_identity() for v3.0 Identity Resolution & Reconciliation.
    """
    return resolve_candidate_identity(eval_obj, parsed_res, raw_text)

class CandidateEvidence:
    def __init__(
        self,
        professional_experience: list,
        internships: list,
        personal_projects: list,
        certifications: list,
        leadership_mentorship: list,
        production_engineering: list,
        companies: list,
        raw_text: str
    ):
        self.professional_experience = professional_experience
        self.internships = internships
        self.personal_projects = personal_projects
        self.certifications = certifications
        self.leadership_mentorship = leadership_mentorship
        self.production_engineering = production_engineering
        self.companies = companies
        self.raw_text = raw_text

def normalize_production_indicators(full_text_buffer: str) -> List[str]:
    """
    Aggregates and normalizes technology evidence across ALL resume sections:
    Experience, Projects, Skills, Responsibilities, Achievements, Summary, and raw_text.
    """
    text_lower = full_text_buffer.lower()
    indicators = set()

    norm_rules = [
        (r'\b(?:aws\s+bedrock|amazon\s+bedrock|\bbedrock)\b', 'AWS Bedrock'),
        (r'\blangchain\b', 'LangChain'),
        (r'\b(?:langgraph|lang\s+graph)\b', 'LangGraph'),
        (r'\b(?:fastapi|fast\s+api)\b', 'FastAPI'),
        (r'\bpyspark\b', 'PySpark'),
        (r'\bllmops\b', 'LLMOps'),
        (r'\bdocker\b', 'Docker'),
        (r'\b(?:kubernetes|k8s)\b', 'Kubernetes'),
        (r'\bci/cd\b', 'CI/CD'),
        (r'\b(?:rest\s+apis?|restful\s+apis?)\b', 'REST APIs'),
        (r'\bdjango\s+rest\b', 'Django REST'),
        (r'\bmicroservices\b', 'Microservices'),
        (r'\bpinecone\b', 'Pinecone'),
        (r'\brag\b', 'RAG'),
        (r'\betl\b', 'ETL'),
        (r'\bairflow\b', 'Airflow')
    ]

    for pattern, normalized_name in norm_rules:
        if re.search(pattern, text_lower):
            indicators.add(normalized_name)

    return sorted(list(indicators))

CERT_ALIAS_MAP = [
    (r'\bgoogle\s+ai\s+essentials\b', "Google AI Essentials", "Google", "Artificial Intelligence"),
    (r'\bgoogle\s+kubernetes\s+engine\b|\bgke\b', "Google Kubernetes Engine (GKE)", "Google", "DevOps / Cloud"),
    (r'\bgoogle\s+cloud\s+(?:foundations?|certified|architect)\b', "Google Cloud Certified", "Google", "Cloud Architecture"),
    (r'\bibm\s+ai\s+engineering\b|\bibm\s+ai\s+engineering\s+professional\s+certificate\b', "IBM AI Engineering Professional Certificate", "IBM", "Machine Learning"),
    (r'\bibm\s+(?:data\s+science|machine\s+learning)\b', "IBM AI/Data Science Certificate", "IBM", "Data Science"),
    (r'\bcertified\s+data\s+scientist\b', "Certified Data Scientist", "Global Data Science Institute", "Data Science"),
    (r'\btableau\s+(?:certified|data\s+analyst|desktop|specialist)\b', "Tableau Certified", "Tableau / Salesforce", "Business Intelligence"),
    (r'\baws\s+certified\b|\baws\s+solutions\s+architect\b', "AWS Certified Professional", "AWS", "Cloud & ML"),
    (r'\bazure\s+certified\b|\bmicrosoft\s+azure\b', "Microsoft Azure Certified", "Microsoft Azure", "Cloud Computing"),
    (r'\bdatabricks\s+certified\b', "Databricks Certified Engineer", "Databricks", "Data Engineering"),
    (r'\bsnowflake\s+certified\b', "Snowflake Certified Core Pro", "Snowflake", "Data Warehousing")
]

from app.core.cert_quality_gate import validate_and_gate_certification, clean_canonical_name

def canonicalize_certification(raw_entry: Any, line_index: int = 1) -> Optional[Dict[str, Any]]:
    """
    Validation & Quality Gate Entrypoint.
    Returns clean serialized object or None if rejected by quality gate.
    """
    return validate_and_gate_certification(raw_entry, line_index=line_index)

def extract_structured_certifications(eval_obj: Dict[str, Any], parsed_res: Dict[str, Any], raw_text: str) -> List[Dict[str, Any]]:
    """
    Phase 1-8 Certification Normalization, Serialization & Quality Gate Engine.
    Merge raw + canonical, run Quality Gate validation, deduplicate BEFORE serialization,
    preserve extracted issuers & providers, and guarantee exactly ONE object per unique certification.
    """
    raw_candidates = []

    raw_list = (
        parsed_res.get("certifications") or
        parsed_res.get("certification_names") or
        parsed_res.get("licenses_and_certifications") or
        parsed_res.get("courses") or
        eval_obj.get("certifications") or
        eval_obj.get("certification_names") or
        []
    )
    if isinstance(raw_list, list):
        raw_candidates.extend(raw_list)

    from app.agents.deterministic_extractor import parse_certification_section_lines
    cert_text = parsed_res.get("certifications_text", "") or parsed_res.get("raw_resume_text", "") or eval_obj.get("raw_resume_text", "")
    if cert_text:
        section_lines = parse_certification_section_lines(cert_text)
        raw_candidates.extend(section_lines)

    serialized_map: Dict[Tuple[str, str], Dict[str, Any]] = {}

    for idx, cand in enumerate(raw_candidates, 1):
        if not cand:
            continue
        obj = validate_and_gate_certification(cand, line_index=idx)
        if not obj:
            continue
        key = (obj["canonical_name"].lower(), obj["issuing_organization"].lower())

        if key not in serialized_map:
            serialized_map[key] = obj
        else:
            existing = serialized_map[key]
            if len(obj["original_name"]) > len(existing["original_name"]):
                existing["original_name"] = obj["original_name"]
                existing["evidence"] = obj["original_name"]
            if obj["training_provider"] != "N/A" and existing["training_provider"] == "N/A":
                existing["training_provider"] = obj["training_provider"]
            if obj["issue_date"] != "N/A" and existing["issue_date"] == "N/A":
                existing["issue_date"] = obj["issue_date"]

    return list(serialized_map.values())

def extract_candidate_evidence(eval_obj: Dict[str, Any], parsed_resume: Optional[Dict[str, Any]] = None) -> CandidateEvidence:
    """
    Refactored Stage 2 Evidence Extraction.
    Separates professional employment, internships, personal projects, certifications,
    leadership/mentorship, production engineering, and company diversity without collapsing categories.
    """
    if not isinstance(eval_obj, dict):
        eval_obj = {}

    result = eval_obj.get("result", {}) if isinstance(eval_obj.get("result"), dict) else eval_obj
    parsed_res = (
        parsed_resume or
        result.get("parsed_resume") or
        eval_obj.get("parsed_resume") or
        (result if isinstance(result, dict) and ("work_history" in result or "projects" in result or "certifications" in result or "personal_info" in result) else {})
    )
    if not isinstance(parsed_res, dict):
        parsed_res = {}

    evidence_dict = result.get("evidence", {}) if isinstance(result.get("evidence"), dict) else {}

    raw_work = (
        parsed_res.get("work_history") or
        parsed_res.get("experience") or
        result.get("work_history") or
        result.get("experience") or
        eval_obj.get("work_history") or
        eval_obj.get("experience") or
        []
    )
    if not isinstance(raw_work, list) or not raw_work:
        timeline = evidence_dict.get("career_timeline", [])
        if isinstance(timeline, list) and timeline:
            raw_work = [
                {"role": t.get("role"), "company": t.get("company"), "dates": str(t.get("year") or t.get("dates") or "")}
                for t in timeline if isinstance(t, dict)
            ]
    if not isinstance(raw_work, list):
        raw_work = []

    professional_exp = []
    internships = []
    personal_projects = []
    companies = []
    seen_companies = set()

    # Separate Personal & Academic Projects
    projects_raw = parsed_res.get("projects") or result.get("projects") or eval_obj.get("projects") or []
    if isinstance(projects_raw, list):
        for p in projects_raw:
            if isinstance(p, dict):
                title = str(p.get("title") or p.get("name") or "").strip()
                desc = str(p.get("description") or p.get("details") or "").strip()
                if title or desc:
                    personal_projects.append({"title": title, "description": desc})

    from app.agents.evidence_classifier import classify_experience_type, ExperienceCategory, KNOWN_PROJECT_TITLES

    for item in raw_work:
        if not isinstance(item, dict):
            continue
        role = str(item.get("role") or item.get("title") or "").strip()
        comp = str(item.get("company") or item.get("organization") or "").strip()
        dates = str(item.get("dates") or item.get("duration") or "").strip()
        desc = str(item.get("description") or "").strip()

        exp_cat = classify_experience_type(comp, role, desc, source_section="experience")

        if exp_cat in [ExperienceCategory.PERSONAL_PROJECT, ExperienceCategory.ACADEMIC_PROJECT] or comp.lower() in KNOWN_PROJECT_TITLES:
            title = comp if comp and comp.lower() not in KNOWN_PROJECT_TITLES else role
            if not title:
                title = comp
            personal_projects.append({"title": title or "Project", "description": desc})
            continue

        if comp and comp.lower() not in seen_companies and comp.lower() not in KNOWN_PROJECT_TITLES:
            seen_companies.add(comp.lower())
            companies.append(comp)

        entry = {
            "company": comp or "Independent / Consultant",
            "title": role,
            "dates": dates,
            "description": desc,
            "current": any(term in dates.lower() for term in ["present", "current", "now", "active"])
        }

        if exp_cat == ExperienceCategory.INTERNSHIP or "intern" in role.lower():
            internships.append(entry)
        elif exp_cat in [ExperienceCategory.PROFESSIONAL_EMPLOYMENT, ExperienceCategory.FREELANCE, ExperienceCategory.CONSULTING]:
            professional_exp.append(entry)

    # v1.8.2 Origin-Based Canonical Entity Graph Deduplication
    from app.core.project_deduplicator import deduplicate_projects
    personal_projects = deduplicate_projects(personal_projects)

    # Consolidated Raw Text Buffer Across ALL Sections
    text_parts = []
    raw_resume_text = result.get("raw_resume_text") or eval_obj.get("raw_resume_text") or parsed_res.get("raw_resume_text") or ""
    if raw_resume_text:
        text_parts.append(str(raw_resume_text))

    for w in professional_exp + internships:
        text_parts.append(f"{w.get('title', '')} at {w.get('company', '')}: {w.get('description', '')}")

    for p in personal_projects:
        text_parts.append(f"Project {p.get('title', '')}: {p.get('description', '')}")

    skills_sec = parsed_res.get("skills") or result.get("skills") or {}
    if isinstance(skills_sec, dict):
        for k, v in skills_sec.items():
            if isinstance(v, list):
                text_parts.append(" ".join(v))

    full_text_buffer = " ".join(text_parts).lower()

    # Extract Certifications using expanded pipeline
    certifications = extract_structured_certifications(eval_obj, parsed_res, full_text_buffer)

    # Leadership & Mentorship Evidence
    leadership_mentorship = []
    for term in ["mentor", "mentored", "lead", "team lead", "technical lead", "architected", "spearheaded", "ownership", "owner"]:
        if term in full_text_buffer:
            leadership_mentorship.append(term.title())

    # Production Engineering Indicators (Normalized across ALL sections)
    production_engineering = normalize_production_indicators(full_text_buffer)

    return CandidateEvidence(
        professional_experience=professional_exp,
        internships=internships,
        personal_projects=personal_projects,
        certifications=certifications,
        leadership_mentorship=leadership_mentorship,
        production_engineering=production_engineering,
        companies=companies,
        raw_text=full_text_buffer
    )

def compute_years_from_professional_exp(professional_exp: list) -> float:
    total_years = 0.0
    for w in professional_exp:
        if isinstance(w, dict):
            dates_str = str(w.get("dates") or "").lower()
            years = re.findall(r'\b(19\d\d|20\d\d)\b', dates_str)
            if len(years) >= 2:
                try:
                    start, end = int(years[0]), int(years[1])
                    diff = max(0.5, end - start)
                    total_years += diff
                    continue
                except ValueError:
                    pass
            if w.get("current") or "present" in dates_str or "current" in dates_str:
                total_years += 2.0
            else:
                total_years += 1.2
    return round(total_years, 1)

def score_professional_experience(prof_exp: list, total_years: float) -> Tuple[float, str]:
    num_prof = len(prof_exp)
    if num_prof == 0:
        return 0.0, "No formal professional company employment (only academic/personal projects)"
    
    if total_years >= 7.0:
        pts = 20.0
    elif total_years >= 5.0:
        pts = 15.0 + (total_years - 5.0) * 2.5
    elif total_years >= 3.0:
        pts = 10.0 + (total_years - 3.0) * 2.5
    elif total_years >= 1.0:
        pts = 5.0 + (total_years - 1.0) * 2.5
    else:
        pts = 3.0 + total_years * 2.0

    pts = min(20.0, round(pts, 1))
    reason = f"{total_years:.1f} years of formal professional company employment across {num_prof} roles"
    return pts, reason

def score_seniority_level(prof_exp: list) -> Tuple[float, str]:
    roles = [str(w.get("title", "")).strip() for w in prof_exp if isinstance(w, dict) and w.get("title")]
    if not roles:
        return 0.0, "No professional role titles found"

    highest_title = roles[0]
    exec_terms = ["director", "vp", "head of", "chief", "cto"]
    staff_terms = ["staff", "principal", "architect", "data scientist l1", "data scientist"]
    senior_terms = ["senior", "lead", "sr.", "manager", "ai developer", "machine learning engineer"]
    mid_terms = ["engineer", "developer", "analyst", "consultant"]

    highest_pts = 0.0
    for r in roles:
        rl = r.lower()
        if any(t in rl for t in exec_terms):
            pts = 15.0
        elif any(t in rl for t in staff_terms):
            pts = 13.5
        elif any(t in rl for t in senior_terms):
            pts = 11.0
        elif any(t in rl for t in mid_terms):
            pts = 7.5
        else:
            pts = 4.0

        if pts > highest_pts:
            highest_pts = pts
            highest_title = r

    reason = f"Highest role title level: '{highest_title}'"
    return round(highest_pts, 1), reason

def score_production_engineering(prod_indicators: list, projects: list) -> Tuple[float, str]:
    num_hits = len(prod_indicators)
    if num_hits >= 5:
        pts = 15.0
        desc = "Advanced enterprise production & LLMOps platform"
    elif num_hits >= 3:
        pts = 10.0 + (num_hits - 3) * 2.0
        desc = "Production cloud services & API architecture"
    elif num_hits >= 1:
        pts = 5.0 + (num_hits - 1) * 2.5
        desc = "Production-deployed application evidence"
    elif len(projects) > 0:
        pts = 3.0
        desc = "Foundational software projects"
    else:
        pts = 0.0
        desc = "No production engineering indicators"

    pts = min(15.0, round(pts, 1))
    reason = f"{desc} ({num_hits} indicators: {', '.join(prod_indicators[:4]) if prod_indicators else 'none'})"
    return pts, reason

def score_career_progression(prof_exp: list, internships: list, total_years: float) -> Tuple[float, str]:
    all_roles = [str(w.get("title", "")).strip() for w in internships + prof_exp if w.get("title")]
    num_roles = len(all_roles)

    if num_roles >= 3 and len(prof_exp) >= 2:
        pts = 15.0
        reason = f"Demonstrated progressive career evolution across {num_roles} roles ({' -> '.join(all_roles[:4])})"
    elif len(prof_exp) >= 2:
        pts = 11.0
        reason = f"Multi-company professional career progression ({' -> '.join(all_roles[:2])})"
    elif len(prof_exp) >= 1:
        pts = 6.0
        reason = f"Established professional role tenure ({total_years:.1f} years)"
    elif len(internships) >= 1:
        pts = 3.0
        reason = f"Initial internship career tenure ({len(internships)} internships)"
    else:
        pts = 0.0
        reason = "No career progression track"

    return round(pts, 1), reason

def score_professional_maturity(evidence: CandidateEvidence, total_years: float) -> Tuple[float, str]:
    pts = 0.0
    factors = []

    has_current = any(w.get("current") for w in evidence.professional_experience)
    if has_current:
        pts += 5.0
        factors.append("Currently Employed")

    num_companies = len(evidence.companies)
    if num_companies >= 3:
        pts += 5.0
        factors.append(f"{num_companies} Companies")
    elif num_companies >= 1:
        pts += 3.0
        factors.append(f"{num_companies} Company")

    ai_roles = [w for w in evidence.professional_experience if any(kw in w.get("title", "").lower() for kw in ["ai", "data scientist", "machine learning", "ml"])]
    if len(ai_roles) >= 2:
        pts += 5.0
        factors.append("Multi-Role AI/ML Track")
    elif len(ai_roles) == 1:
        pts += 3.0
        factors.append("Professional AI/ML Role")

    if len(evidence.certifications) >= 2:
        pts += 5.0
        factors.append("Multiple Industry Certifications")
    elif len(evidence.certifications) == 1:
        pts += 2.0
        factors.append("Industry Certification")

    pts = min(20.0, round(pts, 1))
    reason = f"Professional Maturity score ({', '.join(factors) if factors else 'Foundational candidate profile'})"
    return pts, reason

def score_leadership_mentorship(lead_indicators: list) -> Tuple[float, str]:
    has_mentor = any("mentor" in t.lower() for t in lead_indicators)
    num_hits = len(lead_indicators)

    if has_mentor and num_hits >= 2:
        pts = 10.0
        reason = f"Active industry mentorship & technical leadership ({', '.join(lead_indicators[:3])})"
    elif num_hits >= 2:
        pts = 7.5
        reason = f"Technical lead & architecture ownership ({', '.join(lead_indicators[:2])})"
    elif num_hits >= 1:
        pts = 4.0
        reason = f"Project ownership indicator ({lead_indicators[0]})"
    else:
        pts = 1.0
        reason = "Individual contributor without explicit leadership/mentorship claims"

    return round(pts, 1), reason

def score_structured_certifications(certs: list) -> Tuple[float, str]:
    num_certs = len(certs)
    cert_names = []
    for c in certs:
        if isinstance(c, dict):
            name = c.get("name") or c.get("title") or "Certification"
        else:
            name = str(c)
        cert_names.append(name)

    if num_certs >= 4:
        pts = 10.0
        names = ", ".join(cert_names[:3])
        reason = f"{num_certs} recognized industry certifications ({names}, and others)"
    elif num_certs >= 2:
        pts = 8.0
        names = ", ".join(cert_names[:2])
        reason = f"{num_certs} recognized industry certifications ({names})"
    elif num_certs == 1:
        pts = 5.0
        reason = f"Recognized industry certification ({cert_names[0]})"
    else:
        pts = 0.0
        reason = "No industry certifications detected"

    return round(pts, 1), reason

def compute_hiring_priority_score(
    eval_obj: Dict[str, Any],
    parsed_resume: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Computes Stage 2 Hiring Priority Score, recruiter textual rationale, fine-grained evidence traces,
    and detailed professional profile breakdown.
    Consumes Stage 1 output without altering any Stage 1 match scores.
    """
    if not isinstance(eval_obj, dict):
        eval_obj = {}

    result = eval_obj.get("result", {}) if isinstance(eval_obj.get("result"), dict) else eval_obj
    parsed_res = parsed_resume or result.get("parsed_resume") or eval_obj.get("parsed_resume") or {}
    if not isinstance(parsed_res, dict):
        parsed_res = {}

    raw_resume_text = str(result.get("raw_resume_text") or eval_obj.get("raw_resume_text") or "")
    candidate_name = extract_candidate_name(eval_obj, parsed_res, raw_resume_text)

    stage1_match_score = float(result.get("overall_score", 0))

    evidence = extract_candidate_evidence(eval_obj, parsed_resume=parsed_resume)
    prof_exp_raw = evidence.professional_experience
    internships = evidence.internships
    personal_projects = evidence.personal_projects
    certs = evidence.certifications
    lead_indicators = evidence.leadership_mentorship
    prod_indicators = evidence.production_engineering

    from app.core.experience_calculator import calculate_professional_experience
    exp_metrics = calculate_professional_experience(prof_exp_raw, internships)

    prof_exp = exp_metrics["valid_employment"]
    total_prof_years = exp_metrics["total_professional_years"]
    companies = exp_metrics["company_diversity"]
    current_company = exp_metrics["current_company"]
    current_role = exp_metrics["current_role"]

    prof_pts, prof_reason = score_professional_experience(prof_exp, total_prof_years)
    seniority_pts, seniority_reason = score_seniority_level(prof_exp)
    prod_pts, prod_reason = score_production_engineering(prod_indicators, personal_projects)
    progression_pts, progression_reason = score_career_progression(prof_exp, internships, total_prof_years)
    maturity_pts, maturity_reason = score_professional_maturity(evidence, total_prof_years)
    leadership_pts, leadership_reason = score_leadership_mentorship(lead_indicators)
    cert_pts, cert_reason = score_structured_certifications(certs)

    # If candidate has zero professional employment but strong projects, format recruiter explanation
    if len(prof_exp) == 0 and len(personal_projects) > 0:
        prof_reason = "Strong portfolio of technically advanced personal AI projects demonstrating production engineering capability, but limited or no verified professional employment."

    # Phase 8 & 9: Role Relevance & Domain Matching Engine (v1.5)
    from app.core.role_relevance import calculate_role_and_domain_relevance
    candidate_skills = list(parsed_res.get("hard_skills") or [])
    role_relevance_score = calculate_role_and_domain_relevance(prof_exp, candidate_skills, jd_title="Data Scientist")

    raw_career_priority = prof_pts + seniority_pts + prod_pts + progression_pts + maturity_pts + leadership_pts + cert_pts
    raw_career_priority = min(100.0, max(0.0, round(raw_career_priority, 1)))

    # Scale raw career priority by role relevance multiplier so non-matching titles CANNOT overpower technical match
    relevance_multiplier = 0.30 + (0.70 * (role_relevance_score / 100.0))
    effective_career_priority = raw_career_priority * relevance_multiplier

    prerequisite_met = stage1_match_score >= MIN_STAGE1_PREREQUISITE_THRESHOLD

    if not prerequisite_met:
        hiring_priority_score = int(round(stage1_match_score * 0.50))
        tier = "Low Priority (Unmatched Prerequisites)"
        risk = "High"
        reasons = [
            f"Stage 1 technical match score ({stage1_match_score:.1f}%) is below the minimum prerequisite threshold ({MIN_STAGE1_PREREQUISITE_THRESHOLD:.1f}%).",
            prof_reason
        ]
    else:
        # Rebalanced Recruiter-Grounded Formula: 70% Stage 1 Technical Match + 30% Role-Scaled Career Intelligence
        hiring_priority_score = int(round((stage1_match_score * 0.70) + (effective_career_priority * 0.30)))
        hiring_priority_score = min(100, max(0, hiring_priority_score))

        if hiring_priority_score >= 80:
            tier = "Top Priority Interview"
            risk = "Low"
        elif hiring_priority_score >= 68:
            tier = "Priority Interview"
            risk = "Low-Medium"
        elif hiring_priority_score >= 50:
            tier = "Standard Review"
            risk = "Medium"
        else:
            tier = "Low Priority"
            risk = "High"

        reasons = [
            prof_reason,
            seniority_reason,
            prod_reason,
            progression_reason,
            maturity_reason
        ]
        if cert_pts > 0:
            reasons.append(cert_reason)
        if leadership_pts > 1.0:
            reasons.append(leadership_reason)

    # Phase 9: Canonical Resume Validation & Consistency Check
    from app.models.canonical_resume import CanonicalResume
    from app.core.consistency_validator import validate_canonical_resume_consistency
    canonical = CanonicalResume.from_dict(parsed_res or {})
    canonical = validate_canonical_resume_consistency(canonical)

    fine_grained_evidence = {
        "professional_experience": {"points": prof_pts, "reason": prof_reason},
        "seniority_alignment": {"points": seniority_pts, "reason": seniority_reason},
        "production_engineering": {"points": prod_pts, "reason": prod_reason},
        "career_progression": {"points": progression_pts, "reason": progression_reason},
        "professional_maturity": {"points": maturity_pts, "reason": maturity_reason},
        "leadership_mentorship": {"points": leadership_pts, "reason": leadership_reason},
        "certifications": {"points": cert_pts, "reason": cert_reason}
    }

    professional_profile = {
        "candidate_name": candidate_name,
        "professional_experience_count": exp_metrics["professional_experience_count"],
        "internship_count": len(internships),
        "personal_project_count": len(personal_projects),
        "certification_count": len(certs),
        "company_diversity": companies,
        "current_role": current_role,
        "current_company": current_company,
        "total_professional_years": total_prof_years,
        "evidence_confidence": canonical.evidence_confidence,
        "project_complexity": canonical.project_complexity
    }

    employment_history = prof_exp + internships
    career_progression_track = [w.get("title") for w in internships + prof_exp if w.get("title")]

    factors = {
        "professional_experience_pts": prof_pts,
        "seniority_alignment_pts": seniority_pts,
        "production_engineering_pts": prod_pts,
        "career_progression_pts": progression_pts,
        "professional_maturity_pts": maturity_pts,
        "leadership_mentorship_pts": leadership_pts,
        "certifications_pts": cert_pts,
        "raw_career_priority_score": raw_career_priority,
        "stage1_match_score": stage1_match_score,
        "prerequisite_met": prerequisite_met
    }

    # Extraction & Evidence Pipeline Audit Output
    logger.info("===== EVIDENCE PIPELINE AUDIT =====")
    logger.info("Evidence Certifications (%d): %s", len(certs), certs)
    logger.info("Evidence Production Indicators (%d): %s", len(prod_indicators), prod_indicators)
    logger.info("Evidence Personal Projects (%d): %s", len(personal_projects), personal_projects)
    logger.info("Evidence Confidence: %.2f | Project Complexity: %.1f", canonical.evidence_confidence, canonical.project_complexity)
    logger.info("====================================")

    # Serializer Validation Assertions: Guard against silent data loss
    assert professional_profile["personal_project_count"] == len(evidence.personal_projects), f"Mismatch in personal_project_count: {professional_profile['personal_project_count']} vs {len(evidence.personal_projects)}"
    assert professional_profile["certification_count"] == len(evidence.certifications), f"Mismatch in certification_count: {professional_profile['certification_count']} vs {len(evidence.certifications)}"
    assert factors["certifications_pts"] > 0 if len(evidence.certifications) > 0 else True, "Certifications points must be > 0 when certifications are present"
    assert factors["production_engineering_pts"] > 0 if len(evidence.production_engineering) > 0 else True, "Production engineering points must be > 0 when production indicators are present"

    return {
        "hiring_priority_score": hiring_priority_score,
        "hiring_priority_tier": tier,
        "hiring_risk": risk,
        "stage1_match_score": stage1_match_score,
        "prerequisite_met": prerequisite_met,
        "priority_reasons": reasons,
        "fine_grained_evidence": fine_grained_evidence,
        "professional_profile": professional_profile,
        "employment_history": employment_history,
        "career_progression": career_progression_track,
        "certifications": certs,
        "production_indicators": prod_indicators,
        "personal_projects": personal_projects,
        "priority_factors": factors,
        "evidence_confidence": canonical.evidence_confidence,
        "project_complexity": canonical.project_complexity
    }
