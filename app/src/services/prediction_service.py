"""
Prediction service.

Coordinates ML prediction workflow:
- Text predictions
- Audio predictions
- Balance deduction
- Task creation and updates
"""
import logging
from pathlib import Path
from uuid import UUID, uuid4

from ..db.repositories.ml_model import MLModelRepository
from ..db.repositories.user import UserRepository
from ..db.repositories.wallet import WalletRepository
from ..db.repositories.transaction import TransactionRepository
from ..core.config import settings

logger = logging.getLogger(__name__)


class PredictionService:
    """Prediction orchestration service."""

    def __init__(self, session, audio_service, stt_service, tts_service):
        """Initialize with session and ML services."""
        self.session = session
        self.audio_service = audio_service
        self.stt_service = stt_service
        self.tts_service = tts_service

        # Repositories
        self.user_repo = UserRepository(session)
        self.model_repo = MLModelRepository(session)
        self.wallet_repo = WalletRepository(session)
        self.transaction_repo = TransactionRepository(session)

        logger.info("PredictionService initialized")

    async def process_text_prediction(
        self, user_id: UUID, input_text: str, model_name: str = "GPT-4 TTS"
    ) -> dict:
        """
        Process text-based prediction.

        Args:
            user_id: User UUID
            input_text: Text input from user
            model_name: ML model to use

        Returns:
            dict with task_id, status, result_text, audio_url, cost

        Raises:
            ValueError: If model not found or insufficient balance
        """
        logger.info(
            f"Processing text prediction for user {user_id}: {input_text[:50]}..."
        )

        # Get ML model
        model = await self.model_repo.get_by_name(model_name)
        if not model:
            logger.warning(f"ML model not found: {model_name}")
            raise ValueError(f"ML model '{model_name}' not found")

        cost = float(model.cost_per_prediction)

        # Check user balance
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

        # Create task ID
        task_id = uuid4()

        # Mock: Generate response text
        response_text = (
            f"Mock response to: '{input_text[:30]}...' "
            f"(Model: {model_name}, Task: {task_id})"
        )

        logger.debug(f"Mock response generated: {response_text[:50]}...")

        # Generate audio response
        audio_filename = f"{task_id}_result.ogg"
        audio_path = Path(settings.AUDIO_RESULTS_DIR) / audio_filename
        await self.tts_service.synthesize(response_text, str(audio_path))

        # Deduct credits
        new_balance = current_balance - cost
        await self.wallet_repo.update_balance(user.wallet.id, new_balance)

        # Create transaction (for audit trail)
        await self.transaction_repo.create(
            amount=cost,
            transaction_type="debit",
            description=f"ML prediction: {model_name}",
            wallet_id=user.wallet.id,
            user_id=user_id,
        )

        logger.info(
            f"Text prediction processed: Task {task_id} | "
            f"Cost: ${cost} | Balance: {current_balance} -> {new_balance}"
        )

        # TODO: Stage 5 - Create MLTask in database and update status

        return {
            "task_id": str(task_id),
            "status": "completed",
            "input_text": input_text,
            "result_text": response_text,
            "audio_url": f"/api/v1/predict/{task_id}/audio",
            "cost": cost,
        }

    async def process_audio_prediction(
        self,
        user_id: UUID,
        audio_file: bytes,
        filename: str,
        model_name: str = "Whisper STT",
    ) -> dict:
        """
        Process audio-based prediction.

        Args:
            user_id: User UUID
            audio_file: Audio file bytes
            filename: Original filename
            model_name: ML model to use

        Returns:
            dict with task_id, status, transcription, result_text, audio_url, cost

        Raises:
            ValueError: If model not found or insufficient balance
        """
        logger.info(f"Processing audio prediction for user {user_id}: {filename}")

        # Get ML model
        model = await self.model_repo.get_by_name(model_name)
        if not model:
            logger.warning(f"ML model not found: {model_name}")
            raise ValueError(f"ML model '{model_name}' not found")

        cost = float(model.cost_per_prediction)

        # Check user balance
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

        # Create task ID
        task_id = uuid4()

        # Save audio file
        audio_path = await self.audio_service.save_audio_file(
            audio_file, filename, task_id
        )

        # Validate audio
        is_valid = await self.audio_service.validate_audio(audio_path)
        if not is_valid:
            logger.error(f"Invalid audio file: {audio_path}")
            raise ValueError("Invalid audio file")

        # STT: Transcribe audio
        transcription = await self.stt_service.transcribe(audio_path)

        logger.debug(f"Transcription: {transcription}")

        # Mock: Process transcription and generate response
        response_text = (
            f"Mock response to audio transcription: '{transcription[:30]}...' "
            f"(Model: {model_name}, Task: {task_id})"
        )

        # TTS: Convert response to audio
        result_audio_filename = f"{task_id}_result.ogg"
        result_audio_path = Path(settings.AUDIO_RESULTS_DIR) / result_audio_filename
        await self.tts_service.synthesize(response_text, str(result_audio_path))

        # Deduct credits
        new_balance = current_balance - cost
        await self.wallet_repo.update_balance(user.wallet.id, new_balance)

        # Create transaction (for audit trail)
        await self.transaction_repo.create(
            amount=cost,
            transaction_type="debit",
            description=f"ML prediction: {model_name} (audio)",
            wallet_id=user.wallet.id,
            user_id=user_id,
        )

        logger.info(
            f"Audio prediction processed: Task {task_id} | "
            f"Cost: ${cost} | Balance: {current_balance} -> {new_balance}"
        )

        # TODO: Stage 5 - Create MLTask in database and update status

        return {
            "task_id": str(task_id),
            "status": "completed",
            "transcription": transcription,
            "result_text": response_text,
            "audio_url": f"/api/v1/predict/{task_id}/audio",
            "cost": cost,
        }

    async def get_prediction_result(self, task_id: UUID) -> dict:
        """
        Get prediction result by task ID.

        NOTE: Mock implementation for Stage 4.
        Real implementation will query MLTask from database in Stage 5.

        Args:
            task_id: Task UUID

        Returns:
            dict with task details

        Raises:
            ValueError: If task not found
        """
        logger.info(f"Getting prediction result for task: {task_id}")

        # TODO: Stage 5 - Implement real task retrieval from database
        # task = await self.mltask_repo.get_by_id(task_id)

        logger.warning("MOCK: Prediction result retrieval not fully implemented")
        raise ValueError(
            "Prediction history not available in Stage 4. "
            "Use the prediction response directly."
        )
