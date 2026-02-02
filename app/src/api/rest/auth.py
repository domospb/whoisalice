"""
Authentication REST endpoints.

POST /auth/register - Register new user
POST /auth/login - Login and get JWT token
"""
import logging
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.session import get_db
from src.services.auth_service import AuthService
from src.api.schemas.auth import (
    RegisterRequest,
    LoginRequest,
    TokenResponse,
    UserResponse,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth", tags=["Authentication"])

logger.info("Auth router initialized")


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
)
async def register(
    request: RegisterRequest,
    session: AsyncSession = Depends(get_db),
):
    """
    Register new user.

    Creates a new user account with wallet (initial balance: $0).
    """
    logger.info(f"POST /auth/register called: {request.username}")

    auth_service = AuthService(session)

    try:
        user_data = await auth_service.register_user(
            username=request.username,
            email=request.email,
            password=request.password,
        )

        logger.info(f"User registered successfully: {request.username}")

        return UserResponse(**user_data)

    except ValueError as e:
        logger.warning(f"Registration failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except Exception as e:
        logger.error(f"Registration error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Registration failed",
        )


@router.post("/login", response_model=TokenResponse)
async def login(
    request: LoginRequest,
    session: AsyncSession = Depends(get_db),
):
    """
    Login and get JWT token.

    Returns access token for authentication.
    """
    logger.info(f"POST /auth/login called: {request.username}")

    auth_service = AuthService(session)

    try:
        login_data = await auth_service.login(
            username=request.username,
            password=request.password,
        )

        logger.info(f"User logged in successfully: {request.username}")

        return TokenResponse(
            access_token=login_data["access_token"],
            token_type=login_data["token_type"],
        )

    except ValueError as e:
        logger.warning(f"Login failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except Exception as e:
        logger.error(f"Login error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Login failed",
        )
