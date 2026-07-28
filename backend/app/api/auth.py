"""
Authentication API Router for TalentScout Enterprise.
Provides endpoints for login, session verification, token refresh, and logout.
"""
import logging
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from app.schemas.auth import LoginRequest, TokenResponse, RefreshTokenRequest, UserResponse
from app.services.auth_service import auth_service
from app.core.security import decode_token

logger = logging.getLogger("talentscout_auth_api")

router = APIRouter()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/token", auto_error=False)

def get_current_user(token: Optional[str] = Depends(oauth2_scheme)) -> UserResponse:
    """
    FastAPI dependency injection to require and extract the current authenticated recruiter.
    """
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication token missing",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
    payload = decode_token(token)
    if not payload or payload.get("type") != "access":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired access token",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
    email = payload.get("email")
    if not email:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token payload invalid",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
    user_dict = auth_service.get_user_by_email(email)
    if not user_dict:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Recruiter profile not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
    return UserResponse(
        id=user_dict["id"],
        email=user_dict["email"],
        full_name=user_dict["full_name"],
        role=user_dict["role"],
        avatar_url=user_dict.get("avatar_url")
    )

@router.post("/login", response_model=TokenResponse, summary="Recruiter Login (JSON)")
async def login(credentials: LoginRequest):
    """
    Authenticate recruiter credentials via JSON (Used by React Frontend).
    """
    user = auth_service.authenticate_recruiter(credentials.email, credentials.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
    tokens = auth_service.create_tokens_for_user(user)
    return tokens

@router.post("/token", response_model=TokenResponse, summary="Swagger OAuth2 Form Login")
async def login_token(form_data: OAuth2PasswordRequestForm = Depends()):
    """
    Authenticate recruiter credentials via OAuth2 form-data (Used by Swagger UI Authorize button).
    Reuses the exact same auth_service authentication logic.
    """
    user = auth_service.authenticate_recruiter(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
    tokens = auth_service.create_tokens_for_user(user)
    return tokens

@router.get("/me", response_model=UserResponse, summary="Current User Profile")
async def get_me(current_user: UserResponse = Depends(get_current_user)):
    """
    Return profile details for the currently authenticated recruiter.
    """
    return current_user

@router.post("/refresh", response_model=TokenResponse, summary="Refresh Access Token")
async def refresh_token(body: RefreshTokenRequest):
    """
    Validate refresh token and issue a new access token.
    """
    tokens = auth_service.refresh_access_token(body.refresh_token)
    if not tokens:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return tokens

@router.post("/logout", summary="Recruiter Logout")
async def logout(body: Optional[RefreshTokenRequest] = None, current_user: UserResponse = Depends(get_current_user)):
    """
    Logout currently authenticated recruiter and revoke refresh token session.
    """
    if body and body.refresh_token:
        auth_service.invalidate_refresh_token(body.refresh_token)
    logger.info(f"[LOGOUT] Recruiter {current_user.email} logged out successfully.")
    return {"success": True, "message": "Logged out successfully and session revoked."}
