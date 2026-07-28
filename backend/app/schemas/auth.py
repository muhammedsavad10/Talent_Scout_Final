"""
Authentication Pydantic schemas for TalentScout Enterprise.
"""
from typing import Optional
from pydantic import BaseModel

class LoginRequest(BaseModel):
    email: str
    password: str

class RefreshTokenRequest(BaseModel):
    refresh_token: str

class UserResponse(BaseModel):
    id: str
    email: str
    full_name: str
    role: str = "recruiter"
    avatar_url: Optional[str] = None

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user: UserResponse

class AuthStatusResponse(BaseModel):
    authenticated: bool
    user: Optional[UserResponse] = None
