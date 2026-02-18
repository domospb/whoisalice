"""
Application configuration and settings.

Loads environment variables and provides configuration for:
- Database connection
- JWT settings
- API settings
- File storage paths
"""
import logging
from pathlib import Path

from pydantic_settings import BaseSettings

logger = logging.getLogger(__name__)


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Database
    POSTGRES_USER: str = "whoisalice"
    POSTGRES_PASSWORD: str = "changeme_strong_password"
    POSTGRES_DB: str = "whoisalice"
    POSTGRES_HOST: str = "database"
    POSTGRES_PORT: int = 5432

    # JWT
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # API
    API_V1_PREFIX: str = "/api/v1"
    PROJECT_NAME: str = "WhoIsAlice"
    VERSION: str = "0.1.0"
    DESCRIPTION: str = "AI Voice Assistant API"

    # Storage
    AUDIO_UPLOAD_DIR: str = "volumes/audio"
    AUDIO_RESULTS_DIR: str = "volumes/results"
    MAX_AUDIO_SIZE_MB: int = 10

    # Telegram
    TELEGRAM_BOT_TOKEN: str = ""

    # HuggingFace
    HUGGINGFACE_API_TOKEN: str = ""
    HF_STT_MODEL: str = "openai/whisper-medium"
    HF_TTS_MODEL: str = "facebook/mms-tts-rus"
    HF_CHAT_MODEL: str = "Qwen/Qwen2.5-7B-Instruct"

    class Config:
        """Pydantic config."""

        env_file = ".env"
        extra = "ignore"  # Ignore extra fields from .env

    def ensure_directories(self):
        """Create storage directories if they don't exist."""
        Path(self.AUDIO_UPLOAD_DIR).mkdir(parents=True, exist_ok=True)
        Path(self.AUDIO_RESULTS_DIR).mkdir(parents=True, exist_ok=True)


# Global settings instance
settings = Settings()

# Ensure storage directories exist
settings.ensure_directories()

logger.info("Configuration loaded successfully")
logger.info(f"Project: {settings.PROJECT_NAME} v{settings.VERSION}")
logger.info(f"Database: {settings.POSTGRES_HOST}:{settings.POSTGRES_PORT}")
logger.info(f"Audio upload dir: {settings.AUDIO_UPLOAD_DIR}")
logger.info(f"Token expiration: {settings.ACCESS_TOKEN_EXPIRE_MINUTES} minutes")