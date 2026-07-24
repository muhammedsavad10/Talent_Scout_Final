"""
Deterministic Prerequisite Ontology, Concept Support & Equivalence Engine for TalentScout Enterprise.
Loads skill prerequisites, higher-level concept support, and conservative technology equivalences
from YAML configuration. Performs evidence-backed inferences and equivalent technology matches.
"""
import os
import logging
from typing import Dict, List, Any, Set

logger = logging.getLogger("talentscout_prerequisite_engine")

_CONFIG_CACHE = None

def _load_config() -> Dict[str, Any]:
    global _CONFIG_CACHE
    if _CONFIG_CACHE is not None:
        return _CONFIG_CACHE

    yaml_path = os.path.join(os.path.dirname(__file__), "skill_prerequisites.yaml")
    
    data = {
        "config": {
            "inference_credit_weight": 0.85,
            "senior_inference_credit_weight": 0.90,
            "concept_credit_weight": 0.85,
            "equivalent_credit_weight": 0.80,
            "preferred_credit_weight": 0.70
        },
        "foundational_skills": [
            "python", "javascript", "java", "c#", "c++", "go", "rust",
            "ruby", "php", "sql", "git", "docker", "numpy", "pandas",
            "html", "css", "linux", "bash", "shell"
        ],
        "prerequisites": {},
        "concept_support": {},
        "equivalent_groups": {}
    }
    
    if os.path.exists(yaml_path):
        try:
            import yaml
            with open(yaml_path, "r", encoding="utf-8") as f:
                loaded = yaml.safe_load(f)
                if isinstance(loaded, dict):
                    data = loaded
        except ImportError:
            logger.warning("PyYAML not installed, using fallback parser for skill_prerequisites.yaml")
            data = _parse_yaml_fallback(yaml_path)
        except Exception as e:
            logger.error(f"Failed to load skill_prerequisites.yaml: {e}")

    _CONFIG_CACHE = data
    return _CONFIG_CACHE

def _parse_yaml_fallback(filepath: str) -> Dict[str, Any]:
    result = {
        "config": {
            "inference_credit_weight": 0.85,
            "senior_inference_credit_weight": 0.90,
            "concept_credit_weight": 0.85,
            "equivalent_credit_weight": 0.80,
            "preferred_credit_weight": 0.70
        },
        "foundational_skills": [
            "python", "javascript", "java", "c#", "c++", "go", "rust",
            "ruby", "php", "sql", "git", "docker", "numpy", "pandas",
            "html", "css", "linux", "bash", "shell"
        ],
        "prerequisites": {},
        "concept_support": {
            "feature engineering": ["scikit-learn", "xgboost", "catboost", "lightgbm", "production ml", "pandas"],
            "nlp": ["transformers", "bert", "llms", "hugging face", "rag", "spacy"]
        },
        "equivalent_groups": {
            "vector_databases": ["qdrant", "pinecone", "weaviate", "milvus", "chromadb", "faiss", "elasticsearch"]
        }
    }
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            lines = f.readlines()
        
        current_section = None
        for line in lines:
            line_str = line.strip()
            if not line_str or line_str.startswith("#"):
                continue
            if line_str == "config:":
                current_section = "config"
                continue
            elif line_str == "foundational_skills:":
                current_section = "foundational_skills"
                continue
            elif line_str == "prerequisites:":
                current_section = "prerequisites"
                continue
            elif line_str == "concept_support:":
                current_section = "concept_support"
                continue
            elif line_str == "equivalent_groups:":
                current_section = "equivalent_groups"
                continue
                
            if current_section == "config" and ":" in line_str:
                k, v = line_str.split(":", 1)
                k_clean = k.strip()
                v_clean = v.split("#")[0].strip()
                try:
                    if k_clean in result["config"]:
                        result["config"][k_clean] = float(v_clean)
                except ValueError:
                    pass
            elif current_section == "foundational_skills" and line_str.startswith("-"):
                sk = line_str.lstrip("-").strip().lower()
                if sk and sk not in result["foundational_skills"]:
                    result["foundational_skills"].append(sk)
            elif current_section in ("prerequisites", "concept_support") and ":" in line_str:
                k, v = line_str.split(":", 1)
                k = k.strip().lower()
                v_str = v.split("#")[0].strip()
                if v_str.startswith("[") and v_str.endswith("]"):
                    items = [x.strip().strip('"\'') for x in v_str[1:-1].split(",") if x.strip()]
                    result[current_section][k] = items
    except Exception as e:
        logger.error(f"Fallback YAML parser failed: {e}")
    return result

