"""
Authentication REST endpoints.

POST /auth/register - Register new user
POST /auth/login - Login and get JWT token
"""
import logging
from fastapi import APIRouter, Depends, HTTPException

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth", tags=["Authentication"])

logger.info("Auth router initialized")


@router.post("/register")
async def register():
    """Register new user."""
    logger.info("POST /auth/register called")
    # TODO: Implement registration
    raise HTTPException(status_code=501, detail="Not implemented yet")


@router.post("/login")
async def login():
    """Login and get JWT token."""
    logger.info("POST /auth/login called")
    # TODO: Implement login
    raise HTTPException(status_code=501, detail="Not implemented yet")
