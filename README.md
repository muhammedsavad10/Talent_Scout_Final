# TalentScout Multi-Agent Recruitment Intelligence System

TalentScout is a cutting-edge, multi-agent recruitment intelligence platform designed to streamline and automate the candidate evaluation process using state-of-the-art AI. The system evaluates resumes against job descriptions, provides deep skills mapping, behavioral analysis, and actionable insights for recruiters.

## Project Structure

The project is structured into two main components:
- `backend/`: The Python FastAPI backend and agent orchestrator.
- `frontend/`: The React (Vite) frontend containing the Recruiter Dashboard and Candidate Portal.

## Architecture

TalentScout employs a multi-agent architecture powered by LangGraph, integrating multiple specialized AI agents:
1. **Scout Agent**: Parses and structures incoming resumes.
2. **Strategy Agent**: Formulates a customized evaluation strategy.
3. **Evaluation Agent**: Analyzes the candidate's skills and experience against the requirements.
4. **Scoring Agent**: Computes quantifiable scores.
5. **Orchestrator**: Manages state, batching, and routing.

These agents coordinate to produce a comprehensive candidate evaluation. State and vector embeddings are stored in Supabase and Qdrant.

## Technologies Used
- **Backend Framework**: FastAPI, Python 3.10
- **AI / LLM Orchestration**: LangGraph, LangChain, Groq API, Gemini API
- **Databases**: Supabase (PostgreSQL), Qdrant (Vector DB)
- **Frontend**: React, Vite, TailwindCSS (if configured)
- **Testing**: Pytest, Playwright

## Workflows

### Candidate Evaluation Workflow
1. Candidate uploads resume via the frontend or API.
2. The orchestrator triggers the multi-agent evaluation pipeline.
3. The evaluation is saved to Supabase and Qdrant.
4. Recruiter reviews the structured insights and scoring via the dashboard.

### Batch Evaluation Workflow
The system supports batch evaluations where multiple resumes can be processed concurrently through a centralized rate-limited state machine.

## Setup and Installation

### Backend Setup
1. Ensure Python 3.10+ is installed.
2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Copy `backend/.env.example` to `backend/.env` and configure your API keys (Groq, Gemini, Supabase, Qdrant).
5. Run the backend:
   ```bash
   uvicorn app.main:app --reload
   ```

### Frontend Setup
1. Ensure Node.js 18+ is installed.
2. Navigate to `frontend/`:
   ```bash
   cd frontend
   npm install
   ```
3. Run the development server:
   ```bash
   npm run dev
   ```

## API Endpoints
- `POST /api/evaluate`: Single candidate resume evaluation.
- `POST /api/batch`: Submit a batch of resumes.
- `GET /api/candidates`: Retrieve evaluated candidates.
- `GET /api/status/{job_id}`: Check batch processing status.

*(See FastAPI docs at `/docs` for complete API documentation)*
