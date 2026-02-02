"""
Wallet database model.
"""
from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import DECIMAL, String
from sqlalchemy.orm import Mapped, mapped_column

from src.db.session import Base


class WalletModel(Base):
    """
    Database model for Wallet entity.

    Stores user financial balance and currency information.
    """

    __tablename__ = "wallets"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    balance: Mapped[float] = mapped_column(DECIMAL(10, 2), default=0.0)
    currency: Mapped[str] = mapped_column(String(3), default="USD")
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)

    def __repr__(self) -> str:
        """String representation."""
        return f"<Wallet(id={self.id}, balance={self.balance})>"
