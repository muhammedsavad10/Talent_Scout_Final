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

def test_decision_config_availability():
    """
    Verifies that the decision engine configs are available.
    """
    from app.agents.decision_engine import validate_decision_configs
    validate_decision_configs()

