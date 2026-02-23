"""
Application configuration and settings.

Loads environment variables and provides configuration for:
- Database connection
- JWT settings
- API settings
- File storage paths
"""
import logging
import os
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
    # CORS: in production set e.g. CORS_ORIGINS=https://app.example.com,https://admin.example.com
    CORS_ORIGINS: str = "*"

    # Storage (must match docker-compose volume mounts: audio_uploads, audio_results)
    AUDIO_UPLOAD_DIR: str = "volumes/audio_uploads"
    AUDIO_RESULTS_DIR: str = "volumes/audio_results"
    MAX_AUDIO_SIZE_MB: int = 10

    # Telegram
    TELEGRAM_BOT_TOKEN: str = ""

    # HuggingFace Inference Providers (router) - Together AI as default
    HF_INFERENCE_ENDPOINT: str = "https://router.huggingface.co"
    HF_PROVIDER: str = "together"  # Together AI; enable at https://hf.co/settings/inference-providers
    HUGGINGFACE_API_TOKEN: str = ""
    # STT: keep Whisper (works with Together/hf-inference)
    HF_STT_MODEL: str = "openai/whisper-large-v3"
    # TTS: set a model supported by your provider; see https://huggingface.co/models?pipeline_tag=text-to-speech
    HF_TTS_MODEL: str = "microsoft/speecht5_tts"
    # TTS provider: "huggingface" (default) or "yandex"
    TTS_PROVIDER: str = "huggingface"
    # Yandex SpeechKit TTS (when TTS_PROVIDER=yandex): https://cloud.yandex.com/docs/speechkit
    YANDEX_API_KEY: str = ""  # Service account API key; create in Yandex Cloud Console
    YANDEX_FOLDER_ID: str = ""  # Не передавать при API-ключе сервисного аккаунта (только для IAM token)
    YANDEX_TTS_VOICE: str = "filipp"  # e.g. filipp, alena, john (en-US); see docs for list
    YANDEX_TTS_LANG: str = "ru-RU"  # ru-RU, en-US, etc.
    # Text generation: GLM-5 via Together
    HF_CHAT_MODEL: str = "zai-org/GLM-5"
    # Image-to-text (vision): Kimi-K2.5 via Together
    HF_IMAGE_TO_TEXT_MODEL: str = "moonshotai/Kimi-K2.5"

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

# Use new HF inference endpoint (huggingface_hub reads HF_INFERENCE_ENDPOINT at import time)
os.environ["HF_INFERENCE_ENDPOINT"] = settings.HF_INFERENCE_ENDPOINT

# Ensure storage directories exist
settings.ensure_directories()

logger.info("Configuration loaded successfully")
logger.info(f"Project: {settings.PROJECT_NAME} v{settings.VERSION}")
logger.info(f"Database: {settings.POSTGRES_HOST}:{settings.POSTGRES_PORT}")
logger.info(f"Audio upload dir: {settings.AUDIO_UPLOAD_DIR}")
logger.info(f"Token expiration: {settings.ACCESS_TOKEN_EXPIRE_MINUTES} minutes")
