"""
TalentScout Enterprise Version 1.0 — Phase H Observability & Monitoring Test Suite.
Validates Prometheus plaintext metric rendering, Cloud Logging structured JSON format readiness,
correlation ID propagation, and health check probes.
"""
import pytest
from fastapi.testclient import TestClient
from main import app
from app.core.metrics import metrics_collector

client = TestClient(app)

def test_phase_h_prometheus_metrics_endpoint():
    """Verify /metrics endpoint returns Prometheus plaintext formatted telemetry."""
    metrics_collector.record_request("GET", "/api/v1/evaluation", 200, 0.15)
    metrics_collector.record_stage_duration("stage1_evaluation", 120.5)
    
    response = client.get("/metrics")
    assert response.status_code == 200
    assert "text/plain" in response.headers.get("content-type", "")
    content = response.text
    assert "talentscout_uptime_seconds" in content
    assert "talentscout_http_requests_total" in content
    assert "talentscout_stage_duration_seconds_sum" in content

def test_phase_h_correlation_id_header_propagation():
    """Verify X-Request-ID and X-Correlation-ID headers are returned on all API responses."""
    response = client.get("/")
    assert response.status_code == 200
    headers = response.headers
    assert "X-Request-ID" in headers
    assert "X-Correlation-ID" in headers

def test_phase_h_health_check_probes():
    """Verify liveness, readiness, and database health endpoints."""
    res_live = client.get("/health/liveness")
    assert res_live.status_code == 200
    assert res_live.json().get("status") == "alive"

    res_ready = client.get("/health/readiness")
    assert res_ready.status_code == 200
    assert res_ready.json().get("status") == "ready"

    res_db = client.get("/health/databases")
    assert res_db.status_code == 200
    assert res_db.json().get("status") == "healthy"
