"""
Speech-to-Text service.

Mock implementation for Stage 4.
Real implementation with Whisper/Claude API in Stage 5.
"""
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


class STTService:
    """Speech-to-Text service (Mock)."""

    def __init__(self):
        """Initialize STT service."""
        logger.info("STTService initialized (MOCK MODE)")

    async def transcribe(self, audio_path: str) -> str:
        """Transcribe audio file to text (MOCK)."""
        filename = Path(audio_path).name
        logger.info(f"Transcribing audio (MOCK): {filename}")

        # TODO: Stage 5 - Replace with real Whisper API call
        mock_transcription = f"Mock transcription of audio file: {filename}"

        logger.info(f"Transcription result (MOCK): {mock_transcription}")
        return mock_transcription