def get_inference_credit_weight(is_senior: bool = False) -> float:
    cfg = _load_config()
    cfg_dict = cfg.get("config", {})
    if is_senior:
        return float(cfg_dict.get("senior_inference_credit_weight", 0.90))
    return float(cfg_dict.get("inference_credit_weight", 0.85))

def get_equivalent_credit_weight() -> float:
    cfg = _load_config()
    return float(cfg.get("config", {}).get("equivalent_credit_weight", 0.80))

def classify_skill_category(skill_name: str) -> str:
    if not skill_name or not isinstance(skill_name, str):
        return "Critical"
    clean_lower = skill_name.strip().lower()
    cfg = _load_config()

    foundational_list = [s.lower().strip() for s in cfg.get("foundational_skills", [])]
    if clean_lower in foundational_list:
        return "Foundational"

    critical_list = [s.lower().strip() for s in cfg.get("critical_skills", [])]
    if clean_lower in critical_list:
        return "Critical"

    preferred_list = [s.lower().strip() for s in cfg.get("preferred_skills", [])]
    if clean_lower in preferred_list:
        return "Preferred"

    important_list = [s.lower().strip() for s in cfg.get("important_skills", [])]
    if clean_lower in important_list:
        return "Important"

    return "Important" if len(clean_lower.split()) == 1 else "Critical"

def is_senior_candidate(parsed_resume: Dict[str, Any]) -> bool:
    work_entries = parsed_resume.get("work_history", [])
    years_est = len(work_entries) * 2
    if years_est >= 3:
        return True

    senior_keywords = ["senior", "lead", "principal", "staff", "architect", "head", "manager", "data scientist", "machine learning engineer", "ai engineer"]
    for w in work_entries:
        if isinstance(w, dict):
            role = (w.get("role") or w.get("title") or "").lower()
            if any(k in role for k in senior_keywords):
                return True

    raw_text = (parsed_resume.get("raw_resume_text") or "").lower()
    exp_list = parsed_resume.get("experience", [])
    exp_str = " ".join([str(e) for e in exp_list]).lower()
    full_str = f"{raw_text} {exp_str}"
    
    if any(k in full_str for k in senior_keywords):
        return True

    return False

def find_equivalent_technology(required_skill: str, candidate_skills_lower_set: Set[str]) -> List[str]:
    """
    Checks if candidate possesses an equivalent technology in the exact same domain group.
    e.g. Qdrant missing, but candidate has Pinecone or FAISS.
    """
    cfg = _load_config()
    groups = cfg.get("equivalent_groups", {})
    req_clean = required_skill.lower().strip()
    
    equivalent_matches = []
    for group_name, members in groups.items():
        members_lower = [m.lower().strip() for m in members]
        if req_clean in members_lower:
            for cand_skill in candidate_skills_lower_set:
                if cand_skill in members_lower and cand_skill != req_clean:
                    equivalent_matches.append(cand_skill)
    return equivalent_matches

def check_concept_support(required_skill: str, candidate_skills_lower_set: Set[str]) -> List[str]:
    """
    Checks if higher-level concept (e.g. Feature Engineering, NLP) is strongly supported
    by specialized tools or projects on the resume.
    """
    cfg = _load_config()
    concept_map = cfg.get("concept_support", {})
    req_clean = required_skill.lower().strip()
    supporting_techs = concept_map.get(req_clean, [])
    
    matches = []
    for tech in supporting_techs:
        tech_lower = tech.lower().strip()
        if tech_lower in candidate_skills_lower_set:
            matches.append(tech)
    return matches

def get_prerequisites_for_skill(advanced_skill: str) -> List[str]:
    cfg = _load_config()
    prereqs = cfg.get("prerequisites", {})
    return prereqs.get(advanced_skill.lower().strip(), [])

