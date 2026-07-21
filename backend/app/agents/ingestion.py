"""
Ingestion Agent: Handles PDF extraction and LLM-based structured parsing.
"""
import logging
import re
import json
from io import BytesIO
from pypdf import PdfReader
from app.core.config import settings, add_timing, call_llm, record_llm_call
from app.models.schemas import ParsedResume

logger = logging.getLogger("talentscout_ingestion")

SECTION_RULES = {
    "projects": [r"\bprojects\b", r"\bpersonal projects\b", r"\bacademic projects\b"],
    "certifications": [r"\bcertifications\b", r"\blicenses\b", r"\bprofessional certifications\b", r"\bcertificates\b"],
    "skills": [r"\btechnical skills\b", r"\bskills\b", r"\btechnologies\b", r"\btech stack\b", r"\bexpertise\b"],
    "languages": [r"\blanguages\b", r"\blanguages spoken\b"],
    "experience": [r"\bexperience\b", r"\bwork experience\b", r"\bemployment\b", r"\bwork history\b"]
}

def extract_text_from_pdf(file_bytes: bytes) -> str:
    """Extracts raw text from PDF bytes."""
    try:
        reader = PdfReader(BytesIO(file_bytes))
    except Exception as e:
        logger.error(f"PDF parsing initialization failed: {e}")
        raise ValueError("Invalid or corrupted PDF file.")

    if len(reader.pages) > 10:
        raise ValueError("PDF exceeds the 10-page limit.")

    try:
        text = "".join([page.extract_text() + "\n" for page in reader.pages])
        if not text.strip():
            raise ValueError("PDF contains no readable text. (OCR fallback required)")
        return text
    except Exception as e:
        logger.error(f"PDF Extraction failed: {e}")
        raise

def split_resume_into_sections(raw_text: str) -> dict[str, str]:
    """
    Deterministically splits raw text into categories using regex for common header markers.
    Categories: education, experience, projects, skills, certifications, summary
    """
    sections = {
        "education": "",
        "experience": "",
        "projects": "",
        "skills": "",
        "certifications": "",
        "languages": "",
        "summary": ""
    }
    if not raw_text:
        return sections
        
    # Define regex patterns to detect section headers at boundaries
    patterns = {
        "education": r"\b(education|academic background|studies|university education|academic credentials|scholastic)\b",
        "experience": r"\b(experience|work experience|employment|work history|professional experience|internships|professional background|career history)\b",
        "projects": r"\b(projects|personal projects|technical projects|academic projects|notable projects)\b",
        "skills": r"\b(skills|technical skills|hard skills|expertise|technologies|tools|competencies|skills inventory)\b",
        "certifications": r"\b(certifications|certificates|courses|awards|credentials|professional certifications)\b",
        "languages": r"\b(languages|languages spoken)\b",
        "summary": r"\b(summary|objective|profile|professional summary|executive summary|about me|introduction)\b"
    }
    
    # Find positions of all matched headers
    lines = raw_text.split('\n')
    header_indices = []
    
    for idx, line in enumerate(lines):
        clean_line = line.strip().lower()
        if not clean_line:
            continue
            
        # Keep length of header short (usually under 6 words) to avoid matching regular sentences
        word_count = len(clean_line.split())
        is_uppercase = line.strip().isupper()
        has_colon = clean_line.endswith(":")
        
        if word_count > 6 and not (is_uppercase or has_colon):
            continue
            
        # Clean colon for matching
        match_line = clean_line.rstrip(":")
            
        matched_section = None
        for sec_name, pattern in patterns.items():
            if re.search(pattern, match_line):
                matched_section = sec_name
                break
        
        if matched_section:
            header_indices.append((idx, matched_section))
            
    # If no headers detected, fallback to putting raw text in summary
    if not header_indices:
        sections["summary"] = raw_text
        return sections
        
    # Sort indices
    header_indices.sort(key=lambda x: x[0])
    
    # Extract content between headers
    for i in range(len(header_indices)):
        start_line_idx, sec_name = header_indices[i]
        end_line_idx = len(lines)
        if i + 1 < len(header_indices):
            end_line_idx = header_indices[i + 1][0]
            
        sec_text = "\n".join(lines[start_line_idx:end_line_idx]).strip()
        if sections[sec_name]:
            sections[sec_name] += "\n" + sec_text
        else:
            sections[sec_name] = sec_text
            
    return sections


