"""
Ingestion Agent: Handles PDF extraction and LLM-based structured parsing.
"""
import logging
import json
from io import BytesIO
from pypdf import PdfReader
from groq import Groq
from app.core.config import settings
from app.models.schemas import ParsedResume

logger = logging.getLogger("talentscout_ingestion")

# Initialize Groq client
try:
    groq_client = Groq(api_key=settings.GROQ_API_KEY)
except Exception as e:
    logger.error(f"Failed to initialize Groq client: {e}")
    groq_client = None

def extract_text_from_pdf(file_bytes: bytes) -> str:
    """Extracts raw text from PDF bytes."""
    try:
        reader = PdfReader(BytesIO(file_bytes))
    except Exception as e:
        logger.error(f"PDF parsing initialization failed: {e}")
        raise ValueError("Invalid or corrupted PDF file.")

    if len(reader.pages) > 10:
        raise ValueError("PDF exceeds the 10-page limit.")

    try:
        text = "".join([page.extract_text() + "\n" for page in reader.pages])
        if not text.strip():
            raise ValueError("PDF contains no readable text. (OCR fallback required)")
        return text
    except Exception as e:
        logger.error(f"PDF Extraction failed: {e}")
        raise

def parse_resume_to_json(raw_text: str) -> dict:
    """
    Sends raw text to Groq Llama 3 to extract structured JSON.
    Enforces the ParsedResume Pydantic schema.
    """
    if not groq_client:
        raise RuntimeError("Groq client is not initialized.")

    prompt = f"""
    You are an expert HR Data Extraction Agent.
    Read the following resume text and extract the data into a strict JSON format.
    Do not add markdown formatting, do not add introductory text. Output ONLY valid JSON.
    
    Required JSON structure:
    {{
        "education": ["Degree from University"],
        "experience": ["Role at Company"],
        "hard_skills": ["Python", "React", "AWS"]
    }}
    
    Resume Text:
    {raw_text}
    """

    try:
        response = groq_client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="llama-3.1-8b-instant", # Using 8b for lightning-fast parsing
            temperature=0.0,        # 0.0 forces deterministic, non-creative output
            response_format={"type": "json_object"} # Forces Groq to return valid JSON
        )
        
        # Parse the string response into a Python dictionary
        result_str = response.choices[0].message.content
        parsed_data = json.loads(result_str)
        
        # Validate against our Pydantic schema to guarantee architectural integrity
        validated_data = ParsedResume(**parsed_data)
        return validated_data.model_dump()
        
    except Exception as e:
        logger.error(f"LLM Parsing failed: {e}")
        raise
