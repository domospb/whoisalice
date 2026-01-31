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
    Encapsulates user data and balance management logic.
    """
  
    def __init__(
        self,
        username: str,
        email: str,
        password_hash: str,
        role: UserRole,
        user_id: Optional[UUID] = None,
        balance: float = 0.0,
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
            balance: Initial balance in credits (default: 0.0)
            created_at: Account creation timestamp (default: now)
        """
        self._id: UUID = user_id or uuid4()
        self._username: str = username
        self._email: str = email
        self._password_hash: str = password_hash
        self._role: UserRole = role
        self._balance: float = balance
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
    def balance(self) -> float:
        """Get current balance."""
        return self._balance

    @property
    def created_at(self) -> datetime:
        """Get account creation timestamp."""
        return self._created_at

    # Balance management methods
    def add_balance(self, amount: float) -> None:
        """
        Add credits to user's balance.

        Args:
            amount: Amount to add (must be positive)

        Raises:
            ValueError: If amount is not positive
        """
        if amount <= 0:
            raise ValueError("Amount to add must be positive")
        self._balance += amount

    def deduct_balance(self, amount: float) -> None:
        """
        Deduct credits from user's balance.

        Args:
            amount: Amount to deduct (must be positive)

        Raises:
            ValueError: If amount is not positive or exceeds balance
        """
        if amount <= 0:
            raise ValueError("Amount to deduct must be positive")
        if amount > self._balance:
            raise ValueError("Insufficient balance")
        self._balance -= amount

    def can_afford(self, amount: float) -> bool:
        """
        Check if user can afford a given amount.

        Args:
            amount: Amount to check

        Returns:
            True if balance is sufficient, False otherwise
        """
        return self._balance >= amount

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
            f"role={self._role.value}, balance={self._balance})"
        )


class RegularUser(User):
    """
    Regular user with standard privileges.

    Can perform ML predictions and manage their own balance.
    """
    
    def __init__(
        self,
        username: str,
        email: str,
        password_hash: str,
        user_id: Optional[UUID] = None,
        balance: float = 0.0,
        created_at: Optional[datetime] = None
    ):
        """Initialize a RegularUser with REGULAR role."""
        super().__init__(
            username=username,
            email=email,
            password_hash=password_hash,
            role=UserRole.REGULAR,
            user_id=user_id,
            balance=balance,
            created_at=created_at
        )


class AdminUser(User):
    """
    Administrator user with elevated privileges.

    Can manage other users' balances and view all transactions.
    """

    def __init__(
        self,
        username: str,
        email: str,
        password_hash: str,
        user_id: Optional[UUID] = None,
        balance: float = 0.0,
        created_at: Optional[datetime] = None
    ):
        """Initialize an AdminUser with ADMIN role."""
        super().__init__(
            username=username,
            email=email,
            password_hash=password_hash,
            role=UserRole.ADMIN,
            user_id=user_id,
            balance=balance,
            created_at=created_at
        )

    def moderate_balance(self, target_user: User, amount: float) -> None:
        """
        Add credits to another user's balance (admin privilege).

        Args:
            target_user: User whose balance to modify
            amount: Amount to add (must be positive)

        Raises:
            ValueError: If amount is not positive
        """
        if amount <= 0:
            raise ValueError("Amount to add must be positive")
        target_user.add_balance(amount)