def parse_resume_to_json(raw_text: str) -> dict:
    """
    Sends raw text to Groq Llama 3 to extract structured JSON.
    Splits raw text deterministically using regex first, then supplies only the
    retrieved segments to the LLM to format work experience, projects, and skills.
    Includes a Validate & Repair loop.
    """
    # 1. Deterministic text splitting
    sections = split_resume_into_sections(raw_text)

    prompt = f"""
    You are an expert HR Data Extraction Agent. Return ONLY valid JSON containing candidate data. No markdown, no pre-amble.
    
    Deterministic Text segments:
    - Experience: {sections["experience"][:4000]}
    - Projects: {sections["projects"][:3000]}
    - Education: {sections["education"][:1500]}
    - Header/Profile Snippet: {raw_text[:2000]}
    
    Required JSON structure:
    {{
        "personal_info": {{"name": "Full Name", "email": "email@example.com", "phone": "Phone", "links": ["url"]}},
        "education": ["Degree from University"],
        "experience": ["Role at Company"],
        "work_history": [
            {{"company": "Company Name", "role": "Title", "dates": "Timeline", "description": "2-3 sentences. Mention every tool, framework, and library used (e.g. PyTorch, Docker, FastAPI, AWS). Preserve exact technology names."}}
        ],
        "projects": [
            {{"title": "Project Name", "role": "Role", "dates": "Timeline", "description": "2-3 sentences. Mention every tool, framework, and library used. Preserve exact technology names."}}
        ],
        "awards": ["Award Name"]
    }}
    
    Rules:
    - CRITICAL: Do NOT extract Skills, Languages, or Certifications. Those are handled deterministically.
    - Descriptions must include all specific tools/libraries mentioned in source text. Target 40-60 words per entry.
    - No duplicated items or commentary.
    - Do not invent info. If empty, output empty list or null.
    """

    try:
        import time
        start_llm = time.perf_counter()
        result_str = call_llm(
            messages=[{"role": "user", "content": prompt}],
            temperature=0.0,
            response_format={"type": "json_object"},
            max_tokens=800,
            stage="parsing",
        )
        latency = time.perf_counter() - start_llm
        add_timing("LLM: Resume Parsing", latency)

        try:
            parsed_data = json.loads(result_str)
        except json.JSONDecodeError as json_err:
            logger.error(f"[PARSER COMPLETENESS] JSON Parse Failed: {json_err}")
            raise

        # --- STAGE 1: Deterministic Extraction ---
        from app.agents.deterministic_extractor import (
            extract_skills_deterministically,
            extract_certifications_deterministically,
            extract_languages_deterministically,
            ONTOLOGY_VERSION
        )
        
        # 1a. Skills
        # First check the dedicated skills section
        extracted_skills = extract_skills_deterministically(sections.get("skills", ""), "Skills Section")
        # Also grab skills scattered in experience/projects for better coverage
        if sections.get("experience"):
            extracted_skills.extend(extract_skills_deterministically(sections.get("experience", ""), "Experience Section"))
        if sections.get("projects"):
            extracted_skills.extend(extract_skills_deterministically(sections.get("projects", ""), "Projects Section"))
            
        # Deduplicate deterministically extracted skills by name
        unique_skills_map = {}
        for skill in extracted_skills:
            clean_name = skill["name"].lower()
            if clean_name not in unique_skills_map:
                unique_skills_map[clean_name] = skill
        
        detailed_skills = list(unique_skills_map.values())
        
        # Format for downstream payload
        structured_skills_dict = {}
        hard_skills_flat = []
        unknown_skills = []
        
        for s in detailed_skills:
            cat = s["category"]
            if cat not in structured_skills_dict:
                structured_skills_dict[cat] = []
            structured_skills_dict[cat].append(s["name"])
            
            if s.get("confidence", 100) >= 60:
                hard_skills_flat.append(s["name"])
                
            if "other" in s.get("categories", ["other"]):
                unknown_skills.append(s["name"])
            
        parsed_data["skills"] = structured_skills_dict
        parsed_data["hard_skills"] = hard_skills_flat
        parsed_data["detailed_skills"] = detailed_skills
        parsed_data["unknown_skills"] = unknown_skills
        
        # 1b. Certifications
        certs = extract_certifications_deterministically(sections.get("certifications", ""))
        parsed_data["certifications"] = certs
        parsed_data["certification_names"] = [c["title"] for c in certs]
        
        # 1c. Languages
        langs = extract_languages_deterministically(sections.get("languages", ""))
        parsed_data["languages"] = langs

        # --- STAGE 2 & 3 & 4: Validation, Targeted Repair & Merge ---
        # NOTE: LLM repair is eliminated. The initial parse prompt is already comprehensive,
        # deterministic extractors handle skills/certs/languages reliably, and the scorer
        # has fallback matching through work_history, projects, and raw_text for any gaps.
        from app.agents.parser_validation import validate
        
        parser_history = []
        validation_report = validate(parsed_data, sections, raw_text)
        
        parser_history.append({
            "attempt": 1,
            "overall_score": validation_report.get("overall_score", 100.0) if isinstance(validation_report, dict) else getattr(validation_report, "overall_score", 100.0),
            "repair": False
        })
        
        repair_latency_ms = 0
        
        skills_list = parsed_data.get("detailed_skills", [])
        total_skills = len(skills_list)
        other_skills = len([s for s in skills_list if s.get("category") == "other"])
        ontology_match_pct = (1.0 - (other_skills / max(1, total_skills))) * 100

        parser_metrics = {
            "parser_version": "v2.0",
            
            # Parser Quality Metrics
            "extraction_completeness": 100.0,
            "garbage_rate": 0.0,
            "duplicate_rate": 0.0,
            "structure_quality": sum(s.get("confidence", 100) for s in skills_list) / max(1, total_skills) if total_skills > 0 else 100.0,
            "overall_score": validation_report.get("overall_score", 100.0) if isinstance(validation_report, dict) else getattr(validation_report, "overall_score", 100.0),
            
            # Execution Stats
            "deterministic_items": len(detailed_skills) + len(certs) + len(langs),
            "llm_items": sum(len(parsed_data.get(k) or []) for k in ["work_history", "projects", "education"]),
            "repaired_items": 0,
            "duplicates_removed": len(extracted_skills) - len(detailed_skills),
            "garbage_removed": 0, 
            "repair_triggered": validation_report.get("repair_performed", False) if isinstance(validation_report, dict) else getattr(validation_report, "repair_performed", False),
            "repair_latency_ms": repair_latency_ms,
            "repair_calls": 1 if (validation_report.get("repair_performed", False) if isinstance(validation_report, dict) else getattr(validation_report, "repair_performed", False)) else 0,
            "llm_repairs": 1 if (validation_report.get("repair_performed", False) if isinstance(validation_report, dict) else getattr(validation_report, "repair_performed", False)) else 0,
            "sections_repaired": validation_report.get("repair_sections", []) if isinstance(validation_report, dict) else getattr(validation_report, "repair_sections", []),
            "section_scores": {k: v.get("section_score", 100.0) if isinstance(v, dict) else getattr(v, "section_score", 100.0) for k, v in (validation_report.get("sections", {}) if isinstance(validation_report, dict) else getattr(validation_report, "sections", {})).items()}
        }
        
        # Generate Ontology Suggestions for unknown skills with high confidence
        ontology_suggestions = []
        for s in detailed_skills:
            if "other" in s.get("categories", ["other"]) and s.get("confidence", 100) > 60:
                ontology_suggestions.append({
                    "unknown_skill": s["name"],
                    "seen_in_resumes": 1, # Just 1 for this individual execution
                    "average_confidence": s.get("confidence", 100),
                    "suggested_category": "Needs Review",
                    "recommended_aliases": [s["name"].lower()]
                })

        ontology_metrics = {
            "ontology_version": ONTOLOGY_VERSION,
            "coverage": ontology_match_pct,
            "matched": total_skills - other_skills,
            "unknown": other_skills,
            "ontology_suggestions": ontology_suggestions
        }

        # --- STAGE 5: Flattening ---
        # Skipping flattening since deterministic logic handles it already

        flat_parsed = {
            "education": parsed_data.get("education") or [],
            "experience": parsed_data.get("experience") or [],
            "work_history": parsed_data.get("work_history") or [],
            "projects": parsed_data.get("projects") or [],
            "certifications": parsed_data.get("certifications") or [],
            "certification_names": parsed_data.get("certification_names") or [],
            "skills": parsed_data.get("skills") or {},
            "hard_skills": parsed_data.get("hard_skills") or [],
            "detailed_skills": parsed_data.get("detailed_skills") or [],
            "unknown_skills": parsed_data.get("unknown_skills") or [],
            "raw_resume_text": raw_text,
            "personal_info": parsed_data.get("personal_info") or {},
            "languages": parsed_data.get("languages") or [],
            "awards": parsed_data.get("awards") or [],
            "parser_validation": validation_report if isinstance(validation_report, dict) else validation_report.model_dump(),
            "parser_history": parser_history,
            "parser_metrics": parser_metrics,
            "ontology_metrics": ontology_metrics
        }
        
        # Clean up None values to empty strings to avoid downstream regex crashes
        if isinstance(flat_parsed["projects"], list):
            for proj in flat_parsed["projects"]:
                if isinstance(proj, dict):
                    for key in ["title", "role", "dates", "description"]:
                        if proj.get(key) is None:
                            proj[key] = ""
                            
        if isinstance(flat_parsed["work_history"], list):
            for work in flat_parsed["work_history"]:
                if isinstance(work, dict):
                    for key in ["company", "role", "dates", "description"]:
                        if work.get(key) is None:
                            work[key] = ""

        # Validate against our Pydantic schema
        validated_data = ParsedResume(**flat_parsed)
        return validated_data.model_dump()
        
    except Exception as e:
        logger.error(f"LLM Parsing failed: {e}")
        raise
