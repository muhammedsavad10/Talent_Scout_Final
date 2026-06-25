"""
Unit and integration tests for the Ingestion Agent and Router.
"""
import pytest
from unittest.mock import MagicMock
from fastapi.testclient import TestClient
from main import app
from app.agents.ingestion import extract_text_from_pdf, parse_resume_to_json

client = TestClient(app)

@pytest.fixture
def mock_groq(mocker):
    """Fixture to mock the Groq client used in the ingestion agent."""
    mock_client = mocker.patch("app.agents.ingestion.groq_client")
    return mock_client

@pytest.fixture
def mock_pdf_reader(mocker):
    """Fixture to mock PdfReader."""
    return mocker.patch("app.agents.ingestion.PdfReader")

def test_extract_text_from_pdf_success(mock_pdf_reader):
    """Test that extract_text_from_pdf extracts text from multiple pages."""
    # Mock pages in PdfReader
    mock_page1 = MagicMock()
    mock_page1.extract_text.return_value = "Page 1 content."
    mock_page2 = MagicMock()
    mock_page2.extract_text.return_value = "Page 2 content."
    
    mock_reader_instance = MagicMock()
    mock_reader_instance.pages = [mock_page1, mock_page2]
    mock_pdf_reader.return_value = mock_reader_instance
    
    text = extract_text_from_pdf(b"dummy pdf bytes")
    assert "Page 1 content." in text
    assert "Page 2 content." in text

def test_extract_text_from_pdf_empty(mock_pdf_reader):
    """Test that extract_text_from_pdf raises ValueError when no text is found."""
    mock_page = MagicMock()
    mock_page.extract_text.return_value = "   "
    
    mock_reader_instance = MagicMock()
    mock_reader_instance.pages = [mock_page]
    mock_pdf_reader.return_value = mock_reader_instance
    
    with pytest.raises(ValueError, match="PDF contains no readable text"):
        extract_text_from_pdf(b"dummy pdf bytes")

def test_extract_text_from_pdf_invalid(mock_pdf_reader):
    """Test that extract_text_from_pdf raises ValueError when PdfReader fails to initialize."""
    mock_pdf_reader.side_effect = Exception("File is not a valid PDF")
    
    with pytest.raises(ValueError, match="Invalid or corrupted PDF file."):
        extract_text_from_pdf(b"corrupted bytes")

def test_extract_text_from_pdf_exceeds_page_limit(mock_pdf_reader):
    """Test that extract_text_from_pdf raises ValueError when pages exceed the limit."""
    mock_reader_instance = MagicMock()
    # Create a list of 11 mock pages
    mock_reader_instance.pages = [MagicMock() for _ in range(11)]
    mock_pdf_reader.return_value = mock_reader_instance
    
    with pytest.raises(ValueError, match="PDF exceeds the 10-page limit."):
        extract_text_from_pdf(b"dummy pdf bytes")

def test_parse_resume_to_json_success(mock_groq):
    """Test parse_resume_to_json with valid LLM output matching the schema."""
    # Mock Groq chat completions response
    mock_response = MagicMock()
    mock_response.choices = [
        MagicMock(message=MagicMock(content='{"education": ["B.S. Computer Science, MIT"], "experience": ["Developer at Google"], "hard_skills": ["Python", "FastAPI"]}'))
    ]
    mock_groq.chat.completions.create.return_value = mock_response
    
    result = parse_resume_to_json("Raw resume text")
    assert result["education"] == ["B.S. Computer Science, MIT"]
    assert result["experience"] == ["Developer at Google"]
    assert result["hard_skills"] == ["Python", "FastAPI"]

def test_parse_resume_to_json_validation_failure(mock_groq):
    """Test parse_resume_to_json raises exception on invalid schema response from LLM."""
    mock_response = MagicMock()
    # Missing education field
    mock_response.choices = [
        MagicMock(message=MagicMock(content='{"experience": ["Developer at Google"], "hard_skills": ["Python"]}'))
    ]
    mock_groq.chat.completions.create.return_value = mock_response
    
    with pytest.raises(Exception):
        parse_resume_to_json("Raw resume text")

