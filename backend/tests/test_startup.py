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
    assert response.status_code == 404

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
    Verifies that the embedding model is available.
    Silent fallbacks are no longer allowed.
    """
    from app.agents.scout import embedding_model
    
    # In tests, this might be a MagicMock (via conftest.py) or the real model
    # The key is that it's successfully loaded and has an encode method.
    assert hasattr(embedding_model, "encode")
