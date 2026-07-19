"""
Temporary reconstruction stub.

Reconstructed after Phase 5 data loss.

This implementation only restores application startup.

Full logic will be implemented in later reconstruction phases.
"""
import logging
import uuid
from typing import List
from fastapi import APIRouter, File, UploadFile, Form

logger = logging.getLogger(__name__)

router = APIRouter()

@router.post("/batch")
async def batch_evaluate_stub(
    files: List[UploadFile] = File(...),
    job_description: str = Form(...),
    job_role: str = Form(...)
):
    """
    Placeholder endpoint for batch evaluation.
    Returns the expected schema for the frontend (a batch_id).
    """
    return {"batch_id": str(uuid.uuid4())}

@router.get("/batch/{batch_id}")
async def get_batch_status_stub(batch_id: str):
    """
    Placeholder endpoint for polling batch status.
    Returns a dummy completed status to satisfy frontend polling.
    """
    return {
        "batch_id": batch_id,
        "status": "COMPLETED",
        "total": 0,
        "completed": 0,
        "processing": 0,
        "queued": 0,
        "failed": 0,
        "successfully_evaluated": 0,
        "ranked_candidates": []
    }
