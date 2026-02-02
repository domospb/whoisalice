"""
ML Task repository for database operations.
"""
import logging
from datetime import datetime
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from ..models.ml_task import MLTaskModel, PredictionResultModel

logger = logging.getLogger(__name__)


class MLTaskRepository:
    """Repository for ML Task database operations."""

    def __init__(self, session: AsyncSession):
        """
        Initialize repository with database session.

        Args:
            session: SQLAlchemy async session
        """
        self.session = session

    async def create(
        self,
        user_id: UUID,
        model_id: UUID,
        input_data: str,
        input_type: str,
        output_type: str,
        status: str = "pending",
    ) -> MLTaskModel:
        """
        Create a new ML task.

        Args:
            user_id: User UUID
            model_id: ML Model UUID
            input_data: Input data (text or file path)
            input_type: Type of input (text or audio)
            output_type: Type of output (text or audio)
            status: Initial status (default: pending)

        Returns:
            Created ML task
        """
        logger.info(f"Creating ML task for user {user_id}, model {model_id}")

        task = MLTaskModel(
            user_id=user_id,
            model_id=model_id,
            input_data=input_data,
            input_type=input_type,
            output_type=output_type,
            status=status,
        )

        self.session.add(task)
        await self.session.commit()
        await self.session.refresh(task)

        logger.info(f"ML task created: {task.id}, status: {status}")

        return task

    async def get_by_id(self, task_id: UUID) -> MLTaskModel | None:
        """
        Get ML task by ID.

        Args:
            task_id: Task UUID

        Returns:
            ML task or None if not found
        """
        logger.debug(f"Getting ML task by ID: {task_id}")

        result = await self.session.execute(
            select(MLTaskModel)
            .where(MLTaskModel.id == task_id)
            .options(
                selectinload(MLTaskModel.user),
                selectinload(MLTaskModel.model),
                selectinload(MLTaskModel.result),
            )
        )

        task = result.scalar_one_or_none()

        if task:
            logger.debug(f"Task found: {task.id}, status: {task.status}")
        else:
            logger.debug(f"Task not found: {task_id}")

        return task

    async def get_by_user(self, user_id: UUID) -> list[MLTaskModel]:
        """
        Get all tasks for a user.

        Args:
            user_id: User UUID

        Returns:
            List of ML tasks
        """
        logger.debug(f"Getting ML tasks for user: {user_id}")

        result = await self.session.execute(
            select(MLTaskModel)
            .where(MLTaskModel.user_id == user_id)
            .options(
                selectinload(MLTaskModel.model),
                selectinload(MLTaskModel.result),
            )
            .order_by(MLTaskModel.created_at.desc())
        )

        tasks = list(result.scalars().all())

        logger.debug(f"Found {len(tasks)} tasks for user {user_id}")

        return tasks

    async def update_status(
        self, task_id: UUID, status: str, error_message: str | None = None
    ) -> MLTaskModel | None:
        """
        Update task status.

        Args:
            task_id: Task UUID
            status: New status
            error_message: Optional error message

        Returns:
            Updated task or None if not found
        """
        logger.info(f"Updating task {task_id} status to: {status}")

        task = await self.get_by_id(task_id)

        if not task:
            logger.warning(f"Task not found for update: {task_id}")
            return None

        task.status = status

        if error_message:
            task.error_message = error_message

        if status in ["completed", "failed"]:
            task.completed_at = datetime.utcnow()

        await self.session.commit()
        await self.session.refresh(task)

        logger.info(f"Task {task_id} updated to status: {status}")

        return task

    async def complete_task(
        self, task_id: UUID, result_id: UUID
    ) -> MLTaskModel | None:
        """
        Mark task as completed with result.

        Args:
            task_id: Task UUID
            result_id: PredictionResult UUID

        Returns:
            Updated task or None if not found
        """
        logger.info(f"Completing task {task_id} with result {result_id}")

        task = await self.get_by_id(task_id)

        if not task:
            logger.warning(f"Task not found for completion: {task_id}")
            return None

        task.status = "completed"
        task.result_id = result_id
        task.completed_at = datetime.utcnow()

        await self.session.commit()
        await self.session.refresh(task)

        logger.info(f"Task completed: {task_id}")

        return task


class PredictionResultRepository:
    """Repository for Prediction Result database operations."""

    def __init__(self, session: AsyncSession):
        """
        Initialize repository with database session.

        Args:
            session: SQLAlchemy async session
        """
        self.session = session

    async def create(
        self,
        prediction_data: str,
        valid_data: int = 0,
        invalid_data: int = 0,
    ) -> PredictionResultModel:
        """
        Create a new prediction result.

        Args:
            prediction_data: Prediction data (JSON string)
            valid_data: Count of valid data points
            invalid_data: Count of invalid data points

        Returns:
            Created prediction result
        """
        logger.info("Creating prediction result")

        result = PredictionResultModel(
            prediction_data=prediction_data,
            valid_data=valid_data,
            invalid_data=invalid_data,
        )

        self.session.add(result)
        await self.session.commit()
        await self.session.refresh(result)

        logger.info(f"Prediction result created: {result.id}")

        return result

    async def get_by_id(self, result_id: UUID) -> PredictionResultModel | None:
        """
        Get prediction result by ID.

        Args:
            result_id: Result UUID

        Returns:
            Prediction result or None if not found
        """
        logger.debug(f"Getting prediction result by ID: {result_id}")

        result = await self.session.execute(
            select(PredictionResultModel).where(
                PredictionResultModel.id == result_id
            )
        )

        prediction_result = result.scalar_one_or_none()

        if prediction_result:
            logger.debug(f"Result found: {prediction_result.id}")
        else:
            logger.debug(f"Result not found: {result_id}")

        return prediction_result
