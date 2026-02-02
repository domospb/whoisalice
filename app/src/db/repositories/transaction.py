"""
Transaction repository for database operations.
"""
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.models.transaction import TransactionModel


class TransactionRepository:
    """Repository for Transaction database operations."""

    def __init__(self, session: AsyncSession):
        """
        Initialize repository with database session.

        Args:
            session: SQLAlchemy async session
        """
        self.session = session

    async def create(
        self,
        amount: float,
        transaction_type: str,
        wallet_id: UUID,
        user_id: UUID | None = None,
        ml_task_id: UUID | None = None,
        description: str = "",
    ) -> TransactionModel:
        """
        Create a new transaction.

        Args:
            amount: Transaction amount
            transaction_type: Type (credit or debit)
            wallet_id: Wallet UUID
            user_id: Optional user UUID
            ml_task_id: Optional ML task UUID
            description: Transaction description

        Returns:
            Created transaction
        """
        transaction = TransactionModel(
            amount=amount,
            transaction_type=transaction_type,
            wallet_id=wallet_id,
            user_id=user_id,
            ml_task_id=ml_task_id,
            description=description,
        )
        self.session.add(transaction)
        await self.session.commit()
        await self.session.refresh(transaction)
        return transaction

    async def get_by_wallet(self, wallet_id: UUID) -> list[TransactionModel]:
        """
        Get all transactions for a wallet, sorted by timestamp (newest first).

        Args:
            wallet_id: Wallet UUID

        Returns:
            List of transactions
        """
        result = await self.session.execute(
            select(TransactionModel)
            .where(TransactionModel.wallet_id == wallet_id)
            .order_by(TransactionModel.timestamp.desc())
        )
        return list(result.scalars().all())

    async def get_by_user(self, user_id: UUID) -> list[TransactionModel]:
        """
        Get all transactions for a user, sorted by timestamp (newest first).

        Args:
            user_id: User UUID

        Returns:
            List of transactions
        """
        result = await self.session.execute(
            select(TransactionModel)
            .where(TransactionModel.user_id == user_id)
            .order_by(TransactionModel.timestamp.desc())
        )
        return list(result.scalars().all())
