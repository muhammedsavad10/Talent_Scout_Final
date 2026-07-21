import asyncio
import json
from app.agents.orchestrator import run_evaluation_pipeline

def _serialize(obj):
    if hasattr(obj, "model_dump"):
        return obj.model_dump()
    elif hasattr(obj, "dict"):
        return obj.dict()
    return str(obj)

async def test():
    text = "Name: Ideal Candidate\nI am a highly skilled engineer with 8 years of experience. My expertise includes Python, JavaScript, FastAPI, React, and Docker."
    required = ["python", "kubernetes", "fastapi"]
    
    result = await run_evaluation_pipeline(text, "test_eval", required)
    
    try:
        serialized = json.dumps(result, default=_serialize)
        print("Serialization successful!")
    except Exception as e:
        print("Serialization failed:", e)

if __name__ == "__main__":
    asyncio.run(test())
