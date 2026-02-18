"""
Speech-to-Text service.

Uses OpenAI Whisper model via HuggingFace Inference API.
"""
import logging
from pathlib import Path

from huggingface_hub import InferenceClient

from src.core.config import settings

logger = logging.getLogger(__name__)


class STTService:
    """Speech-to-Text service using Whisper via HuggingFace API."""

    def __init__(self):
        """Initialize STT service with HF Inference client."""
        self.model = settings.HF_STT_MODEL
        self.client = None

        if settings.HUGGINGFACE_API_TOKEN:
            self.client = InferenceClient(
                model=self.model,
                token=settings.HUGGINGFACE_API_TOKEN,
            )
            logger.info(f"STTService initialized with model: {self.model}")
        else:
            logger.warning("STTService: no HF token, using mock mode")

    async def transcribe(self, audio_path: str) -> str:
        """
        Transcribe audio file to text.

        Args:
            audio_path: Path to audio file

        Returns:
            Transcribed text
        """
        filename = Path(audio_path).name
        logger.info(f"Transcribing audio: {filename}")

        if not self.client:
            logger.warning("STT mock mode: no HF client available")
            return f"Mock transcription of: {filename}"

        audio_file = Path(audio_path)
        if not audio_file.exists():
            raise ValueError(f"Audio file not found: {audio_path}")

        audio_bytes = audio_file.read_bytes()
        result = self.client.automatic_speech_recognition(audio=audio_bytes)

        transcription = result.text if hasattr(result, "text") else str(result)
        logger.info(f"Transcription result: {transcription[:80]}...")
        return transcription

    async def transcribe_bytes(self, audio_bytes: bytes) -> str:
        """
        Transcribe audio bytes to text.

        Args:
            audio_bytes: Raw audio data

        Returns:
            Transcribed text
        """
        logger.info(f"Transcribing audio bytes ({len(audio_bytes)} bytes)")

        if not self.client:
            logger.warning("STT mock mode: no HF client available")
            return "Mock transcription of audio bytes"

        result = self.client.automatic_speech_recognition(audio=audio_bytes)

        transcription = result.text if hasattr(result, "text") else str(result)
        logger.info(f"Transcription result: {transcription[:80]}...")
        return transcription
