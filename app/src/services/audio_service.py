"""
Audio file handling service.

Handles:
- Save audio files
- Convert audio formats (MP3 → OGG)
- Validate audio files
- Manage file storage
"""
import logging
from pathlib import Path
from uuid import UUID

import aiofiles

from src.core.config import settings

logger = logging.getLogger(__name__)


class AudioService:
    """Audio file handling service."""

    def __init__(self):
        """Initialize audio service."""
        self.upload_dir = Path(settings.AUDIO_UPLOAD_DIR)
        self.results_dir = Path(settings.AUDIO_RESULTS_DIR)
        self.max_size_bytes = settings.MAX_AUDIO_SIZE_MB * 1024 * 1024
        logger.info("AudioService initialized")

    async def save_audio_file(
        self, file_data: bytes, filename: str, task_id: UUID
    ) -> str:
        """
        Save uploaded audio file.

        Args:
            file_data: Audio file bytes
            filename: Original filename
            task_id: Task UUID for unique naming

        Returns:
            Full path to saved file

        Raises:
            ValueError: If file is too large
        """
        logger.info(f"Saving audio file for task {task_id}: {filename}")

        # Check file size
        file_size = len(file_data)
        if file_size > self.max_size_bytes:
            logger.warning(
                f"File too large: {file_size} bytes " f"(max: {self.max_size_bytes})"
            )
            raise ValueError(
                f"File too large. Max size: {settings.MAX_AUDIO_SIZE_MB}MB"
            )

        # Create unique filename
        file_ext = Path(filename).suffix or ".ogg"
        unique_filename = f"{task_id}{file_ext}"
        file_path = self.upload_dir / unique_filename

        # Save file
        logger.debug(f"Writing file to: {file_path}")
        async with aiofiles.open(file_path, "wb") as f:
            await f.write(file_data)

        logger.info(f"Audio file saved: {file_path} ({file_size} bytes)")

        return str(file_path)

    async def convert_to_ogg(self, input_path: str) -> str:
        """
        Convert audio file to OGG format using ffmpeg.

        NOTE: Mock implementation for Stage 4.
        Real ffmpeg conversion will be added in Stage 5.

        Args:
            input_path: Path to input audio file

        Returns:
            Path to converted OGG file
        """
        logger.info(f"Converting audio to OGG: {input_path}")

        input_file = Path(input_path)

        # Check if already OGG
        if input_file.suffix.lower() in [".ogg", ".oga"]:
            logger.debug("File is already OGG format")
            return input_path

        # Mock conversion - just copy file
        output_path = input_file.with_suffix(".ogg")
        logger.warning(f"MOCK: Copying file instead of converting: {output_path}")

        # TODO: Stage 5 - Implement real ffmpeg conversion
        # import asyncffmpeg
        # await asyncffmpeg.convert(input_path, output_path, ...)

        async with aiofiles.open(input_path, "rb") as f_in:
            data = await f_in.read()
            async with aiofiles.open(output_path, "wb") as f_out:
                await f_out.write(data)

        logger.info(f"Audio converted (MOCK): {output_path}")
        return str(output_path)

    async def validate_audio(self, file_path: str) -> bool:
        """
        Validate audio file format and size.

        Args:
            file_path: Path to audio file

        Returns:
            True if valid, False otherwise
        """
        logger.debug(f"Validating audio file: {file_path}")

        file = Path(file_path)

        # Check file exists
        if not file.exists():
            logger.warning(f"File does not exist: {file_path}")
            return False

        # Check file size
        file_size = file.stat().st_size
        if file_size > self.max_size_bytes:
            logger.warning(f"File too large: {file_size} bytes")
            return False

        if file_size == 0:
            logger.warning("File is empty")
            return False

        # Check audio format (basic check by extension)
        valid_extensions = [".ogg", ".mp3", ".wav", ".m4a", ".oga"]
        if file.suffix.lower() not in valid_extensions:
            logger.warning(f"Invalid audio format: {file.suffix}")
            return False

        logger.debug(f"Audio file valid: {file_size} bytes")
        return True

    async def get_audio_duration(self, file_path: str) -> float:
        """
        Get audio file duration in seconds.

        Mock implementation for Stage 4.

        Args:
            file_path: Path to audio file

        Returns:
            Duration in seconds (mock value)
        """
        logger.debug(f"Getting audio duration: {file_path}")

        # TODO: Stage 5 - Implement real duration calculation
        # from pydub import AudioSegment
        # audio = AudioSegment.from_file(file_path)
        # return len(audio) / 1000.0

        # Mock: return 5 seconds
        logger.debug("MOCK: Returning 5.0 seconds duration")
        return 5.0
