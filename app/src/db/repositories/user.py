"""
User repository for database operations.
"""
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.db.models.user import UserModel


class UserRepository:
    """Repository for User database operations."""

    def __init__(self, session: AsyncSession):
        """
        Initialize repository with database session.

        Args:
            session: SQLAlchemy async session
        """
        self.session = session

    async def create(
        self,
        username: str,
        email: str,
        password_hash: str,
        role: str = "regular",
        wallet_id: UUID | None = None,
    ) -> UserModel:
        """
        Create a new user.

        Args:
            username: Unique username
            email: Unique email
            password_hash: Hashed password
            role: User role (regular or admin)
            wallet_id: Optional wallet reference

        Returns:
            Created user
        """
        user = UserModel(
            username=username,
            email=email,
            password_hash=password_hash,
            role=role,
            wallet_id=wallet_id,
        )
        self.session.add(user)
        await self.session.commit()
        await self.session.refresh(user)
        return user

    async def get_by_id(self, user_id: UUID) -> UserModel | None:
        """
        Get user by ID with wallet loaded.

        Args:
            user_id: User UUID

        Returns:
            User or None if not found
        """
        result = await self.session.execute(
            select(UserModel)
            .where(UserModel.id == user_id)
            .options(selectinload(UserModel.wallet))
        )
        return result.scalar_one_or_none()

    async def get_by_username(self, username: str) -> UserModel | None:
        """
        Get user by username.

        Args:
            username: Username to search

        Returns:
            User or None if not found
        """
        result = await self.session.execute(
            select(UserModel)
            .where(UserModel.username == username)
            .options(selectinload(UserModel.wallet))
        )
        return result.scalar_one_or_none()

    async def get_by_email(self, email: str) -> UserModel | None:
        """
        Get user by email.

        Args:
            email: Email to search

        Returns:
            User or None if not found
        """
        result = await self.session.execute(
            select(UserModel)
            .where(UserModel.email == email)
            .options(selectinload(UserModel.wallet))
        )
        return result.scalar_one_or_none()
