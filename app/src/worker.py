"""
ML Worker - Processes tasks from RabbitMQ queue.

Stage 5: Asynchronous ML task processing.

Features:
- Consumes tasks from RabbitMQ
- Validates input data
- Performs ML predictions (mock for now)
- Deducts balance and creates transactions
- Saves results to database
"""
import asyncio
import json
import logging
import os
from pathlib import Path
from uuid import UUID

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from .core.config import settings
from .db.repositories.ml_model import MLModelRepository
from .db.repositories.ml_task import MLTaskRepository, PredictionResultRepository
from .db.repositories.user import UserRepository
from .db.repositories.wallet import WalletRepository
from .db.repositories.transaction import TransactionRepository
from .services.audio_service import AudioService
from .services.stt_service import STTService
from .services.tts_service import TTSService
from .queue.connection import get_rabbitmq_connection
from .queue.consumer import TaskConsumer

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Worker ID (from environment or hostname)
WORKER_ID = os.getenv("WORKER_ID", f"worker-{os.getpid()}")


class MLWorker:
    """ML Worker that processes prediction tasks."""

    def __init__(self, session_factory, rabbitmq_connection):
        """
        Initialize worker.

        Args:
            session_factory: SQLAlchemy async session factory
            rabbitmq_connection: RabbitMQ connection instance
        """
        self.session_factory = session_factory
        self.rabbitmq_connection = rabbitmq_connection
        self.consumer = None

        # Services (will be initialized per-task with session)
        self.audio_service = AudioService()
        self.stt_service = STTService()
        self.tts_service = TTSService()

        logger.info(f"MLWorker initialized: {WORKER_ID}")

    async def process_task(self, message_data: dict):
        """
        Process a single ML task.

        Args:
            message_data: Task data from queue

        Returns:
            bool: True if successful, False otherwise
        """
        task_id = message_data.get("task_id")
        logger.info(f"[{WORKER_ID}] Processing task: {task_id}")

        try:
            # Create database session
            async with self.session_factory() as session:
                # Initialize repositories
                mltask_repo = MLTaskRepository(session)
                result_repo = PredictionResultRepository(session)
                user_repo = UserRepository(session)
                wallet_repo = WalletRepository(session)
                transaction_repo = TransactionRepository(session)
                model_repo = MLModelRepository(session)

                # Get task from database
                task = await mltask_repo.get_by_id(UUID(task_id))
                if not task:
                    logger.error(f"Task not found: {task_id}")
                    return False

                # Update status to processing
                await mltask_repo.update_status(task.id, "processing")
                await session.commit()

                logger.info(
                    f"[{WORKER_ID}] Task {task_id} status: pending -> processing"
                )

                # Get user and model
                user = await user_repo.get_by_id(task.user_id)
                model = await model_repo.get_by_id(task.model_id)

                if not user or not user.wallet or not model:
                    raise ValueError("User, wallet, or model not found")

                cost = float(model.cost_per_prediction)

                # Check balance
                current_balance = float(user.wallet.balance)
                if current_balance < cost:
                    raise ValueError(
                        f"Insufficient balance: {current_balance} < {cost}"
                    )

                # Process based on input type
                if task.input_type == "text":
                    result_data = await self._process_text(
                        task.input_data, model.name
                    )
                elif task.input_type == "audio":
                    result_data = await self._process_audio(
                        task.input_data, model.name
                    )
                else:
                    raise ValueError(f"Unsupported input type: {task.input_type}")

                # Validate result
                valid_count = 1 if result_data else 0
                invalid_count = 0 if result_data else 1

                # Save prediction result
                await result_repo.create(
                    ml_task_id=task.id,
                    prediction_data=json.dumps(result_data),
                    valid_data=valid_count,
                    invalid_data=invalid_count,
                )

                logger.info(
                    f"[{WORKER_ID}] Prediction result saved for task {task_id}"
                )

                # Deduct balance
                new_balance = current_balance - cost
                await wallet_repo.update_balance(user.wallet.id, new_balance)

                # Create transaction
                await transaction_repo.create(
                    amount=cost,
                    transaction_type="debit",
                    description=f"ML prediction: {model.name} (worker: {WORKER_ID})",
                    wallet_id=user.wallet.id,
                    user_id=user.id,
                )

                logger.info(
                    f"[{WORKER_ID}] Balance deducted: ${cost} "
                    f"({current_balance} -> {new_balance})"
                )

                # Mark task as completed
                await mltask_repo.complete(task.id)
                await session.commit()

                logger.info(
                    f"[{WORKER_ID}] Task {task_id} completed successfully "
                    f"(valid: {valid_count}, invalid: {invalid_count})"
                )

                return True

        except Exception as e:
            logger.error(f"[{WORKER_ID}] Task {task_id} failed: {e}", exc_info=True)

            # Update task status to failed
            try:
                async with self.session_factory() as session:
                    mltask_repo = MLTaskRepository(session)
                    await mltask_repo.fail(task_id, str(e))
                    await session.commit()
                    logger.info(f"[{WORKER_ID}] Task {task_id} marked as failed")
            except Exception as update_error:
                logger.error(f"Failed to update task status: {update_error}")

            return False

    async def _process_text(self, input_text: str, model_name: str) -> dict:
        """
        Process text input.

        Args:
            input_text: Text input
            model_name: ML model name

        Returns:
            dict with prediction result
        """
        logger.debug(f"[{WORKER_ID}] Processing text: {input_text[:50]}...")

        # Mock: Generate response
        response_text = (
            f"Mock response to: '{input_text[:50]}...' "
            f"(Model: {model_name}, Worker: {WORKER_ID})"
        )

        # Generate audio (TTS mock)
        # Note: Audio file will be saved with task_id in the service
        logger.info(f"[{WORKER_ID}] Generating TTS audio (mock)")

        return {
            "input": input_text,
            "output": response_text,
            "model": model_name,
            "worker": WORKER_ID,
        }

    async def _process_audio(self, audio_path: str, model_name: str) -> dict:
        """
        Process audio input.

        Args:
            audio_path: Path to audio file
            model_name: ML model name

        Returns:
            dict with prediction result
        """
        logger.debug(f"[{WORKER_ID}] Processing audio: {audio_path}")

        # Validate audio file exists
        if not Path(audio_path).exists():
            raise ValueError(f"Audio file not found: {audio_path}")

        # STT: Transcribe audio (mock)
        transcription = await self.stt_service.transcribe(audio_path)
        logger.info(f"[{WORKER_ID}] Transcription: {transcription[:50]}...")

        # Mock: Generate response
        response_text = (
            f"Mock response to audio: '{transcription[:50]}...' "
            f"(Model: {model_name}, Worker: {WORKER_ID})"
        )

        # TTS: Generate audio response (mock)
        logger.info(f"[{WORKER_ID}] Generating TTS audio (mock)")

        return {
            "transcription": transcription,
            "output": response_text,
            "model": model_name,
            "worker": WORKER_ID,
        }

    async def start(self):
        """Start consuming tasks from queue."""
        logger.info(f"[{WORKER_ID}] Starting worker...")

        # Connect to RabbitMQ
        await self.rabbitmq_connection.connect()
        channel = await self.rabbitmq_connection.get_channel()

        # Create consumer
        self.consumer = TaskConsumer(channel)
        await self.consumer.setup_queue()

        logger.info(f"[{WORKER_ID}] Worker ready, waiting for tasks...")

        # Start consuming
        await self.consumer.start_consuming(self.process_task)

    async def stop(self):
        """Stop worker gracefully."""
        logger.info(f"[{WORKER_ID}] Stopping worker...")
        await self.rabbitmq_connection.close()
        logger.info(f"[{WORKER_ID}] Worker stopped")


async def main():
    """Main entry point for worker."""
    logger.info("=" * 60)
    logger.info(f"ML Worker starting: {WORKER_ID}")
    logger.info("=" * 60)

    # Create database engine and session factory
    engine = create_async_engine(settings.DATABASE_URL, echo=False)
    session_factory = async_sessionmaker(
        engine, expire_on_commit=False, class_=None
    )

    # Get RabbitMQ connection
    rabbitmq_connection = await get_rabbitmq_connection()

    # Create worker
    worker = MLWorker(session_factory, rabbitmq_connection)

    try:
        # Start worker
        await worker.start()
    except KeyboardInterrupt:
        logger.info("Received interrupt signal")
    except Exception as e:
        logger.error(f"Worker error: {e}", exc_info=True)
    finally:
        await worker.stop()
        await engine.dispose()
        logger.info("Worker shutdown complete")


if __name__ == "__main__":
    asyncio.run(main())
