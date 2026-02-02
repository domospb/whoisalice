"""
History service.

Retrieves historical data:
- Transaction history
- Prediction history
"""
import logging
from uuid import UUID

from ..db.repositories.transaction import TransactionRepository
from ..db.repositories.user import UserRepository

logger = logging.getLogger(__name__)


class HistoryService:
    """History retrieval service."""

    def __init__(self, session):
        """Initialize with database session."""
        self.session = session
        self.transaction_repo = TransactionRepository(session)
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

        NOTE: Mock implementation for Stage 4.
        Real implementation will query MLTask table in Stage 5.

        Args:
            user_id: User UUID

        Returns:
            list of prediction dicts
        """
        logger.info(f"Getting prediction history for user: {user_id}")

        # TODO: Stage 5 - Implement real prediction history
        # predictions = await self.mltask_repo.get_by_user(user_id)

        logger.warning("MOCK: Prediction history not available in Stage 4")

        # Return empty list for now
        return []

    async def get_prediction_by_id(self, user_id: UUID, task_id: UUID) -> dict:
        """
        Get specific prediction details.

        NOTE: Mock implementation for Stage 4.
        Real implementation will query MLTask table in Stage 5.

        Args:
            user_id: User UUID
            task_id: Task UUID

        Returns:
            dict with prediction details

        Raises:
            ValueError: If prediction not found
        """
        logger.info(f"Getting prediction {task_id} for user {user_id}")

        # TODO: Stage 5 - Implement real prediction retrieval
        # task = await self.mltask_repo.get_by_id(task_id)
        # if not task or task.user_id != user_id:
        #     raise ValueError("Prediction not found")

        logger.warning("MOCK: Prediction retrieval not available in Stage 4")

        raise ValueError("Prediction history not available in Stage 4")
