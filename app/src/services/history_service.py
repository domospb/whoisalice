"""
History service.

Retrieves historical data:
- Transaction history
- Prediction history
"""
import logging
from uuid import UUID

from src.db.repositories.transaction import TransactionRepository
from src.db.repositories.ml_task import MLTaskRepository
from src.db.repositories.user import UserRepository

logger = logging.getLogger(__name__)


class HistoryService:
    """History retrieval service."""

    def __init__(self, session):
        """Initialize with database session."""
        self.session = session
        self.transaction_repo = TransactionRepository(session)
        self.mltask_repo = MLTaskRepository(session)
        self.user_repo = UserRepository(session)
        logger.info("HistoryService initialized")

    async def get_transactions(self, user_id: UUID) -> list:
        """
        Get user's transaction history.

        Args:
            user_id: User UUID

        Returns:
            list of transaction dicts

        Raises:
            ValueError: If user not found
        """
        logger.info(f"Getting transaction history for user: {user_id}")

        # Verify user exists
        user = await self.user_repo.get_by_id(user_id)
        if not user:
            logger.warning(f"User not found: {user_id}")
            raise ValueError("User not found")

        # Get transactions
        transactions = await self.transaction_repo.get_by_user(user_id)

        logger.debug(f"Found {len(transactions)} transactions")

        # Format transactions
        result = []
        for tx in transactions:
            result.append(
                {
                    "transaction_id": str(tx.id),
                    "amount": float(tx.amount),
                    "type": tx.transaction_type,
                    "description": tx.description,
                    "timestamp": tx.timestamp.isoformat(),
                }
            )

        logger.info(f"Transaction history retrieved: {len(result)} records")
        return result

    async def get_predictions(self, user_id: UUID) -> list:
        """
        Get user's prediction history.

        Stage 5: Query MLTask table.

        Args:
            user_id: User UUID

        Returns:
            list of prediction dicts
        """
        logger.info(f"Getting prediction history for user: {user_id}")

        # Verify user exists
        user = await self.user_repo.get_by_id(user_id)
        if not user:
            logger.warning(f"User not found: {user_id}")
            raise ValueError("User not found")

        # Get MLTasks
        tasks = await self.mltask_repo.get_by_user(user_id)

        logger.debug(f"Found {len(tasks)} predictions")

        # Format tasks
        result = []
        for task in tasks:
            result.append(
                {
                    "task_id": str(task.id),
                    "status": task.status,
                    "model_name": task.model.name if task.model else "Unknown",
                    "input_type": task.input_type,
                    "output_type": task.output_type,
                    "created_at": task.created_at.isoformat(),
                    "completed_at": task.completed_at.isoformat()
                    if task.completed_at
                    else None,
                    "cost": float(task.model.cost_per_prediction)
                    if task.model
                    else 0.0,
                }
            )

        logger.info(f"Prediction history retrieved: {len(result)} records")
        return result

    async def get_prediction_by_id(self, user_id: UUID, task_id: UUID) -> dict:
        """
        Get specific prediction details.

        Stage 5: Query MLTask from database.

        Args:
            user_id: User UUID
            task_id: Task UUID

        Returns:
            dict with prediction details

        Raises:
            ValueError: If prediction not found or access denied
        """
        logger.info(f"Getting prediction {task_id} for user {user_id}")

        task = await self.mltask_repo.get_by_id(task_id)

        if not task:
            logger.warning(f"Task not found: {task_id}")
            raise ValueError("Prediction not found")

        if task.user_id != user_id:
            logger.warning(
                f"Access denied: Task {task_id} does not belong to user {user_id}"
            )
            raise ValueError("Access denied")

        # Format task details
        result = {
            "task_id": str(task.id),
            "status": task.status,
            "model_name": task.model.name if task.model else "Unknown",
            "input_type": task.input_type,
            "output_type": task.output_type,
            "input_data": task.input_data,
            "created_at": task.created_at.isoformat(),
            "completed_at": task.completed_at.isoformat()
            if task.completed_at
            else None,
            "cost": float(task.model.cost_per_prediction) if task.model else 0.0,
        }

        if task.result:
            result["prediction_data"] = task.result.prediction_data
            result["valid_count"] = task.result.valid_data
            result["invalid_count"] = task.result.invalid_data

        if task.error_message:
            result["error_message"] = task.error_message

        if task.status == "completed":
            result["audio_url"] = f"/api/v1/predict/{task.id}/audio"

        logger.info(f"Prediction details retrieved for task {task_id}")
        return result
