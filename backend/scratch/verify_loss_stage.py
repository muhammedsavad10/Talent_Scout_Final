import asyncio
import json
from app.agents.ingestion import split_resume_into_sections, parse_resume_to_json
from app.agents.deterministic_extractor import extract_certifications_deterministically
from app.agents.orchestrator import run_evaluation_pipeline
from app.agents.comparator import compare_candidates
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

async def run_audit():
    print("===== END-TO-END STAGE TRACE FOR DETHAN.PDF =====")
    
    # Stage A: Raw Resume Text
    count_a = 5 if ("Google AI Essentials" in raw_text_dethan or "CERTIFICATIONS" in raw_text_dethan) else 0
    print(f"Stage A (Raw Resume): {count_a}")

    # Stage B: Section Splitter
    sections = split_resume_into_sections(raw_text_dethan)
    cert_text = sections.get("certifications", "")
    lines_b = [l for l in cert_text.split('\n') if l.strip() and "CERTIFICATIONS" not in l.upper()]
    count_b = len(lines_b)
    print(f"Stage B (Section Splitter): {count_b}")

    # Stage C: Deterministic Extractor
    det_certs = extract_certifications_deterministically(cert_text or raw_text_dethan)
    count_c = len(det_certs)
    print(f"Stage C (Deterministic Extractor): {count_c} ({det_certs})")

    # Stage D: Parsed Resume
    parsed_res = parse_resume_to_json(raw_text_dethan)
    count_d = len(parsed_res.get("certifications", []))
    print(f"Stage D (Parsed Resume): {count_d} ({parsed_res.get('certifications')})")

    # Stage E: CandidateEvidence
    eval_payload = {"result": parsed_res, "parsed_resume": parsed_res, "raw_resume_text": raw_text_dethan}
    evidence_e = extract_candidate_evidence(eval_payload, parsed_resume=parsed_res)
    count_e = len(evidence_e.certifications)
    print(f"Stage E (CandidateEvidence): {count_e}")

    # Stage F: Hiring Priority
    hp_f = compute_hiring_priority_score(eval_payload, parsed_resume=parsed_res)
    count_f = len(hp_f.get("certifications", []))
    print(f"Stage F (Hiring Priority): {count_f}")

    # Stage G: Pipeline Orchestrator & Serializer Output
    pipeline_res = await run_evaluation_pipeline(raw_text_dethan, "eval_dethan_test", [], "Data Scientist")
    
    # Check if hiring_priority is at root of pipeline_res or inside evaluation
    hp_in_orchestrator = pipeline_res.get("hiring_priority")
    count_g = len(hp_in_orchestrator.get("certifications", [])) if isinstance(hp_in_orchestrator, dict) else 0
    print(f"Stage G (Orchestrator Output hiring_priority present?): {hp_in_orchestrator is not None}, count={count_g}")

    # Stage H: Comparator / Final API Serializer
    ranked = compare_candidates([pipeline_res])
    first_cand = ranked[0] if ranked else {}
    hp_final = first_cand.get("hiring_priority", {})
    certs_final = hp_final.get("certifications", []) if isinstance(hp_final, dict) else []
    count_h = len(certs_final)
    print(f"Stage H (Final API / Comparator): {count_h}")

    print("\n" + "="*45)
    print(f"{'Stage':<25} {'Count':<10}")
    print("="*45)
    print(f"{'Raw Resume':<25} {count_a:<10}")
    print(f"{'Section Splitter':<25} {count_b:<10}")
    print(f"{'Deterministic Extractor':<25} {count_c:<10}")
    print(f"{'Parsed Resume':<25} {count_d:<10}")
    print(f"{'CandidateEvidence':<25} {count_e:<10}")
    print(f"{'Hiring Priority':<25} {count_f:<10}")
    print(f"{'Serializer (Orchestrator)':<25} {count_g:<10}")
    print(f"{'Final API (Comparator)':<25} {count_h:<10}")
    print("="*45)

if __name__ == "__main__":
    asyncio.run(run_audit())
