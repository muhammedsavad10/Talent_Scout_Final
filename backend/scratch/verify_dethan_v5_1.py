import json
from app.core.hiring_priority import compute_hiring_priority_score

eval_dethan = {
    "evaluation_id": "eval_dethan_real_prod",
    "personal_info": {"name": "Devadethan R"},
    "overall_score": 83.0,
    "parsed_resume": {
        "personal_info": {"name": "Devadethan R"},
        "work_history": [
            {
                "company": "Prevalent AI",
                "role": "Data Scientist L1",
                "dates": "2023 - Present",
                "description": "Deployed AWS Bedrock, LLMOps, FastAPI microservices, Docker, Kubernetes, CI/CD, PySpark."
            },
            {
                "company": "DifferentByte",
                "role": "AI Developer",
                "dates": "2022 - 2023",
                "description": "Built LangChain and LangGraph REST APIs using PySpark and Django REST."
            }
        ],
        "certifications": [
            {"title": "Google AI Essentials", "issuer": "Google"},
            {"title": "IBM AI Engineering Professional Certificate", "issuer": "IBM"},
            {"title": "Certified Data Scientist, IBM, Simplilearn, (Dec 2023)", "issuer": "Global Data Science Institute"},
            {"title": "Google Kubernetes Engine (GKE)", "issuer": "Google Cloud"},
            {"title": "Tableau Certified", "issuer": "Tableau / Salesforce"}
        ]
    },
    "raw_resume_text": "Devadethan R. Data Scientist L1 at Prevalent AI. Google AI Essentials, IBM AI Engineering Professional Certificate, Certified Data Scientist, IBM, Simplilearn, (Dec 2023), Google Kubernetes Engine (GKE), Tableau Certified."
}

res = compute_hiring_priority_score(eval_dethan)

output = {
    "candidate_name": res["professional_profile"]["candidate_name"],
    "certification_count": res["professional_profile"]["certification_count"],
    "certifications": res["certifications"]
}

print("===== DETHAN PRODUCTION API RESPONSE VERIFICATION (v5.1) =====")
print(json.dumps(output, indent=2))