def test_upload_endpoint_success(mocker, mock_groq, mock_pdf_reader):
    """Test upload endpoint returns correctly parsed structured JSON and saves to DB."""
    # Mock text extraction
    mock_page = MagicMock()
    mock_page.extract_text.return_value = "Resume text content"
    mock_reader_instance = MagicMock()
    mock_reader_instance.pages = [mock_page]
    mock_pdf_reader.return_value = mock_reader_instance
    
    # Mock LLM parsing
    mock_response = MagicMock()
    mock_response.choices = [
        MagicMock(message=MagicMock(content='{"education": ["M.S. Stanford"], "experience": ["Lead at Apple"], "hard_skills": ["Swift", "iOS"]}'))
    ]
    mock_groq.chat.completions.create.return_value = mock_response
    
    # Mock Supabase
    mock_supabase = mocker.patch("app.api.ingest.supabase_db")
    mock_supabase.table.return_value.insert.return_value.execute.return_value = MagicMock()
    
    # Send request with a mock PDF file
    files = {"file": ("resume.pdf", b"dummy pdf bytes", "application/pdf")}
    response = client.post("/api/v1/ingestion/upload", files=files)
    
    assert response.status_code == 200
    json_data = response.json()
    assert json_data["status"] == "success"
    assert "candidate_id" in json_data
    assert json_data["filename"] == "resume.pdf"
    assert json_data["parsed_data"]["education"] == ["M.S. Stanford"]
    assert json_data["parsed_data"]["experience"] == ["Lead at Apple"]
    assert json_data["parsed_data"]["hard_skills"] == ["Swift", "iOS"]
    
    # Verify DB insert was called
    mock_supabase.table.assert_called_once_with("candidates")
    mock_supabase.table.return_value.insert.assert_called_once()

def test_upload_endpoint_db_failure(mocker, mock_groq, mock_pdf_reader):
    """Test upload endpoint returns success_but_db_failed when database saving fails."""
    # Mock text extraction
    mock_page = MagicMock()
    mock_page.extract_text.return_value = "Resume text content"
    mock_reader_instance = MagicMock()
    mock_reader_instance.pages = [mock_page]
    mock_pdf_reader.return_value = mock_reader_instance
    
    # Mock LLM parsing
    mock_response = MagicMock()
    mock_response.choices = [
        MagicMock(message=MagicMock(content='{"education": ["M.S. Stanford"], "experience": ["Lead at Apple"], "hard_skills": ["Swift", "iOS"]}'))
    ]
    mock_groq.chat.completions.create.return_value = mock_response
    
    # Mock Supabase raising exception on insert
    mock_supabase = mocker.patch("app.api.ingest.supabase_db")
    mock_supabase.table.return_value.insert.side_effect = Exception("DB connection timeout")
    
    files = {"file": ("resume.pdf", b"dummy pdf bytes", "application/pdf")}
    response = client.post("/api/v1/ingestion/upload", files=files)
    
    assert response.status_code == 200
    json_data = response.json()
    assert json_data["status"] == "success_but_db_failed"
    assert json_data["parsed_data"]["education"] == ["M.S. Stanford"]

def test_upload_endpoint_non_pdf():
    """Test upload endpoint rejects non-PDF file uploads with a 400 error."""
    files = {"file": ("resume.txt", b"dummy txt content", "text/plain")}
    response = client.post("/api/v1/ingestion/upload", files=files)
    
    assert response.status_code == 400
    assert response.json()["detail"] == "Only PDF files are supported."

def test_upload_endpoint_empty_pdf(mock_pdf_reader):
    """Test upload endpoint returns 422 if the PDF contains no readable text."""
    mock_page = MagicMock()
    mock_page.extract_text.return_value = ""
    mock_reader_instance = MagicMock()
    mock_reader_instance.pages = [mock_page]
    mock_pdf_reader.return_value = mock_reader_instance
    
    files = {"file": ("empty.pdf", b"dummy pdf bytes", "application/pdf")}
    response = client.post("/api/v1/ingestion/upload", files=files)
    
    assert response.status_code == 422
    assert "PDF contains no readable text" in response.json()["detail"]

def test_upload_endpoint_llm_failure(mock_pdf_reader, mock_groq):
    """Test upload endpoint returns 500 when LLM parsing completely fails."""
    mock_page = MagicMock()
    mock_page.extract_text.return_value = "Valid text content"
    mock_reader_instance = MagicMock()
    mock_reader_instance.pages = [mock_page]
    mock_pdf_reader.return_value = mock_reader_instance
    
    # Mock LLM raising exception
    mock_groq.chat.completions.create.side_effect = RuntimeError("Groq API Timeout")
    
    files = {"file": ("resume.pdf", b"dummy pdf bytes", "application/pdf")}
    response = client.post("/api/v1/ingestion/upload", files=files)
    
    assert response.status_code == 500
    assert response.json()["detail"] == "Internal server error."
