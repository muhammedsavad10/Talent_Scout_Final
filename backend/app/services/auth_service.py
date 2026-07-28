"""
Recruiter Authentication Service for TalentScout Enterprise.
Manages recruiter account authentication, password validation, and token refresh logic.
"""
import logging
from typing import Optional, Dict, Any
from app.core.config import settings
from app.core.security import verify_password, get_password_hash, create_access_token, create_refresh_token, decode_token
from app.schemas.auth import UserResponse

logger = logging.getLogger("talentscout_auth_service")

# Server-Side Invalidated Refresh Tokens (Revocation List)
INVALIDATED_REFRESH_TOKENS = set()

# Pre-seeded Recruiter Accounts (Only active when ALLOW_DEMO_ACCOUNTS is Enabled)
def get_demo_recruiters() -> Dict[str, Dict[str, Any]]:
    if not getattr(settings, "ALLOW_DEMO_ACCOUNTS", True):
        logger.info("[AUTH] Demo recruiter accounts disabled in settings.ALLOW_DEMO_ACCOUNTS.")
        return {}
    return {
        "recruiter@talentscout.ai": {
            "id": "rec_01h8x90001_prod",
            "email": "recruiter@talentscout.ai",
            "full_name": "Lead Tech Recruiter",
            "hashed_password": get_password_hash("Recruiter123!"),
            "role": "recruiter",
            "avatar_url": "https://images.unsplash.com/photo-1534528741775-53994a69daeb?auto=format&fit=crop&q=80&w=256"
        },
        "admin@talentscout.ai": {
            "id": "rec_01h8x90002_admin",
            "email": "admin@talentscout.ai",
            "full_name": "Senior Talent Acquisition Manager",
            "hashed_password": get_password_hash("AdminRecruiter2026!"),
            "role": "admin",
            "avatar_url": "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?auto=format&fit=crop&q=80&w=256"
        }
    }

class AuthService:
    @staticmethod
    def get_user_by_email(email: str) -> Optional[Dict[str, Any]]:
        """Retrieve user profile by email address."""
        email_clean = email.strip().lower()
        recruiters = get_demo_recruiters()
        return recruiters.get(email_clean)

    @staticmethod
    def authenticate_recruiter(email: str, password: str) -> Optional[UserResponse]:
        """Authenticate recruiter email and password."""
        user = AuthService.get_user_by_email(email)
        if not user:
            logger.warning(f"[AUTH_FAILED] User with email '{email}' not found.")
            return None
            
        if not verify_password(password, user["hashed_password"]):
            logger.warning(f"[AUTH_FAILED] Invalid password attempt for email '{email}'.")
            return None
            
        return UserResponse(
            id=user["id"],
            email=user["email"],
            full_name=user["full_name"],
            role=user["role"],
            avatar_url=user.get("avatar_url")
        )

    @staticmethod
    def create_tokens_for_user(user: UserResponse) -> Dict[str, Any]:
        """Generate Access and Refresh JWT tokens containing explicit role claim."""
        payload = {
            "sub": user.id,
            "email": user.email,
            "role": user.role
        }
        access_token = create_access_token(payload)
        refresh_token = create_refresh_token(payload)
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "user": user
        }

    @staticmethod
    def invalidate_refresh_token(refresh_token: str) -> bool:
        """Register a refresh token as revoked on logout."""
        if refresh_token:
            INVALIDATED_REFRESH_TOKENS.add(refresh_token)
            logger.info("[AUTH_LOGOUT] Refresh token successfully revoked on server.")
            return True
        return False

    @staticmethod
    def refresh_access_token(refresh_token: str) -> Optional[Dict[str, Any]]:
        """Validate refresh token and issue a new access token if not revoked."""
        if refresh_token in INVALIDATED_REFRESH_TOKENS:
            logger.warning("[REFRESH_FAILED] Refresh token has been revoked on server logout.")
            return None

        payload = decode_token(refresh_token)
        if not payload or payload.get("type") != "refresh":
            logger.warning("[REFRESH_FAILED] Invalid or expired refresh token.")
            return None
            
        user_email = payload.get("email")
        if not user_email:
            return None
            
        user_dict = AuthService.get_user_by_email(user_email)
        if not user_dict:
            return None
            
        user_resp = UserResponse(
            id=user_dict["id"],
            email=user_dict["email"],
            full_name=user_dict["full_name"],
            role=user_dict["role"],
            avatar_url=user_dict.get("avatar_url")
        )
        
        new_payload = {
            "sub": user_resp.id,
            "email": user_resp.email,
            "role": user_resp.role
        }
        new_access_token = create_access_token(new_payload)
        return {
            "access_token": new_access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "user": user_resp
        }

auth_service = AuthService()
