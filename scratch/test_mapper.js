const { mapEvaluationResponse } = require('../frontend/src/utils/evaluationMapper.js');

// Mock response matching task-694.log
const rawResponse = {
  "result": {
    "debug": {
      "agent_logs": [],
      "processing_ms": 0,
      "matched_tokens": ["Python", "FastAPI", "SQL"],
      "raw_weighted_score": 0.68,
      "raw_containment_score": 0,
      "raw_semantic_similarity": 0,
      "pipeline_node_transitions": ["Parser", "Normalization", "Validation", "Scorer", "PolicyEngine", "Strategy"]
    },
    "status": "success",
    "contacts": {
      "email": "richard.jackson1@example.com",
      "links": [],
      "phone": "+1 (555) 529-4611"
    },
    "evidence": {
      "timeline_title": "Chronological Career Milestones",
      "business_impact": [],
      "career_timeline": [],
      "skills_evidence": [
        {
          "skill": "Python",
          "status": "Identified",
          "reasoning": null,
          "role_held": null,
          "project_name": null,
          "evidence_snippet": null,
          "match_confidence": 100,
          "evidence_strength": "High"
        },
        {
          "skill": "FastAPI",
          "status": "Identified",
          "reasoning": null,
          "role_held": null,
          "project_name": null,
          "evidence_snippet": null,
          "match_confidence": 100,
          "evidence_strength": "High"
        },
        {
          "skill": "SQL",
          "status": "Identified",
          "reasoning": null,
          "role_held": null,
          "project_name": null,
          "evidence_snippet": null,
          "match_confidence": 100,
          "evidence_strength": "High"
        },
        {
          "skill": "Docker",
          "status": "Not identified",
          "reasoning": null,
          "role_held": null,
          "project_name": null,
          "evidence_snippet": null,
          "match_confidence": 0,
          "evidence_strength": "Low"
        }
      ]
    },
    "filename": "RES_001.pdf",
    "interview": {
      "interview_questions": {
        "easy": [],
        "medium": [],
        "advanced": []
      },
      "verify_during_interview": []
    },
    "recruiter": {
      "confidence": {
        "reasoning": "Medium",
        "learnability": "Medium",
        "skill_extraction": "High",
        "evidence_justification": "Automated evaluation"
      },
      "recruiter_notes": "",
      "resume_feedback": []
    },
    "onboarding": {
      "learning_curve": [],
      "estimated_ramp_up": "2-4 weeks",
      "rationale_factors": []
    },
    "evaluation_id": "5705a877-9dd3-4d79-b56d-f2bee49bcd2e_9e0ad8e0",
    "overall_score": 68,
    "personal_info": {
      "name": "Richard Jackson",
      "email": "richard.jackson1@example.com",
      "links": [],
      "phone": "+1 (555) 529-4611"
    },
    "recommendation": {
      "disclaimer": "This assessment is based only on information present in the submitted resume.",
      "candidate_summary": [],
      "rationale_bullets": [
        "Candidate failed one or more mandatory policy gates.\n - Missing mandatory skill: Docker"
      ],
      "candidate_highlights": [],
      "hiring_recommendation": "Reject"
    },
    "decision_engine": {
      "policy_flags": [
        "Missing mandatory skill: Docker"
      ],
      "overall_score": 68,
      "recommendation": {
        "recommendation_basis": {
          "reasoning": "Candidate failed one or more mandatory policy gates.\n - Missing mandatory skill: Docker",
          "strengths": [],
          "weaknesses": [
            "Missing mandatory skill: Docker"
          ],
          "critical_missing_skills": [
            "Docker"
          ]
        },
        "hiring_recommendation": "Reject"
      },
      "evidence_states": {
        "MATCHED": [
          "Python",
          "FastAPI",
          "SQL"
        ],
        "MISSING": [
          "Docker"
        ],
        "INFERRED": [],
        "CONTRADICTED": []
      },
      "policy_eligible": false,
      "dimension_scores": {
        "skill_match": {
          "score": 75,
          "health": null,
          "status": "EVALUATED",
          "weight": 0.4,
          "sources": ["resume"],
          "evidence": ["Matched 3 out of 4 required skills."],
          "confidence": 100,
          "sub_metrics": null
        },
        "experience_quality": {
          "score": 80,
          "health": null,
          "status": "EVALUATED",
          "weight": 0.15,
          "sources": ["resume"],
          "evidence": ["Deterministic baseline quality."],
          "confidence": 100,
          "sub_metrics": null
        },
        "experience_quantity": {
          "score": 40,
          "health": null,
          "status": "EVALUATED",
          "weight": 0.2,
          "sources": ["resume"],
          "evidence": ["Found 2 roles."],
          "confidence": 100,
          "sub_metrics": null
        },
        "experience_relevance": {
          "score": 75,
          "health": null,
          "status": "EVALUATED",
          "weight": 0.25,
          "sources": ["resume"],
          "evidence": ["Deterministic baseline relevance."],
          "confidence": 100,
          "sub_metrics": null
        }
      },
      "recommendation_basis": {
        "reasoning": "Candidate failed one or more mandatory policy gates.\n - Missing mandatory skill: Docker",
        "strengths": [],
        "weaknesses": [
          "Missing mandatory skill: Docker"
        ],
        "critical_missing_skills": [
          "Docker"
        ]
      }
    },
    "recommendation_basis": {
      "reasoning": "Candidate failed one or more mandatory policy gates.\n - Missing mandatory skill: Docker",
      "strengths": [],
      "weaknesses": [
        "Missing mandatory skill: Docker"
      ],
      "domain_alignment": "Unknown",
      "decision_reasoning": "Candidate failed one or more mandatory policy gates.\n - Missing mandatory skill: Docker",
      "critical_missing_skills": [
        "Docker"
      ]
    }
  },
  "status": "COMPLETED",
  "filename": "RES_001.pdf",
  "evaluation_id": "5705a877-9dd3-4d79-b56d-f2bee49bcd2e_9e0ad8e0"
};

const mapped = mapEvaluationResponse(rawResponse);
console.log("MAPPED RESULT:", JSON.stringify(mapped, null, 2));
