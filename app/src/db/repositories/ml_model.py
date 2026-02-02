"""
ML Model repository for database operations.
"""
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.models.ml_model import MLModelModel


class MLModelRepository:
    """Repository for ML Model database operations."""

    def __init__(self, session: AsyncSession):
        """
        Initialize repository with database session.

        Args:
            session: SQLAlchemy async session
        """
        self.session = session

    async def create(
        self,
        name: str,
        cost_per_prediction: float,
        description: str | None = None,
        version: str = "1.0.0",
        is_active: bool = True,
    ) -> MLModelModel:
        """
        Create a new ML model.

        Args:
            name: Model name
            cost_per_prediction: Cost per prediction
            description: Optional description
            version: Model version
            is_active: Whether model is active

        Returns:
            Created ML model
        """
        model = MLModelModel(
            name=name,
            description=description,
            cost_per_prediction=cost_per_prediction,
            version=version,
            is_active=is_active,
        )
        self.session.add(model)
        await self.session.commit()
        await self.session.refresh(model)
        return model

    async def get_by_id(self, model_id: UUID) -> MLModelModel | None:
        """
        Get ML model by ID.

        Args:
            model_id: Model UUID

        Returns:
            ML model or None if not found
        """
        result = await self.session.execute(
            select(MLModelModel).where(MLModelModel.id == model_id)
        )
        return result.scalar_one_or_none()

    async def get_by_name(self, name: str) -> MLModelModel | None:
        """
        Get ML model by name.

        Args:
            name: Model name

        Returns:
            ML model or None if not found
        """
        result = await self.session.execute(
            select(MLModelModel).where(MLModelModel.name == name)
        )
        return result.scalar_one_or_none()

    async def get_active_models(self) -> list[MLModelModel]:
        """
        Get all active ML models.

        Returns:
            List of active ML models
        """
        result = await self.session.execute(
            select(MLModelModel).where(MLModelModel.is_active.is_(True))
        )
        return list(result.scalars().all())
