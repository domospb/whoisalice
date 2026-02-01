"""
Wallet domain model for financial operations.
"""
from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4


class Wallet:
    """
    Wallet class for managing user's financial balance and operations.

    Handles all currency, balance, and financial operations.
    Separated from User to follow Single Responsibility Principle.
    """

    def __init__(
        self,
        wallet_id: Optional[UUID] = None,
        balance: float = 0.0,
        currency: str = "USD",
        created_at: Optional[datetime] = None,
    ):
        """
        Initialize a Wallet instance.

        Args:
            wallet_id: Unique identifier (generated if not provided)
            balance: Initial balance (default: 0.0)
            currency: Currency code (default: USD)
            created_at: Wallet creation timestamp (default: now)
        """
        self._id: UUID = wallet_id or uuid4()
        self._balance: float = balance
        self._currency: str = currency
        self._created_at: datetime = created_at or datetime.utcnow()

    # Getters (encapsulation)
    @property
    def id(self) -> UUID:
        """Get wallet ID."""
        return self._id

    @property
    def balance(self) -> float:
        """Get current balance."""
        return self._balance

    @property
    def currency(self) -> str:
        """Get currency code."""
        return self._currency

    @property
    def created_at(self) -> datetime:
        """Get wallet creation timestamp."""
        return self._created_at

    # Balance management methods
    def add_balance(self, amount: float) -> None:
        """
        Add credits to wallet balance.

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
        Deduct credits from wallet balance.

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
        Check if wallet can afford a given amount.

        Args:
            amount: Amount to check

        Returns:
            True if balance is sufficient, False otherwise
        """
        return self._balance >= amount

    def __repr__(self) -> str:
        """String representation of Wallet."""
        return (
            f"Wallet(id={self._id}, balance={self._balance}, "
            f"currency='{self._currency}')"
        )
