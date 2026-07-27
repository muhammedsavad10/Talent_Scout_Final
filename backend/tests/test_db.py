"""
Tests for Core Configuration and Database Clients of TalentScout Enterprise.
"""
import pytest
from pydantic import ValidationError
from app.core.config import Settings
from app.db.clients import get_supabase_client, get_qdrant_client

def test_settings_missing_critical_keys(monkeypatch):
    """
    Test that Settings validation fails when critical environment keys are missing.
    """
    # Remove variables from the environment for the scope of this validation test
    monkeypatch.delenv("GROQ_API_KEY", raising=False)
    monkeypatch.delenv("SUPABASE_URL", raising=False)
    monkeypatch.delenv("SUPABASE_KEY", raising=False)
    monkeypatch.delenv("QDRANT_URL", raising=False)
    monkeypatch.delenv("QDRANT_API_KEY", raising=False)
    
    with pytest.raises(ValidationError):
        Settings(_env_file=None)

def test_get_supabase_client_success(mocker):
    """
    Test successful Supabase client creation using mock.
    """
    mock_create = mocker.patch("app.db.clients.create_client")
    mock_client = mocker.MagicMock()
    mock_create.return_value = mock_client
    
    client = get_supabase_client()
    assert client == mock_client
    mock_create.assert_called_once()

def test_get_supabase_client_failure(mocker):
    """
    Test that Supabase client creation returns None gracefully upon failure (Phase D Memory Fallback).
    """
    mocker.patch("app.db.clients.create_client", side_effect=Exception("Supabase connection error"))
    client = get_supabase_client()
    assert client is None

def test_get_qdrant_client_success(mocker):
    """
    Test successful Qdrant client creation using mock.
    """
    mock_qdrant_class = mocker.patch("app.db.clients.QdrantClient")
    mock_client = mocker.MagicMock()
    mock_qdrant_class.return_value = mock_client
    
    client = get_qdrant_client()
    assert client == mock_client
    mock_qdrant_class.assert_called_once()

def test_get_qdrant_client_failure(mocker):
    """
    Test that Qdrant client creation returns None gracefully upon failure (Phase D Memory Fallback).
    """
    mocker.patch("app.db.clients.QdrantClient", side_effect=Exception("Qdrant database error"))
    client = get_qdrant_client()
    assert client is None
