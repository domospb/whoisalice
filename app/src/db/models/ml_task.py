"""
ML Task database models.
"""
from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID, uuid4

from sqlalchemy import ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.db.session import Base

if TYPE_CHECKING:
    from .ml_model import MLModelModel
    from .user import UserModel


class PredictionResultModel(Base):
    """
    Database model for PredictionResult entity.

    Stores ML prediction results with valid/invalid data counts.
    """

    __tablename__ = "prediction_results"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    prediction_data: Mapped[str] = mapped_column(Text)
    valid_data: Mapped[int] = mapped_column(Integer, default=0)
    invalid_data: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)

    def __repr__(self) -> str:
        """String representation."""
        return (
            f"<PredictionResult(id={self.id}, valid={self.valid_data}, "
            f"invalid={self.invalid_data})>"
        )


class MLTaskModel(Base):
    """
    Database model for MLTask entity.

    Stores ML prediction tasks with their status and results.
    """

    __tablename__ = "ml_tasks"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    model_id: Mapped[UUID] = mapped_column(
        ForeignKey("ml_models.id", ondelete="RESTRICT")
    )
    input_data: Mapped[str] = mapped_column(Text)
    input_type: Mapped[str] = mapped_column(String(10))  # text or audio
    output_type: Mapped[str] = mapped_column(String(10))  # text or audio
    status: Mapped[str] = mapped_column(String(20), default="pending", index=True)
    result_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("prediction_results.id", ondelete="SET NULL"), nullable=True
    )
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow, index=True)
    completed_at: Mapped[datetime | None] = mapped_column(nullable=True)

    # Relationships
    user: Mapped["UserModel"] = relationship()
    model: Mapped["MLModelModel"] = relationship()
    result: Mapped["PredictionResultModel"] = relationship()

    def __repr__(self) -> str:
        """String representation."""
        return f"<MLTask(id={self.id}, status='{self.status}')>"
