"""
Wallet repository for database operations.
"""
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..models.wallet import WalletModel


class WalletRepository:
    """Repository for Wallet database operations."""

    def __init__(self, session: AsyncSession):
        """
        Initialize repository with database session.

        Args:
            session: SQLAlchemy async session
        """
        self.session = session

    async def create(
        self, balance: float = 0.0, currency: str = "USD"
    ) -> WalletModel:
        """
        Create a new wallet.

        Args:
            balance: Initial balance
            currency: Currency code

        Returns:
            Created wallet
        """
        wallet = WalletModel(balance=balance, currency=currency)
        self.session.add(wallet)
        await self.session.commit()
        await self.session.refresh(wallet)
        return wallet

    async def get_by_id(self, wallet_id: UUID) -> WalletModel | None:
        """
        Get wallet by ID.

        Args:
            wallet_id: Wallet UUID

        Returns:
            Wallet or None if not found
        """
        result = await self.session.execute(
            select(WalletModel).where(WalletModel.id == wallet_id)
        )
        return result.scalar_one_or_none()

    async def update_balance(
        self, wallet_id: UUID, new_balance: float
    ) -> WalletModel | None:
        """
        Update wallet balance.

        Args:
            wallet_id: Wallet UUID
            new_balance: New balance value

        Returns:
            Updated wallet or None if not found
        """
        wallet = await self.get_by_id(wallet_id)
        if wallet:
            wallet.balance = new_balance
            await self.session.commit()
            await self.session.refresh(wallet)
        return wallet
