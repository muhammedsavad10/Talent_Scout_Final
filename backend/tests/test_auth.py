"""
Unit and Integration Tests for TalentScout Enterprise Authentication System.
"""
import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_auth_login_success():
    """Verify valid recruiter credentials return JWT tokens and user profile."""
    response = client.post(
        "/api/v1/auth/login",
        json={
            "email": "recruiter@talentscout.ai",
            "password": "Recruiter123!"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"
    assert data["user"]["email"] == "recruiter@talentscout.ai"
    assert data["user"]["role"] == "recruiter"

def test_swagger_oauth2_token_form_login():
    """Verify Swagger Authorize form-data login endpoint /api/v1/auth/token operates cleanly without 422."""
    response = client.post(
        "/api/v1/auth/token",
        data={
            "username": "recruiter@talentscout.ai",
            "password": "Recruiter123!"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"
    assert data["user"]["email"] == "recruiter@talentscout.ai"

def test_auth_login_invalid_password():
    """Verify login fails with HTTP 401 when an invalid password is provided."""
    response = client.post(
        "/api/v1/auth/login",
        json={
            "email": "recruiter@talentscout.ai",
            "password": "WrongPassword123!"
        }
    )
    assert response.status_code == 401
    assert "Invalid email or password" in response.json()["detail"]

def test_auth_me_protected_route():
    """Verify /auth/me returns current user profile when bearer token is provided."""
    login_resp = client.post(
        "/api/v1/auth/login",
        json={
            "email": "recruiter@talentscout.ai",
            "password": "Recruiter123!"
        }
    )
    token = login_resp.json()["access_token"]
    
    me_resp = client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert me_resp.status_code == 200
    user_data = me_resp.json()
    assert user_data["email"] == "recruiter@talentscout.ai"

def test_auth_me_unauthorized_without_token():
    """Verify /auth/me rejects unauthenticated requests with HTTP 401."""
    response = client.get("/api/v1/auth/me")
    assert response.status_code == 401

def test_auth_token_refresh():
    """Verify valid refresh token generates a new access token."""
    login_resp = client.post(
        "/api/v1/auth/login",
        json={
            "email": "recruiter@talentscout.ai",
            "password": "Recruiter123!"
        }
    )
    refresh_token = login_resp.json()["refresh_token"]
    
    refresh_resp = client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": refresh_token}
    )
    assert refresh_resp.status_code == 200
    data = refresh_resp.json()
    assert "access_token" in data
    assert data["user"]["email"] == "recruiter@talentscout.ai"
