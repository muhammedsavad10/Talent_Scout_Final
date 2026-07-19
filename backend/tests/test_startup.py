import pytest
from fastapi.testclient import TestClient
from app.core.config import settings

def test_startup_imports_and_registration():
    """
    Verifies that the FastAPI application imports successfully and routers are registered.
    """
    from main import app
    client = TestClient(app)
    
    # Check if routers are registered (e.g., /api/v1/evaluate/batch should exist)
    response = client.get("/api/v1/evaluate/batch/fake-id")
    assert response.status_code == 200
    assert response.json()["status"] == "COMPLETED"

def test_startup_events_execute():
    """
    Verifies that the startup events execute successfully (lifespan manager).
    """
    from main import app
    
    with TestClient(app) as client:
        # The lifespan context manager runs on startup
        # We can verify it didn't crash by making a basic health check request
        response = client.get("/")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"

def test_embedding_availability_reporting():
    """
    Verifies that the embedding model availability is handled correctly.
    If DEVELOPMENT_MODE is True, it should fallback to DummyEmbeddingModel.
    """
    from app.agents.scout import embedding_model, DummyEmbeddingModel
    
    if settings.DEVELOPMENT_MODE:
        # Depending on if sentence_transformers is installed or not, it could be either.
        # But if it's a DummyEmbeddingModel, it should raise RuntimeError on encode.
        if isinstance(embedding_model, DummyEmbeddingModel):
            with pytest.raises(RuntimeError, match="SentenceTransformer unavailable"):
                embedding_model.encode("test")
    else:
        # In production, if it started, it must be the real one
        assert not isinstance(embedding_model, DummyEmbeddingModel)
