"""
User database model.
"""
from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID, uuid4

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..session import Base

if TYPE_CHECKING:
    from .wallet import WalletModel


class UserModel(Base):
    """
    Database model for User entity.

    Stores user account information and references wallet.
    """

    __tablename__ = "users"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    username: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    email: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    role: Mapped[str] = mapped_column(String(20), default="regular")
    wallet_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("wallets.id", ondelete="SET NULL"), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)

    # Relationships
    wallet: Mapped["WalletModel"] = relationship(lazy="joined")

    def __repr__(self) -> str:
        """String representation."""
        return f"<User(id={self.id}, username='{self.username}', role='{self.role}')>"
