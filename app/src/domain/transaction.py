"""
Transaction domain models for the ML service.
"""
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4

from .enums import TransactionType
from .user import User
from .wallet import Wallet


class Transaction(ABC):
    """
    Abstract base class for wallet transactions.

    Implements polymorphic behavior for different transaction types.
    Works with Wallet for financial operations.
    """

    def __init__(
        self,
        amount: float,
        wallet: Wallet,
        transaction_type: TransactionType,
        user: Optional[User] = None,
        description: Optional[str] = None,
        transaction_id: Optional[UUID] = None,
        timestamp: Optional[datetime] = None
    ):
        """
        Initialize a Transaction instance.

        Args:
            amount: Transaction amount (must be positive)
            wallet: Wallet to perform transaction on
            transaction_type: Type of transaction (CREDIT or DEBIT)
            user: User associated with this transaction (for audit trail)
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
        self._wallet: Wallet = wallet
        self._user: Optional[User] = user
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
    def wallet(self) -> Wallet:
        """Get associated wallet."""
        return self._wallet

    @property
    def wallet_id(self) -> UUID:
        """Get associated wallet's ID."""
        return self._wallet.id

    @property
    def user(self) -> Optional[User]:
        """Get associated user (for audit trail)."""
        return self._user

    @property
    def user_id(self) -> Optional[UUID]:
        """Get associated user's ID."""
        return self._user.id if self._user else None

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
    Credit transaction for adding funds to wallet.

    Used for balance top-ups and admin moderations.
    """

    def __init__(
        self,
        amount: float,
        wallet: Wallet,
        user: Optional[User] = None,
        description: Optional[str] = None,
        transaction_id: Optional[UUID] = None,
        timestamp: Optional[datetime] = None
    ):
        """
        Initialize a CreditTransaction.

        Args:
            amount: Amount to credit (must be positive)
            wallet: Wallet to credit
            user: User associated with transaction (optional, for audit)
            description: Optional description (e.g., "Balance top-up")
            transaction_id: Unique identifier (generated if not provided)
            timestamp: Transaction timestamp (default: now)
        """
        super().__init__(
            amount=amount,
            wallet=wallet,
            transaction_type=TransactionType.CREDIT,
            user=user,
            description=description or "Balance credit",
            transaction_id=transaction_id,
            timestamp=timestamp
        )

    def apply(self) -> None:
        """
        Apply credit transaction by adding amount to wallet.

        Raises:
            ValueError: If amount is invalid (handled by Wallet.add_balance)
        """
        self._wallet.add_balance(self._amount)


class DebitTransaction(Transaction):
    """
    Debit transaction for deducting funds from wallet.

    Used when user makes ML prediction requests.
    """

    def __init__(
        self,
        amount: float,
        wallet: Wallet,
        user: Optional[User] = None,
        description: Optional[str] = None,
        ml_task_id: Optional[UUID] = None,
        transaction_id: Optional[UUID] = None,
        timestamp: Optional[datetime] = None
    ):
        """
        Initialize a DebitTransaction.

        Args:
            amount: Amount to debit (must be positive)
            wallet: Wallet to debit from
            user: User associated with transaction (optional, for audit)
            description: Optional description (e.g., "ML prediction cost")
            ml_task_id: Optional reference to associated ML task
            transaction_id: Unique identifier (generated if not provided)
            timestamp: Transaction timestamp (default: now)
        """
        super().__init__(
            amount=amount,
            wallet=wallet,
            transaction_type=TransactionType.DEBIT,
            user=user,
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
        Apply debit transaction by deducting amount from wallet.

        Raises:
            ValueError: If amount is invalid or wallet has insufficient balance
        """
        self._wallet.deduct_balance(self._amount)
