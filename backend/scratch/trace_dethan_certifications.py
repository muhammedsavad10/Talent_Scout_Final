import sys
import json
from app.agents.ingestion import split_resume_into_sections, parse_resume_to_json
from app.agents.deterministic_extractor import extract_certifications_deterministically
from app.core.hiring_priority import extract_candidate_evidence, compute_hiring_priority_score

raw_text_dethan = """Devadethan R
Email: dethan@example.com
Phone: +91 9876543210

CERTIFICATIONS
- Google AI Essentials
- IBM AI Engineering Professional Certification
- Google Kubernetes Engine (GKE)
- Tableau Certified
- Certified Data Scientist

EXPERIENCE
Data Scientist L1 at Prevalent AI (2023 - Present)
Deployed AWS Bedrock, LLMOps, FastAPI microservices, Docker, Kubernetes, CI/CD, PySpark.

AI Developer at DifferentByte (2022 - 2023)
Built LangChain and LangGraph REST APIs using PySpark and Django REST.

PROJECTS
AWS Bedrock LLMOps Platform
Built cloud-native LLM orchestrator using FastAPI and Kubernetes.
"""

print("=== STAGE AUDIT RUN ===")

# Stage A: Raw Resume Text
has_certs_raw = "CERTIFICATIONS" in raw_text_dethan or "Google AI Essentials" in raw_text_dethan
count_raw = 5 if has_certs_raw else 0
print(f"Stage A - Raw Resume Text: count={count_raw}")

# Stage B: Section Splitter
sections = split_resume_into_sections(raw_text_dethan)
cert_sec = sections.get("certifications", "")
print(f"Stage B - Section Splitter: keys={list(sections.keys())}")
print(f"Stage B - Section Splitter certifications text:\n{cert_sec}")
count_b = len([line for line in cert_sec.split('\n') if line.strip() and not line.strip().upper().startswith("CERTIFICATIONS")])
print(f"Stage B Count={count_b}")

# Stage C: Deterministic Extractor
det_certs = extract_certifications_deterministically(cert_sec or raw_text_dethan)
print(f"Stage C - Deterministic Extractor: {det_certs}")
count_c = len(det_certs)

# Stage D: Immediately before CandidateEvidence construction
# Simulate parsed_resume dict as returned by ingestion.py
parsed_resume = {
    "personal_info": {"name": "Devadethan R"},
    "certifications": det_certs,
    "work_history": [
        {"company": "Prevalent AI", "role": "Data Scientist L1", "dates": "2023 - Present", "description": "Deployed AWS Bedrock, LLMOps, FastAPI microservices."}
    ],
    "raw_resume_text": raw_text_dethan
}
print(f"Stage D - Immediately before CandidateEvidence: {parsed_resume.get('certifications')}")
count_d = len(parsed_resume.get("certifications", []))

# Stage E: Immediately after CandidateEvidence construction
eval_payload = {"result": parsed_resume, "parsed_resume": parsed_resume, "raw_resume_text": raw_text_dethan}
evidence = extract_candidate_evidence(eval_payload, parsed_resume=parsed_resume)
print(f"Stage E - CandidateEvidence certifications: {evidence.certifications}")
count_e = len(evidence.certifications)

# Stage F: Immediately before Hiring Priority Engine
priority_input = eval_payload
print(f"Stage F - Priority Input certifications: {priority_input.get('result', {}).get('certifications')}")
count_f = len(priority_input.get('result', {}).get('certifications', []))

# Stage G: Inside Hiring Priority Engine
priority_res = compute_hiring_priority_score(priority_input, parsed_resume=parsed_resume)
print(f"Stage G - Hiring Priority Engine certifications: {priority_res.get('certifications')}")
count_g = len(priority_res.get('certifications', []))

# Stage H: Immediately before API serialization
full_api_response = {
    "evaluation_id": "eval_dethan_test",
    "candidate_name": priority_res["professional_profile"]["candidate_name"],
    "result": priority_res,
    "hiring_priority": priority_res,
    "professional_profile": priority_res["professional_profile"],
    "certifications": priority_res["certifications"],
    "production_indicators": priority_res["production_indicators"],
    "personal_projects": priority_res["personal_projects"]
}
print(f"Stage H - API Serializer certifications: {full_api_response['hiring_priority']['certifications']}")
count_h = len(full_api_response['hiring_priority']['certifications'])

print("\n" + "="*40)
print(f"{'Stage':<30} {'Count':<10}")
print("="*40)
print(f"{'Raw Resume':<30} {count_raw:<10}")
print(f"{'Section Splitter':<30} {count_b:<10}")
print(f"{'Deterministic Extractor':<30} {count_c:<10}")
print(f"{'Parsed Resume':<30} {count_d:<10}")
print(f"{'CandidateEvidence':<30} {count_e:<10}")
print(f"{'Hiring Priority':<30} {count_g:<10}")
print(f"{'Serializer':<30} {count_h:<10}")
print(f"{'Final API':<30} {count_h:<10}")
print("="*40)
