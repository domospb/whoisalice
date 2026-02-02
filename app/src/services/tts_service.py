"""
Text-to-Speech service.

Mock implementation for Stage 4.
Real implementation with GPT-4/ElevenLabs API in Stage 5.
"""
import logging
from pathlib import Path

import aiofiles

logger = logging.getLogger(__name__)


class TTSService:
    """Text-to-Speech service (Mock)."""

    def __init__(self):
        """Initialize TTS service."""
        logger.info("TTSService initialized (MOCK MODE)")

    async def synthesize(self, text: str, output_path: str) -> str:
        """
        Synthesize text to audio file (MOCK).

        Args:
            text: Text to synthesize
            output_path: Path where to save audio file

        Returns:
            Path to generated audio file
        """
        logger.info(f"Synthesizing text to audio (MOCK): {text[:50]}...")

        # TODO: Stage 5 - Replace with real TTS API call
        # For now, create a small placeholder OGG file

        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)

        # Check if mock audio exists
        mock_audio = Path("app/assets/mock_response.ogg")

        if mock_audio.exists():
            logger.debug(f"Copying mock audio from: {mock_audio}")
            async with aiofiles.open(mock_audio, "rb") as f_in:
                data = await f_in.read()
                async with aiofiles.open(output_path, "wb") as f_out:
                    await f_out.write(data)
            logger.info(f"Mock audio copied to: {output_path}")
        else:
            logger.warning("Mock audio file not found, creating minimal placeholder")
            # Create minimal OGG file header (not a valid audio, just placeholder)
            async with aiofiles.open(output_path, "wb") as f:
                await f.write(b"OggS")  # OGG file signature

        return output_path
