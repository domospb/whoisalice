"""
Prediction service.

Coordinates ML prediction workflow:
- Text predictions
- Audio predictions
- Task creation
- Queue publishing (Stage 5: async processing)
"""
import logging
from typing import Optional
from uuid import UUID

from src.db.repositories.ml_model import MLModelRepository
from src.db.repositories.ml_task import MLTaskRepository
from src.db.repositories.user import UserRepository
from src.queue.publisher import TaskPublisher

logger = logging.getLogger(__name__)


class PredictionService:
    """Prediction orchestration service."""

    def __init__(
        self,
        session,
        audio_service,
        task_publisher: Optional[TaskPublisher] = None,
    ):
        """
        Initialize with session and services.

        Args:
            session: Database session
            audio_service: Audio file handling service
            task_publisher: RabbitMQ publisher (optional for testing)
        """
        self.session = session
        self.audio_service = audio_service
        self.task_publisher = task_publisher

        # Repositories
        self.user_repo = UserRepository(session)
        self.model_repo = MLModelRepository(session)
        self.mltask_repo = MLTaskRepository(session)

        logger.info("PredictionService initialized (Stage 5: async mode)")

    async def process_text_prediction(
        self, user_id: UUID, input_text: str, model_name: str = "GPT-4 TTS"
    ) -> dict:
        """
        Create text prediction task and publish to queue.

        Stage 5: Asynchronous processing via RabbitMQ workers.

        Args:
            user_id: User UUID
            input_text: Text input from user
            model_name: ML model to use

        Returns:
            dict with task_id, status="pending", cost

        Raises:
            ValueError: If model not found or insufficient balance
        """
        logger.info(
            f"Creating text prediction task for user {user_id}: "
            f"{input_text[:50]}..."
        )

        # Get ML model
        model = await self.model_repo.get_by_name(model_name)
        if not model:
            logger.warning(f"ML model not found: {model_name}")
            raise ValueError(f"ML model '{model_name}' not found")

        cost = float(model.cost_per_prediction)

        # Check user balance (but don't deduct yet - workers will do it)
        user = await self.user_repo.get_by_id(user_id)
        if not user or not user.wallet:
            raise ValueError("User or wallet not found")

        current_balance = float(user.wallet.balance)
        if current_balance < cost:
            logger.warning(f"Insufficient balance: {current_balance} < {cost}")
            raise ValueError(
                f"Insufficient balance. Required: ${cost}, "
                f"Available: ${current_balance}"
            )

        # Create MLTask in database (status="pending")
        task = await self.mltask_repo.create(
            user_id=user_id,
            model_id=model.id,
            input_data=input_text,
            input_type="text",
            output_type="audio",
            status="pending",
        )

        logger.info(f"MLTask created: {task.id} (status=pending, cost=${cost})")

        # Publish to RabbitMQ queue
        if self.task_publisher:
            try:
                await self.task_publisher.publish_task(
                    task_id=task.id,
                    user_id=user_id,
                    model_id=model.id,
                    input_data=input_text,
                    input_type="text",
                    output_type="audio",
                )
                logger.info(f"Task {task.id} published to queue")
            except Exception as e:
                logger.error(f"Failed to publish task: {e}")
                # Update task status to failed
                await self.mltask_repo.update_status(
                    task.id, "failed", error_message=f"Queue publish error: {e}"
                )
                raise ValueError("Failed to queue prediction task")
        else:
            logger.warning("TaskPublisher not configured, task created but not queued")

        return {
            "task_id": str(task.id),
            "status": "pending",
            "input_text": input_text,
            "cost": cost,
            "message": "Task queued for processing. Check status later.",
        }

    async def process_audio_prediction(
        self,
        user_id: UUID,
        audio_file: bytes,
        filename: str,
        model_name: str = "Whisper STT",
    ) -> dict:
        """
        Create audio prediction task and publish to queue.

        Stage 5: Asynchronous processing via RabbitMQ workers.

        Args:
            user_id: User UUID
            audio_file: Audio file bytes
            filename: Original filename
            model_name: ML model to use

        Returns:
            dict with task_id, status="pending", audio_path, cost

        Raises:
            ValueError: If model not found or insufficient balance
        """
        logger.info(f"Creating audio prediction task for user {user_id}: {filename}")

        # Get ML model
        model = await self.model_repo.get_by_name(model_name)
        if not model:
            logger.warning(f"ML model not found: {model_name}")
            raise ValueError(f"ML model '{model_name}' not found")

        cost = float(model.cost_per_prediction)

        # Check user balance (but don't deduct yet - workers will do it)
        user = await self.user_repo.get_by_id(user_id)
        if not user or not user.wallet:
            raise ValueError("User or wallet not found")

        current_balance = float(user.wallet.balance)
        if current_balance < cost:
            logger.warning(f"Insufficient balance: {current_balance} < {cost}")
            raise ValueError(
                f"Insufficient balance. Required: ${cost}, "
                f"Available: ${current_balance}"
            )

        # Create MLTask in database first (to get task_id)
        task = await self.mltask_repo.create(
            user_id=user_id,
            model_id=model.id,
            input_data="",  # Will be updated with file path
            input_type="audio",
            output_type="audio",
            status="pending",
        )

        logger.info(f"MLTask created: {task.id} (status=pending, cost=${cost})")

        # Save audio file with task_id
        audio_path = await self.audio_service.save_audio_file(
            audio_file, filename, task.id
        )

        # Validate audio
        is_valid = await self.audio_service.validate_audio(audio_path)
        if not is_valid:
            logger.error(f"Invalid audio file: {audio_path}")
            await self.mltask_repo.update_status(
                task.id, "failed", error_message="Invalid audio file"
            )
            raise ValueError("Invalid audio file")

        # Update task with audio file path
        task.input_data = audio_path
        await self.session.commit()

        # Publish to RabbitMQ queue
        if self.task_publisher:
            try:
                await self.task_publisher.publish_task(
                    task_id=task.id,
                    user_id=user_id,
                    model_id=model.id,
                    input_data=audio_path,
                    input_type="audio",
                    output_type="audio",
                )
                logger.info(f"Task {task.id} published to queue")
            except Exception as e:
                logger.error(f"Failed to publish task: {e}")
                await self.mltask_repo.update_status(
                    task.id, "failed", error_message=f"Queue publish error: {e}"
                )
                raise ValueError("Failed to queue prediction task")
        else:
            logger.warning("TaskPublisher not configured, task created but not queued")

        return {
            "task_id": str(task.id),
            "status": "pending",
            "audio_path": audio_path,
            "cost": cost,
            "message": "Task queued for processing. Check status later.",
        }

    async def get_prediction_result(self, task_id: UUID, user_id: UUID) -> dict:
        """
        Get prediction result by task ID.

        Stage 5: Query MLTask from database.

        Args:
            task_id: Task UUID
            user_id: User UUID (for ownership verification)

        Returns:
            dict with task details

        Raises:
            ValueError: If task not found or access denied
        """
        logger.info(f"Getting prediction result for task: {task_id}")

        task = await self.mltask_repo.get_by_id(task_id)

        if not task:
            logger.warning(f"Task not found: {task_id}")
            raise ValueError("Task not found")

        # Verify ownership
        if task.user_id != user_id:
            logger.warning(
                f"Access denied: Task {task_id} does not belong to user {user_id}"
            )
            raise ValueError("Access denied")

        logger.info(f"Task found: {task_id}, status: {task.status}")

        # Build response
        result = {
            "task_id": str(task.id),
            "status": task.status,
            "input_type": task.input_type,
            "output_type": task.output_type,
            "created_at": task.created_at.isoformat(),
            "completed_at": task.completed_at.isoformat()
            if task.completed_at
            else None,
        }

        if task.result:
            result["prediction_data"] = task.result.prediction_data
            result["valid_count"] = task.result.valid_data
            result["invalid_count"] = task.result.invalid_data

        if task.error_message:
            result["error_message"] = task.error_message

        if task.status == "completed":
            result["audio_url"] = f"/api/v1/predict/{task.id}/audio"

        return result
