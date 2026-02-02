"""
Authentication request/response schemas.
"""
import logging
from pydantic import BaseModel, EmailStr

logger = logging.getLogger(__name__)


class RegisterRequest(BaseModel):
    """User registration request."""

    username: str
    email: EmailStr
    password: str


class LoginRequest(BaseModel):
    """User login request."""

    username: str
    password: str


class TokenResponse(BaseModel):
    """JWT token response."""

    access_token: str
    token_type: str = "bearer"


class UserResponse(BaseModel):
    """User data response."""

    id: str
    username: str
    email: str
    role: str


logger.debug("Auth schemas loaded")
