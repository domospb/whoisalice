"""
Authentication service.

Handles:
- User registration
- User login
- JWT token generation
"""
import logging
from uuid import UUID

from src.core.security import (
    get_password_hash,
    verify_password,
    create_access_token,
)
from src.db.repositories.user import UserRepository
from src.db.repositories.wallet import WalletRepository

logger = logging.getLogger(__name__)


class AuthService:
    """Authentication service."""

    def __init__(self, session):
        """Initialize with database session."""
        self.session = session
        self.user_repo = UserRepository(session)
        self.wallet_repo = WalletRepository(session)
        logger.info("AuthService initialized")

    async def register_user(self, username: str, email: str, password: str) -> dict:
        """
        Register a new user.

        Args:
            username: Unique username
            email: User email
            password: Plain text password

        Returns:
            dict with user_id, username, email, role

        Raises:
            ValueError: If username or email already exists
        """
        logger.info(f"Registering new user: {username} ({email})")

        # Check if user already exists
        existing_user = await self.user_repo.get_by_username(username)
        if existing_user:
            logger.warning(f"Registration failed: username '{username}' exists")
            raise ValueError(f"Username '{username}' already exists")

        existing_email = await self.user_repo.get_by_email(email)
        if existing_email:
            logger.warning(f"Registration failed: email '{email}' exists")
            raise ValueError(f"Email '{email}' already registered")

        # Create wallet with initial balance
        logger.debug(f"Creating wallet for user: {username}")
        wallet = await self.wallet_repo.create(balance=0.0, currency="USD")

        # Hash password
        logger.debug("Hashing password")
        password_hash = get_password_hash(password)

        # Create user
        logger.debug(f"Creating user record: {username}")
        user = await self.user_repo.create(
            username=username,
            email=email,
            password_hash=password_hash,
            role="regular",
            wallet_id=wallet.id,
        )

        logger.info(f"User registered successfully: {user.username} (ID: {user.id})")

        return {
            "id": str(user.id),
            "username": user.username,
            "email": user.email,
            "role": user.role,
        }

    async def login(self, username: str, password: str) -> dict:
        """
        Authenticate user and return JWT token.

        Args:
            username: Username
            password: Plain text password

        Returns:
            dict with access_token and user data

        Raises:
            ValueError: If credentials are invalid
        """
        logger.info(f"Login attempt for user: {username}")

        # Find user by username
        user = await self.user_repo.get_by_username(username)
        if not user:
            logger.warning(f"Login failed: username '{username}' not found")
            raise ValueError("Invalid username or password")

        # Verify password
        logger.debug("Verifying password")
        if not verify_password(password, user.password_hash):
            logger.warning(f"Login failed: invalid password for '{username}'")
            raise ValueError("Invalid username or password")

        # Create JWT token
        logger.debug(f"Creating access token for user: {user.id}")
        access_token = create_access_token(data={"sub": str(user.id)})

        logger.info(f"Login successful: {username} (ID: {user.id})")

        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user": {
                "user_id": str(user.id),
                "username": user.username,
                "email": user.email,
                "role": user.role,
            },
        }

    async def get_current_user(self, user_id: UUID) -> dict:
        """
        Get current user by ID.

        Args:
            user_id: User UUID

        Returns:
            dict with user data

        Raises:
            ValueError: If user not found
        """
        logger.debug(f"Getting user data for ID: {user_id}")

        user = await self.user_repo.get_by_id(user_id)
        if not user:
            logger.warning(f"User not found: {user_id}")
            raise ValueError("User not found")

        logger.debug(f"User found: {user.username}")

        return {
            "user_id": str(user.id),
            "username": user.username,
            "email": user.email,
            "role": user.role,
            "balance": float(user.wallet.balance) if user.wallet else 0.0,
        }
