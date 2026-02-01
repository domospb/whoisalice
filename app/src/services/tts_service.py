"""
Text-to-Speech service.

Mock implementation for Stage 4.
Real implementation with GPT-4/ElevenLabs API in Stage 5.
"""
import logging
from pathlib import Path
from shutil import copy2

logger = logging.getLogger(__name__)


class TTSService:
    """Text-to-Speech service (Mock)."""

    def __init__(self):
        """Initialize TTS service."""
        logger.info("TTSService initialized (MOCK MODE)")

    async def synthesize(self, text: str, output_path: str) -> str:
        """Synthesize text to audio file (MOCK)."""
        logger.info(f"Synthesizing text to audio (MOCK): {text[:50]}...")

        # TODO: Stage 5 - Replace with real TTS API call
        # For now, copy mock audio file
        mock_audio = Path("app/assets/mock_response.ogg")

        if mock_audio.exists():
            copy2(mock_audio, output_path)
            logger.info(f"Mock audio copied to: {output_path}")
        else:
            logger.warning("Mock audio file not found, creating placeholder")
            # Create empty file as placeholder
            Path(output_path).touch()

        return output_path
