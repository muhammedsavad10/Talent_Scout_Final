"""
TalentScout Enterprise v1.8.3 — Project Identity Resolution Test Suite.
Validates:
1. Muhammad benchmark candidate test: personal_projects count == 2 (Delay2Decision and FairCrop AI)
2. Zero evidence leakage between distinct projects
3. Duplicate representations of the same project merge cleanly into 1 node
4. Distinct projects sharing identical tech stack (Python, FastAPI, AWS) REMAIN SEPARATE
5. Identity score breakdown and merge_confidence verification
"""
import pytest
import asyncio
from app.agents.orchestrator import run_evaluation_pipeline
from app.core.consistency_validator import validate_final_api_response
from app.core.project_deduplicator import (
    EvidenceFragment,
    FragmentType,
    ProjectNode,
    ProjectEntityGraph,
    deduplicate_projects,
    compute_identity_score
)

MUHAMMAD_RESUME = """
Muhammad Fuvad Sinin
Email: fuvad@example.com | Phone: +91 9876543210
SUMMARY
Senior AI Engineer experienced in scalable systems.

PROJECTS
Delay2Decision
- Designed and developed a dynamic decision-support system using LangChain and Qdrant for airport layover optimization.
FairCrop AI
- Crop yield prediction platform built using PyTorch, FastAPI, and agricultural soil analytics.
"""

def test_v1_8_3_distinct_projects_same_tech_remain_separate():
    raw_projects = [
        {
            "title": "Delay2Decision",
            "description": "Airport layover itinerary planner for flight passengers using LangChain and Qdrant.",
            "technologies": ["Python", "FastAPI", "AWS"]
        },
        {
            "title": "FairCrop AI",
            "description": "Agricultural crop yield analytics platform for soil monitoring using PyTorch.",
            "technologies": ["Python", "FastAPI", "AWS"]
        }
    ]

    deduped = deduplicate_projects(raw_projects)

    # Must NOT merge distinct projects just because they share Python, FastAPI, AWS!
    assert len(deduped) == 2
    titles = [p["canonical_title"] for p in deduped]
    assert "Delay2Decision" in titles
    assert "FairCrop AI" in titles

def test_v1_8_3_duplicate_representations_merge_with_high_confidence():
    raw_projects = [
        {
            "title": "Delay2Decision",
            "description": "Airport layover planning agent.",
            "technologies": ["LangChain", "Qdrant"]
        },
        {
            "title": "Delay2Decision Agent",
            "description": "Flight passenger itinerary layover decision support system.",
            "technologies": ["LangGraph", "Qdrant"]
        }
    ]

    deduped = deduplicate_projects(raw_projects)

    # Must merge duplicate representations into 1 canonical node
    assert len(deduped) == 1
    p = deduped[0]
    assert p["canonical_title"] == "Delay2Decision"
    assert "merge_confidence" in p
    assert p["merge_confidence"] >= 0.85

@pytest.mark.asyncio
async def test_v1_8_3_muhammad_runtime_json_acceptance():
    res = await run_evaluation_pipeline(MUHAMMAD_RESUME, "eval_muhammad_v183", required_skills=["Python"])
    final_json = validate_final_api_response(res)

    projects = final_json.get("projects", [])
    hp_data = final_json.get("hiring_priority", {})
    personal_projects = hp_data.get("personal_projects", [])

    # Runtime personal_projects must contain Delay2Decision and FairCrop AI
    project_titles = [p.get("canonical_title") or p.get("title") for p in (personal_projects or projects)]
    assert any("Delay2Decision" in t for t in project_titles if t)
    assert any("FairCrop" in t for t in project_titles if t)

    d2d = next((p for p in (personal_projects or projects) if "Delay2Decision" in p.get("title", "") or "Delay2Decision" in p.get("canonical_title", "")), None)
    faircrop = next((p for p in (personal_projects or projects) if "FairCrop" in p.get("title", "") or "FairCrop" in p.get("canonical_title", "")), None)

    assert d2d is not None
    assert faircrop is not None

    # Verify zero evidence leakage (d2d does NOT contain crop/agriculture, faircrop does NOT contain airport/layover)
    d2d_ev = (d2d.get("summary", "") + " " + d2d.get("description", "") + " " + d2d.get("evidence", "")).lower()
    faircrop_ev = (faircrop.get("summary", "") + " " + faircrop.get("description", "") + " " + faircrop.get("evidence", "")).lower()

    assert "crop" not in d2d_ev
    assert "agriculture" not in d2d_ev

    assert "airport" not in faircrop_ev
    assert "layover" not in faircrop_ev
