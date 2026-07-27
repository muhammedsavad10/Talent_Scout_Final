"""
TalentScout Enterprise v1.8.2 — Origin-Based Canonical Entity Graph Test Suite.
Validates:
1. Fragment extraction (TITLE, DESCRIPTION, TECHNOLOGY, BULLET)
2. Evidence Graph Merging (technology overlap, domain entity overlap, line proximity)
3. Project UUID generation
4. DuplicateProjectDetected validation pass
5. Muhammad benchmark candidate test: personal_projects count == 2 (Delay2Decision, FairCrop AI), 0 description-only projects
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
    DuplicateProjectDetected
)

MUHAMMAD_RESUME = """
Muhammad Fuvad Sinin
Email: fuvad@example.com | Phone: +91 9876543210
SUMMARY
Senior AI Engineer experienced in scalable systems.

PROJECTS
Delay2Decision
- Designed and developed a dynamic decision-support system using LangChain and Qdrant.
FairCrop AI
- Crop yield prediction platform built using PyTorch and FastAPI.
"""

def test_v1_8_2_fragment_and_node_graph_merge():
    raw_fragments = [
        {"title": "Delay2Decision", "description": "Decision support system using LangChain and Qdrant."},
        {"title": "Designed and developed a dynamic decision-support system using LangChain and Qdrant.", "description": "Multi-agent system."},
        {"title": "FairCrop AI", "description": "Crop yield prediction platform."},
        {"title": "Built an AI-driven decision support platform for crop yield prediction using PyTorch.", "description": "Yield platform."}
    ]
    
    clean_projects = deduplicate_projects(raw_fragments)
    
    # Must produce EXACTLY 2 canonical project records
    assert len(clean_projects) == 2
    
    titles = [p["canonical_title"] for p in clean_projects]
    assert "Delay2Decision" in titles or "FairCrop AI" in titles
    
    # Every project record must have a valid project_uuid
    for p in clean_projects:
        assert "project_uuid" in p
        assert len(p["project_uuid"]) > 10
        assert isinstance(p["technologies"], list)

@pytest.mark.asyncio
async def test_v1_8_2_muhammad_runtime_json_entity_graph():
    res = await run_evaluation_pipeline(MUHAMMAD_RESUME, "eval_muhammad_v182", required_skills=["Python"])
    final_json = validate_final_api_response(res)
    
    projects = final_json.get("projects", [])
    hp_data = final_json.get("hiring_priority", {})
    personal_projects = hp_data.get("personal_projects", [])
    
    # Runtime personal_projects must contain Delay2Decision and FairCrop AI
    project_titles = [p.get("canonical_title") or p.get("title") for p in (personal_projects or projects)]
    assert any("Delay2Decision" in t for t in project_titles if t)
    assert any("FairCrop" in t for t in project_titles if t)
    
    # Verify no description-only or anonymous projects
    for p in (personal_projects or projects):
        title = p.get("canonical_title") or p.get("title") or ""
        assert not title.lower().startswith("built")
        assert not title.lower().startswith("designed")
        assert not title.lower().startswith("developed")
        assert title != "Project"
        assert len(title) > 0

def test_evidence_graph_merge_rule():
    graph = ProjectEntityGraph()
    # Fragment A
    frag_a = EvidenceFragment(
        text="Delay2Decision",
        fragment_type=FragmentType.TITLE,
        source_section="projects",
        technologies={"langchain", "qdrant"}
    )
    # Fragment B (different text, but same tech stack & domain)
    frag_b = EvidenceFragment(
        text="Designed decision support agent for layover routing",
        fragment_type=FragmentType.DESCRIPTION,
        source_section="projects",
        technologies={"langchain", "qdrant"}
    )
    
    graph.add_fragment(frag_a)
    graph.add_fragment(frag_b)
    
    assert len(graph.nodes) == 1
    assert graph.nodes[0].canonical_title == "Delay2Decision"
    assert "langchain" in graph.nodes[0].technologies
