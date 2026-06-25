"""
API Router for document ingestion and database persistence.
"""
import logging
import uuid
from fastapi import APIRouter, UploadFile, File, HTTPException
from app.agents.ingestion import extract_text_from_pdf, parse_resume_to_json
from app.db.clients import supabase_db  # Import our database client

logger = logging.getLogger("talentscout_api_ingest")
router = APIRouter()

@router.post("/upload")
async def upload_resume(file: UploadFile = File(...)):
    """
    Endpoint to upload a PDF resume, extract text, parse to JSON, 
    and SAVE to PostgreSQL (CRUD: Create).
    """
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")
    
    try:
        file_bytes = await file.read()
        
        # 1. Extract & Parse
        raw_text = extract_text_from_pdf(file_bytes)
        structured_data = parse_resume_to_json(raw_text)
        
        # 2. Database CRUD (Create) - Save to PostgreSQL
        candidate_id = str(uuid.uuid4())
        
        try:
            # Assuming your table is named 'candidates' as per Week 1 design
            db_response = supabase_db.table("candidates").insert({
                "filename": file.filename,
                "raw_resume_text": raw_text,
                "parsed_data_json": structured_data
            }).execute()
            logger.info(f"Successfully saved candidate {candidate_id} to database.")
        except Exception as db_err:
            logger.error(f"Database CRUD Error: Failed to save to Supabase. {db_err}")
            # We don't crash the API, but we warn the user
            return {"status": "success_but_db_failed", "parsed_data": structured_data}
        
        return {
            "status": "success",
            "candidate_id": candidate_id,
            "filename": file.filename,
            "parsed_data": structured_data
        }
        
    except ValueError as ve:
        raise HTTPException(status_code=422, detail=str(ve))
    except Exception as e:
        logger.error(f"Processing error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error.")
