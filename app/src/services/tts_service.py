"""
Text-to-Speech service.

Uses facebook/mms-tts-rus model via HuggingFace Inference API.
"""
import logging
from pathlib import Path

import aiofiles

from huggingface_hub import InferenceClient

from src.core.config import settings

logger = logging.getLogger(__name__)


class TTSService:
    """Text-to-Speech service using HuggingFace API."""

    def __init__(self):
        """Initialize TTS service with HF Inference client."""
        self.model = settings.HF_TTS_MODEL
        self.client = None

        if settings.HUGGINGFACE_API_TOKEN:
            self.client = InferenceClient(
                model=self.model,
                token=settings.HUGGINGFACE_API_TOKEN,
            )
            logger.info(f"TTSService initialized with model: {self.model}")
        else:
            logger.warning("TTSService: no HF token, using mock mode")

    async def synthesize(self, text: str, output_path: str) -> str:
        """
        Synthesize text to audio file.

        Args:
            text: Text to synthesize
            output_path: Path where to save audio file

        Returns:
            Path to generated audio file
        """
        logger.info(f"Synthesizing text to audio: {text[:50]}...")

        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)

        if not self.client:
            logger.warning("TTS mock mode: no HF client available")
            async with aiofiles.open(output_path, "wb") as f:
                await f.write(b"OggS")
            return output_path

        audio_bytes = self.client.text_to_speech(text=text)

        async with aiofiles.open(output_path, "wb") as f:
            await f.write(audio_bytes)

        logger.info(f"Audio saved to: {output_path} ({len(audio_bytes)} bytes)")
        return output_path

    async def synthesize_bytes(self, text: str) -> bytes:
        """
        Synthesize text to audio bytes.

        Args:
            text: Text to synthesize

        Returns:
            Audio bytes
        """
        logger.info(f"Synthesizing text to bytes: {text[:50]}...")

        if not self.client:
            logger.warning("TTS mock mode: no HF client available")
            return b"OggS"

        audio_bytes = self.client.text_to_speech(text=text)
        logger.info(f"Audio generated: {len(audio_bytes)} bytes")
        return audio_bytes
