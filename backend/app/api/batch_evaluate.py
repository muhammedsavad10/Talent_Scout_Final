"""
Temporary reconstruction stub.

Reconstructed after Phase 5 data loss.

This implementation only restores application startup.

Full logic will be implemented in later reconstruction phases.
"""
import logging
import uuid
import asyncio
from typing import List
from fastapi import APIRouter, File, UploadFile, Form, BackgroundTasks, HTTPException
from app.agents.orchestrator import run_evaluation_pipeline
from app.services.evaluation_store import evaluation_store
from app.agents.comparator import compare_candidates
from pydantic import BaseModel

logger = logging.getLogger(__name__)

router = APIRouter()

from app.agents.ingestion import extract_text_from_pdf

async def process_batch(batch_id: str, files: List[UploadFile], jd_skills: List[str], job_description: str = ""):
    total = len(files)
    completed = 0
    failed = 0
    
    raw_evaluations = []
    
    for file in files:
        eval_id = f"{batch_id}_{uuid.uuid4().hex[:8]}"
        
        try:
            pdf_bytes = await file.read()
            text = extract_text_from_pdf(pdf_bytes)
        except Exception as e:
            logger.error(f"Batch eval failed to extract PDF {file.filename}: {e}")
            failed += 1
            await evaluation_store.update_batch_status(batch_id, {
                "completed": completed, "failed": failed, "processing": total - completed - failed
            })
            continue
            
        try:
            result = await run_evaluation_pipeline(
                text=text,
                candidate_id=eval_id,
                required_skills=jd_skills,
                jd_text=job_description
            )
            
            # Embed filename into result so comparator can pick it up
            result["filename"] = file.filename
            
            # Store full result
            # We structure it identically to what the frontend expects for single eval
            full_eval = {
                "evaluation_id": eval_id,
                "filename": file.filename,
                "status": "COMPLETED" if result.get("status") == "success" else "FAILED",
                "result": result
            }
            await evaluation_store.save_evaluation(eval_id, full_eval)
            
            if result.get("status") == "success":
                completed += 1
                raw_evaluations.append(result)
            else:
                failed += 1
        except Exception as e:
            logger.exception(f"Batch eval failed for {file.filename}: {e}")
            failed += 1
            
        await evaluation_store.update_batch_status(batch_id, {
            "completed": completed,
            "failed": failed,
            "processing": total - completed - failed
        })
        
    # Finalize batch
    status = "COMPLETED"
    if failed > 0:
        status = "COMPLETED_WITH_ERRORS" if completed > 0 else "FAILED"
        
    # Run comparator if we have successful evaluations
    ranked = []
    if completed > 0:
        ranked = compare_candidates(raw_evaluations)
        
    await evaluation_store.update_batch_status(batch_id, {
        "status": status,
        "successfully_evaluated": completed,
        "results": {"ranked_candidates": [r.model_dump() if isinstance(r, BaseModel) else dict(r) for r in ranked]}
    })


@router.post("/batch")
async def batch_evaluate_stub(
    background_tasks: BackgroundTasks,
    files: List[UploadFile] = File(...),
    job_description: str = Form(...),
    jd_skills: str = Form(default="")
):
    """
    Ingests multiple PDF resumes and initiates a batch processing background task.
    """
    batch_id = str(uuid.uuid4())
    total = len(files)
    
    await evaluation_store.create_batch(batch_id, total)
    
    skills_list = [s.strip() for s in jd_skills.split(",") if s.strip()]
    
    background_tasks.add_task(process_batch, batch_id, files, skills_list, job_description)
    
    return {"batch_id": batch_id, "status": "QUEUED"}

@router.get("/batch/{batch_id}")
async def get_batch_status_stub(batch_id: str):
    """
    Endpoint for polling batch status.
    """
    status = await evaluation_store.get_batch_status(batch_id)
    if not status:
        raise HTTPException(status_code=404, detail="Batch not found")
    return status
