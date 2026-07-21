import asyncio
from app.agents.ingestion import parse_resume_to_json
from app.agents.parser_validation import validate_parsed_resume

def test():
    text = "Name: Ideal Candidate\nI am a highly skilled engineer with 8 years of experience. My expertise includes Python, JavaScript, FastAPI, React, and Docker."
    parsed = parse_resume_to_json(text)
    print("Parsed:", parsed)
    
    validation = validate_parsed_resume(parsed)
    print("Validation:", validation)

if __name__ == "__main__":
    test()
