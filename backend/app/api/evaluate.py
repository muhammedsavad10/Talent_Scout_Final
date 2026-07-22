"""
API Router for the LangGraph Multi-Agent Evaluation Engine.
"""
import logging
from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from app.agents.orchestrator import run_evaluation_pipeline
from app.services.evaluation_store import evaluation_store

logger = logging.getLogger("talentscout_api_evaluate")
router = APIRouter()

import uuid
from app.agents.ingestion import extract_text_from_pdf

@router.post("/evaluate")
async def evaluate_candidate(
    file: UploadFile = File(...),
    jd_text: str = Form(...),
    jd_skills: str = Form(...)  # Expects a comma-separated string (e.g., "Python, FastAPI, Docker")
):
    """
    Ingests a PDF resume and job parameters, executes the LangGraph multi-agent swarm,
    and returns a mathematically transparent evaluation and feedback report.
    """
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")
    
    try:
        # Read the upload stream into raw bytes for the ingestion node
        pdf_bytes = await file.read()
        
        # Extract text from the PDF for the pipeline
        try:
            text = extract_text_from_pdf(pdf_bytes)
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"PDF extraction failed: {str(e)}")
        
        # Parse the comma-separated target skills into a clean list
        skills_list = [skill.strip() for skill in jd_skills.split(",") if skill.strip()]
        
        logger.info(f"Web request received: Initiating LangGraph pipeline for {file.filename}")
        
        candidate_id = f"eval_{uuid.uuid4().hex[:8]}"
        
        # Execute the unified state machine
        final_state = await run_evaluation_pipeline(
            text=text,
            candidate_id=candidate_id,
            required_skills=skills_list
        )
        
        # Gracefully handle internal state machine tracking drops
        if final_state.get("status") == "error":
            logger.error(f"LangGraph execution error drop: {final_state.get('message')}")
            raise HTTPException(status_code=500, detail=final_state.get("message"))
        
        # Save to store and return the standardized payload contract matching status & batch endpoints
        final_state["filename"] = file.filename
        final_state["evaluation_id"] = candidate_id
        final_state["candidate_id"] = candidate_id
        
        full_eval = {
            "evaluation_id": candidate_id,
            "filename": file.filename,
            "status": "COMPLETED",
            "result": final_state
        }
        await evaluation_store.save_evaluation(candidate_id, full_eval)
        
        return full_eval
        
    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"Unhandled evaluation gateway failure: {e}")
        raise HTTPException(status_code=500, detail="Internal server error during pipeline evaluation.")

@router.get("/status/{evaluation_id}")
async def get_evaluation_status(evaluation_id: str):
    """
    Retrieves the full evaluation status and results for a specific candidate.
    """
    eval_data = await evaluation_store.get_evaluation(evaluation_id)
    if not eval_data:
        raise HTTPException(status_code=404, detail="Evaluation not found.")
    return eval_data

@router.post("/email/generate")
async def generate_email(payload: dict):
    return {
        "subject": "Interview Invitation",
        "body": "Dear Candidate,\n\nWe are pleased to invite you to an interview based on your excellent resume.\n\nBest regards,\nRecruiter"
    }

@router.post("/assistant/ask")
async def ask_assistant(payload: dict):
    return {
        "answer": "This is a mocked response from the AI assistant. I see the candidate has relevant experience.",
        "citations": []
    }

@router.post("/dev-mode/verify")
async def dev_mode_verify(payload: dict):
    return {"success": True}