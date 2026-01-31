"""
Transaction domain models for the ML service.
"""
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4

from .enums import TransactionType
from .user import User


class Transaction(ABC):
    """
    Abstract base class for balance transactions.

    Implements polymorphic behavior for different transaction types.
    """

    def __init__(
        self,
        amount: float,
        user: User,
        transaction_type: TransactionType,
        description: Optional[str] = None,
        transaction_id: Optional[UUID] = None,
        timestamp: Optional[datetime] = None
    ):
        """
        Initialize a Transaction instance.

        Args:
            amount: Transaction amount (must be positive)
            user: User associated with this transaction
            transaction_type: Type of transaction (CREDIT or DEBIT)
            description: Optional description of the transaction
            transaction_id: Unique identifier (generated if not provided)
            timestamp: Transaction timestamp (default: now)

        Raises:
            ValueError: If amount is not positive
        """
        if amount <= 0:
            raise ValueError("Transaction amount must be positive")

        self._id: UUID = transaction_id or uuid4()
        self._amount: float = amount
        self._user: User = user
        self._transaction_type: TransactionType = transaction_type
        self._description: str = description or ""
        self._timestamp: datetime = timestamp or datetime.utcnow()

    # Getters (encapsulation)
    @property
    def id(self) -> UUID:
        """Get transaction ID."""
        return self._id

    @property
    def amount(self) -> float:
        """Get transaction amount."""
        return self._amount

    @property
    def user(self) -> User:
        """Get associated user."""
        return self._user

    @property
    def user_id(self) -> UUID:
        """Get associated user's ID."""
        return self._user.id

    @property
    def transaction_type(self) -> TransactionType:
        """Get transaction type."""
        return self._transaction_type

    @property
    def description(self) -> str:
        """Get transaction description."""
        return self._description

    @property
    def timestamp(self) -> datetime:
        """Get transaction timestamp."""
        return self._timestamp

    @abstractmethod
    def apply(self) -> None:
        """
        Apply the transaction to the user's balance.

        This method must be implemented by subclasses to define
        specific behavior for different transaction types.
        """
        pass

    def __repr__(self) -> str:
        """String representation of Transaction."""
        return (
            f"{self.__class__.__name__}(id={self._id}, "
            f"amount={self._amount}, user_id={self.user_id}, "
            f"timestamp={self._timestamp})"
        )


class CreditTransaction(Transaction):
    """
    Credit transaction for adding funds to user's balance.

    Used for balance top-ups and admin moderations.
    """

    def __init__(
        self,
        amount: float,
        user: User,
        description: Optional[str] = None,
        transaction_id: Optional[UUID] = None,
        timestamp: Optional[datetime] = None
    ):
        """
        Initialize a CreditTransaction.

        Args:
            amount: Amount to credit (must be positive)
            user: User receiving the credits
            description: Optional description (e.g., "Balance top-up")
            transaction_id: Unique identifier (generated if not provided)
            timestamp: Transaction timestamp (default: now)
        """
        super().__init__(
            amount=amount,
            user=user,
            transaction_type=TransactionType.CREDIT,
            description=description or "Balance credit",
            transaction_id=transaction_id,
            timestamp=timestamp
        )

    def apply(self) -> None:
        """
        Apply credit transaction by adding amount to user's balance.

        Raises:
            ValueError: If amount is invalid (handled by User.add_balance)
        """
        self._user.add_balance(self._amount)


class DebitTransaction(Transaction):
    """
    Debit transaction for deducting funds from user's balance.

    Used when user makes ML prediction requests.
    """

    def __init__(
        self,
        amount: float,
        user: User,
        description: Optional[str] = None,
        ml_task_id: Optional[UUID] = None,
        transaction_id: Optional[UUID] = None,
        timestamp: Optional[datetime] = None
    ):
        """
        Initialize a DebitTransaction.

        Args:
            amount: Amount to debit (must be positive)
            user: User being charged
            description: Optional description (e.g., "ML prediction cost")
            ml_task_id: Optional reference to associated ML task
            transaction_id: Unique identifier (generated if not provided)
            timestamp: Transaction timestamp (default: now)
        """
        super().__init__(
            amount=amount,
            user=user,
            transaction_type=TransactionType.DEBIT,
            description=description or "Balance debit",
            transaction_id=transaction_id,
            timestamp=timestamp
        )
        self._ml_task_id: Optional[UUID] = ml_task_id

    @property
    def ml_task_id(self) -> Optional[UUID]:
        """Get associated ML task ID if any."""
        return self._ml_task_id

    def apply(self) -> None:
        """
        Apply debit transaction by deducting amount from user's balance.

        Raises:
            ValueError: If amount is invalid or user has insufficient balance
        """
        self._user.deduct_balance(self._amount)
