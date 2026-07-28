"""
Tests for the FastAPI Gateway (main.py) endpoints.
"""
import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_root_endpoint():
    """
    Test that the root health check endpoint returns 200 OK and expected welcome payload.
    """
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {
        "message": "Welcome to the TalentScout API Gateway",
        "status": "healthy"
    }

def test_health_databases_success(mocker):
    """
    Test /health/databases happy path: database clients are healthy.
    """
    # Mocking supabase_db and qdrant_db in app.db.clients
    mocker.patch("app.db.clients.supabase_db")
    mock_qdrant = mocker.patch("app.db.clients.qdrant_db")
    
    # Mock get_collections returning an object with a collections array
    mock_collections_obj = mocker.MagicMock()
    mock_collections_obj.collections = []
    mock_qdrant.get_collections.return_value = mock_collections_obj
    
    response = client.get("/health/databases")
    assert response.status_code == 200
    assert response.json() == {
        "status": "healthy",
        "supabase": "connected",
        "qdrant": "connected",
        "qdrant_collections": 0
    }

def test_health_databases_disaster_qdrant_failure(mocker):
    """
    Test /health/databases disaster path: Qdrant client throws exception.
    Ensures gateway returns 503 Service Unavailable instead of crashing.
    """
    mocker.patch("app.db.clients.get_supabase_client")
    mock_get_qd = mocker.patch("app.db.clients.get_qdrant_client")
    mock_qd_instance = mocker.MagicMock()
    mock_qd_instance.get_collections.side_effect = Exception("Vector DB Server down")
    mock_get_qd.return_value = mock_qd_instance
    
    response = client.get("/health/databases")
    assert response.status_code == 503
    assert response.json()["detail"] == "Database connection degraded."

def test_health_databases_disaster_import_failure(mocker):
    """
    Test /health/databases disaster path: Database client fails to import/is not initialized.
    Ensures gateway returns 503 Service Unavailable instead of crashing.
    """
    mocker.patch("app.db.clients.get_supabase_client", side_effect=Exception("Supabase connection timeout"))
    
    response = client.get("/health/databases")
    assert response.status_code == 503
    assert response.json()["detail"] == "Database connection degraded."
