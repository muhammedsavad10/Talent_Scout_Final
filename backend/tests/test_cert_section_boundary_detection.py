"""
Regression Test Suite for Section Boundary Detection & Wrapped Line Continuations.
Verifies:
1. Stops reading certifications when reaching next section heading (Achievements, Technical Skills, Interests, etc.).
2. Treats wrapped lines within a certification entry as continuations.
"""
import pytest
from app.agents.deterministic_extractor import parse_certification_section_lines, extract_certifications_deterministically

def test_cert_section_boundary_stop():
    raw = """
CERTIFICATIONS
- Google AI Essentials
- IBM AI Engineering Professional Certificate
- Google Kubernetes Engine (GKE)
TECHNICAL SKILLS
- Python, FastAPI, Docker
ACHIEVEMENTS
- Hackathon Winner 2024
"""
    parsed_lines = parse_certification_section_lines(raw)
    assert len(parsed_lines) == 3
    assert "Google AI Essentials" in parsed_lines
    assert "IBM AI Engineering Professional Certificate" in parsed_lines
    assert "Google Kubernetes Engine (GKE)" in parsed_lines
    assert not any("Python" in l for l in parsed_lines)
    assert not any("Hackathon" in l for l in parsed_lines)

def test_cert_wrapped_lines_continuation():
    raw = """
CERTIFICATIONS
- Google AI Essentials
- IBM AI Engineering
  Professional Certificate
- Google Kubernetes Engine
  (GKE)
- Tableau Certified
"""
    parsed_lines = parse_certification_section_lines(raw)
    assert len(parsed_lines) == 4
    assert parsed_lines[0] == "Google AI Essentials"
    assert parsed_lines[1] == "IBM AI Engineering Professional Certificate"
    assert parsed_lines[2] == "Google Kubernetes Engine (GKE)"
    assert parsed_lines[3] == "Tableau Certified"
