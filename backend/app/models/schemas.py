"""
Pydantic schemas for data validation and LLM output enforcement.
"""
from pydantic import BaseModel, Field
from typing import List

class ParsedResume(BaseModel):
    """Strict schema for the LLM to follow when parsing a resume."""
    education: List[str] = Field(description="List of degrees and universities")
    experience: List[str] = Field(description="List of job titles and companies")
    hard_skills: List[str] = Field(description="List of explicit technical skills, tools, and frameworks")
