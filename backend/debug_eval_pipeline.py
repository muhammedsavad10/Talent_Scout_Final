import asyncio
import json
from app.agents.ingestion import split_resume_into_sections, parse_resume_to_json
from app.agents.normalization import normalize_skills_list
from app.agents.parser_validation import validate_parsed_resume
from app.agents.deterministic_extractor import extract_contact_info, extract_known_skills
from app.agents.scorer import run_scorer
from app.agents.policy_engine import evaluate_policy
from app.agents.strategy import generate_strategy
from app.agents.orchestrator import run_evaluation_pipeline

resume_text = """
Name: Ideal Candidate
Experience: Senior Engineer at TechCorp (2018-present).
Education: BS Computer Science.
I am a highly skilled engineer with 8 years of experience. My expertise includes Python, JavaScript, FastAPI, React, and Docker.
"""

required_skills = ["Python", "FastAPI", "Docker", "Kubernetes"]

def serialize_custom(obj):
    if hasattr(obj, "model_dump"):
        return obj.model_dump()
    if hasattr(obj, "dict"):
        return obj.dict()
    if hasattr(obj, "__dict__"):
        return obj.__dict__
    return str(obj)

async def main():
    print("=== START EVALUATION PIPELINE TRACE ===")
    
    # Stage 1: Deterministic Text Splitting
    print("\n[Stage 1a] Deterministic Text Splitting:")
    sections = split_resume_into_sections(resume_text)
    print(json.dumps(sections, indent=2))
    
    # Stage 1b: Parser (LLM)
    print("\n[Stage 1b] Parser (LLM):")
    parsed_resume = parse_resume_to_json(resume_text)
    print(json.dumps(parsed_resume, indent=2, default=serialize_custom))
    
    # Stage 2: Normalization
    print("\n[Stage 2] Normalization:")
    if "skills" in parsed_resume:
        for cat, skills_list in parsed_resume["skills"].items():
            if isinstance(skills_list, list):
                parsed_resume["skills"][cat] = normalize_skills_list(skills_list)
    if "hard_skills" in parsed_resume:
        parsed_resume["hard_skills"] = normalize_skills_list(parsed_resume["hard_skills"])
    print(json.dumps(parsed_resume, indent=2, default=serialize_custom))
    
    # Stage 3: Parser Validation
    print("\n[Stage 3] Parser Validation:")
    validation_report = validate_parsed_resume(parsed_resume)
    print(json.dumps(validation_report, indent=2, default=serialize_custom))
    
    # Stage 4: Deterministic Extraction
    print("\n[Stage 4] Deterministic Extraction:")
    contacts = extract_contact_info(resume_text)
    known_skills = extract_known_skills(resume_text, required_skills)
    parsed_resume["contacts"] = contacts
    if "hard_skills" not in parsed_resume:
        parsed_resume["hard_skills"] = []
    parsed_resume["hard_skills"].extend([s for s in known_skills if s not in parsed_resume["hard_skills"]])
    parsed_resume["hard_skills"] = normalize_skills_list(parsed_resume["hard_skills"])
    print(f"Contacts: {json.dumps(contacts, indent=2, default=serialize_custom)}")
    print(f"Known Skills: {json.dumps(known_skills, indent=2, default=serialize_custom)}")
    print(f"Merged Parsed Resume: {json.dumps(parsed_resume, indent=2, default=serialize_custom)}")
    
    # Stage 5: Scorer
    print("\n[Stage 5] Scorer:")
    scorer_output = run_scorer(parsed_resume, required_skills)
    print(json.dumps(scorer_output, indent=2, default=serialize_custom))
    
    # Stage 6: Policy Engine
    print("\n[Stage 6] Policy Engine:")
    policy_output = evaluate_policy(scorer_output, required_skills)
    print(json.dumps(policy_output, indent=2, default=serialize_custom))
    
    # Stage 7: Recommendation Strategy
    print("\n[Stage 7] Recommendation Strategy:")
    strategy_output = generate_strategy(scorer_output, policy_output)
    print(json.dumps(strategy_output, indent=2, default=serialize_custom))
    
    # Stage 8: Orchestrator Output
    print("\n[Stage 8] Unified Orchestrator Output:")
    result = await run_evaluation_pipeline(resume_text, "debug_id_123", required_skills)
    print(json.dumps(result, indent=2, default=serialize_custom))

if __name__ == "__main__":
    asyncio.run(main())
