"""
Application configuration and settings.

Loads environment variables and provides configuration for:
- Database connection
- JWT settings
- API settings
- File storage paths
"""
import logging
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

    # Storage
    AUDIO_UPLOAD_DIR: str = "volumes/audio"
    AUDIO_RESULTS_DIR: str = "volumes/results"
    MAX_AUDIO_SIZE_MB: int = 10

    # Telegram
    TELEGRAM_BOT_TOKEN: str = ""

    class Config:
        """Pydantic config."""

        env_file = ".env"


# Global settings instance
settings = Settings()

logger.info("Configuration loaded successfully")
logger.info(f"Project: {settings.PROJECT_NAME}")
logger.info(f"Database: {settings.POSTGRES_HOST}:{settings.POSTGRES_PORT}")
logger.info(f"Audio upload dir: {settings.AUDIO_UPLOAD_DIR}")
