"""
Transaction database model.
"""
from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID, uuid4

from sqlalchemy import DECIMAL, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.db.session import Base

if TYPE_CHECKING:
    from .user import UserModel
    from .wallet import WalletModel


class TransactionModel(Base):
    """
    Database model for Transaction entity.

    Stores financial transaction history (credit/debit operations).
    """

    __tablename__ = "transactions"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    amount: Mapped[float] = mapped_column(DECIMAL(10, 2))
    transaction_type: Mapped[str] = mapped_column(String(10))
    description: Mapped[str] = mapped_column(Text, default="")
    wallet_id: Mapped[UUID] = mapped_column(
        ForeignKey("wallets.id", ondelete="CASCADE")
    )
    user_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    ml_task_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("ml_tasks.id", ondelete="SET NULL"), nullable=True
    )
    timestamp: Mapped[datetime] = mapped_column(default=datetime.utcnow, index=True)

    # Relationships
    wallet: Mapped["WalletModel"] = relationship()
    user: Mapped["UserModel"] = relationship()

    def __repr__(self) -> str:
        """String representation."""
        return (
            f"<Transaction(id={self.id}, type={self.transaction_type}, "
            f"amount={self.amount})>"
        )
