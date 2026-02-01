"""
User domain models for the ML service.
"""
from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4

from .enums import UserRole


class User:
    """
    Base User class representing a user in the ML service.  
    Encapsulates user data. Financial operations are handled by Wallet class.
    """
  
    def __init__(
        self,
        username: str,
        email: str,
        password_hash: str,
        role: UserRole,
        user_id: Optional[UUID] = None,
        wallet_id: Optional[UUID] = None,
        created_at: Optional[datetime] = None
    ):
        """
        Initialize a User instance.
        Args:
            username: Unique username for the user
            email: User's email address
            password_hash: Hashed password for authentication
            role: User role (REGULAR or ADMIN)
            user_id: Unique identifier (generated if not provided)
            wallet_id: Reference to user's Wallet (optional)
            created_at: Account creation timestamp (default: now)
        """
        self._id: UUID = user_id or uuid4()
        self._username: str = username
        self._email: str = email
        self._password_hash: str = password_hash
        self._role: UserRole = role
        self._wallet_id: Optional[UUID] = wallet_id
        self._created_at: datetime = created_at or datetime.utcnow()
   
    # Getters (encapsulation)
    @property
    def id(self) -> UUID:
        """Get user ID."""
        return self._id

    @property
    def username(self) -> str:
        """Get username."""
        return self._username

    @property
    def email(self) -> str:
        """Get email."""
        return self._email

    @property
    def password_hash(self) -> str:
        """Get password hash."""
        return self._password_hash

    @property
    def role(self) -> UserRole:
        """Get user role."""
        return self._role

    @property
    def wallet_id(self) -> Optional[UUID]:
        """Get wallet ID reference."""
        return self._wallet_id

    @property
    def created_at(self) -> datetime:
        """Get account creation timestamp."""
        return self._created_at

    def is_admin(self) -> bool:
        """
        Check if user has admin role.

        Returns:
            True if user is admin, False otherwise
        """
        return self._role == UserRole.ADMIN

    def __repr__(self) -> str:
        """String representation of User."""
        return (
            f"User(id={self._id}, username='{self._username}', "
            f"role={self._role.value}, wallet_id={self._wallet_id})"
        )


class RegularUser(User):
    """
    Regular user with standard privileges.

    Can perform ML predictions. Balance managed via separate Wallet.
    """
    
    def __init__(
        self,
        username: str,
        email: str,
        password_hash: str,
        user_id: Optional[UUID] = None,
        wallet_id: Optional[UUID] = None,
        created_at: Optional[datetime] = None
    ):
        """Initialize a RegularUser with REGULAR role."""
        super().__init__(
            username=username,
            email=email,
            password_hash=password_hash,
            role=UserRole.REGULAR,
            user_id=user_id,
            wallet_id=wallet_id,
            created_at=created_at
        )


class AdminUser(User):
    """
    Administrator user with elevated privileges.

    Can manage wallets and view all transactions.
    """

    def __init__(
        self,
        username: str,
        email: str,
        password_hash: str,
        user_id: Optional[UUID] = None,
        wallet_id: Optional[UUID] = None,
        created_at: Optional[datetime] = None
    ):
        """Initialize an AdminUser with ADMIN role."""
        super().__init__(
            username=username,
            email=email,
            password_hash=password_hash,
            role=UserRole.ADMIN,
            user_id=user_id,
            wallet_id=wallet_id,
            created_at=created_at
        )
