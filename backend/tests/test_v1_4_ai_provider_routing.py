"""
TalentScout Enterprise v1.4 — AI Provider Routing & Failover Test Suite.
Verifies GEMINI_API_KEY environment loading, startup health check,
deterministic task routing to Gemini, and immediate 429 rate-limit failover.
"""
import os
import pytest
from app.core.config import settings
from app.services.ai_gateway import check_llm_providers_health, ai_gateway

def test_env_loading_and_gemini_key_presence():
    gemini_key = getattr(settings, "GEMINI_API_KEY", os.environ.get("GEMINI_API_KEY", os.environ.get("GOOGLE_API_KEY", "")))
    assert gemini_key is not None
    assert len(gemini_key) > 5

def test_health_check_returns_valid_provider_status():
    health = check_llm_providers_health()
    assert health["gemini_enabled"] is True
    assert health["gemini_key_loaded"] is True
    assert health["primary_extraction_provider"] == "gemini"
    assert health["primary_generation_provider"] == "gemini"

def test_deterministic_task_routing_defaults_to_gemini():
    assert settings.PRIMARY_EXTRACTION_PROVIDER == "gemini"
    assert settings.PRIMARY_GENERATION_PROVIDER == "gemini"
    assert settings.PRIMARY_ASSISTANT_PROVIDER == "gemini"

def test_429_rate_limit_triggers_immediate_failover(mocker):
    # Mock _call_gemini_api to raise 429 rate limit error
    mock_gemini = mocker.patch.object(
        ai_gateway, "_call_gemini_api", side_effect=RuntimeError("HTTP 429 Too Many Requests: Rate limit exceeded")
    )
    # Mock _call_groq_api to return success
    mock_groq = mocker.patch.object(
        ai_gateway, "_call_groq_api", return_value="Groq Fallback Success Response"
    )

    messages = [{"role": "user", "content": "Test prompt"}]
    res = ai_gateway.execute_request(messages, stage="test_stage", task_type="extraction")

    assert res == "Groq Fallback Success Response"
    # Assert _call_gemini_api was called ONCE before immediate failover to Groq
    assert mock_gemini.call_count == 1
    assert mock_groq.call_count == 1
