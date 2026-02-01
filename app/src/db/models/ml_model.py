"""
ML Model database model.
"""
from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import DECIMAL, Boolean, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from ..session import Base


class MLModelModel(Base):
    """
    Database model for ML Model entity.

    Stores available ML models with their pricing and configuration.
    Each model can have different tariffication (cost_per_prediction).
    """

    __tablename__ = "ml_models"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    name: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    cost_per_prediction: Mapped[float] = mapped_column(DECIMAL(10, 2))
    version: Mapped[str] = mapped_column(String(20), default="1.0.0")
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)

    def __repr__(self) -> str:
        """String representation."""
        return f"<MLModel(id={self.id}, name='{self.name}', cost={self.cost_per_prediction})>"