def infer_foundational_skills(
    candidate_skills_set: Set[str],
    required_skills: List[str],
    parsed_resume: Dict[str, Any] = None
) -> Dict[str, Any]:
    matched = []
    inferred = []
    equivalent = []
    missing = []
    inferred_details: Dict[str, Any] = {}
    
    cfg = _load_config()
    prereq_map = cfg.get("prerequisites", {})
    
    is_senior = is_senior_candidate(parsed_resume or {})
    credit_weight = get_inference_credit_weight(is_senior=is_senior)
    equiv_weight = get_equivalent_credit_weight()

    cand_lower_map = {s.lower().strip(): s for s in candidate_skills_set}
    cand_lower_set = set(cand_lower_map.keys())

    # Map which candidate skills trigger which foundational prerequisites
    trigger_map: Dict[str, List[str]] = {}
    for cand_skill_lower, original_cand_name in cand_lower_map.items():
        foundations = prereq_map.get(cand_skill_lower, [])
        for f in foundations:
            f_lower = f.lower().strip()
            if f_lower not in trigger_map:
                trigger_map[f_lower] = []
            if original_cand_name not in trigger_map[f_lower]:
                trigger_map[f_lower].append(original_cand_name)

    for req in required_skills:
        req_lower = req.lower().strip()
        category = classify_skill_category(req)
        
        # 1. Explicit Match (100% Credit)
        if req_lower in cand_lower_map:
            matched.append(req)
        # 2. Inferred Match via Prerequisite Ontology / Concept Support / Seniority
        elif req_lower in trigger_map:
            inferred.append(req)
            triggers = trigger_map[req_lower]
            inferred_details[req] = {
                "skill": req,
                "status": "INFERRED",
                "category": category,
                "triggered_by": triggers,
                "reason": f"Inferred foundation: {', '.join(triggers[:3])} detected on resume.",
                "credit": credit_weight
            }
        else:
            concept_matches = check_concept_support(req, cand_lower_set)
            if concept_matches:
                inferred.append(req)
                inferred_details[req] = {
                    "skill": req,
                    "status": "INFERRED",
                    "category": category,
                    "triggered_by": concept_matches,
                    "reason": f"Inferred concept: {req} is strongly supported by {', '.join(concept_matches[:3])}.",
                    "credit": credit_weight
                }
            elif is_senior and category == "Foundational":
                inferred.append(req)
                inferred_details[req] = {
                    "skill": req,
                    "status": "INFERRED",
                    "category": category,
                    "triggered_by": [],
                    "is_seniority_mitigated": True,
                    "reason": f"Seniority mitigated foundation: Demonstrated senior experience strongly implies {req} proficiency.",
                    "credit": credit_weight
                }
            else:
                # 3. Equivalent Technology Match (80% Credit)
                equiv_matches = find_equivalent_technology(req, cand_lower_set)
                if equiv_matches:
                    equivalent.append(req)
                    display_matches = [cand_lower_map.get(m, m) for m in equiv_matches]
                    inferred_details[req] = {
                        "skill": req,
                        "status": "EQUIVALENT",
                        "category": category,
                        "triggered_by": display_matches,
                        "reason": f"Equivalent technology: Candidate has experience with transferable technology ({', '.join(display_matches[:3])}).",
                        "credit": equiv_weight
                    }
                elif category == "Preferred":
                    pref_weight = float(cfg.get("config", {}).get("preferred_credit_weight", 0.70))
                    inferred.append(req)
                    inferred_details[req] = {
                        "skill": req,
                        "status": "PREFERRED_OMITTED",
                        "category": category,
                        "triggered_by": [],
                        "reason": f"Preferred optional skill '{req}' omitted (70% credit granted, no policy penalty).",
                        "credit": pref_weight
                    }
                # 4. Missing (0% Credit)
                else:
                    missing.append(req)

    return {
        "MATCHED": matched,
        "INFERRED": inferred,
        "EQUIVALENT": equivalent,
        "MISSING": missing,
        "inferred_details": inferred_details,
        "credit_weight": credit_weight,
        "equivalent_weight": equiv_weight,
        "is_senior_candidate": is_senior
    }
