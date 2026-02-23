"""
Speech-to-Text service.

Uses OpenAI Whisper via Hugging Face Inference Providers (router).
"""
import logging
import tempfile
from pathlib import Path

import httpx
from huggingface_hub import InferenceClient

from src.core.config import settings
from src.core.inference_errors import wrap_inference_error

logger = logging.getLogger(__name__)

# Supported models: https://huggingface.co/models?pipeline_tag=automatic-speech-recognition
STT_SUPPORTED_URL = "https://huggingface.co/models?pipeline_tag=automatic-speech-recognition"

# Extension -> Content-Type for ASR (must match server accepted types)
AUDIO_CONTENT_TYPES = {
    ".ogg": "audio/ogg",
    ".oga": "audio/ogg",
    ".flac": "audio/flac",
    ".mp3": "audio/mpeg",
    ".wav": "audio/wav",
    ".wave": "audio/wave",
    ".webm": "audio/webm",
    ".m4a": "audio/m4a",
    ".amr": "audio/amr",
}


class STTService:
    """Speech-to-Text via Hugging Face Inference Providers."""

    def __init__(self):
        """Initialize STT service with Inference Providers client."""
        self.model = settings.HF_STT_MODEL
        self.client = None
        self.token = settings.HUGGINGFACE_API_TOKEN or ""
        base = (settings.HF_INFERENCE_ENDPOINT or "").rstrip("/")
        self._asr_url = (
            f"{base}/{settings.HF_PROVIDER}/models/{self.model}"
            if base
            else ""
        )

        if settings.HUGGINGFACE_API_TOKEN:
            self.client = InferenceClient(
                token=settings.HUGGINGFACE_API_TOKEN,
                provider=settings.HF_PROVIDER,
            )
            logger.info(
                f"STTService initialized: model={self.model}, "
                f"provider={settings.HF_PROVIDER}"
            )
        else:
            logger.warning("STTService: no HF token, using mock mode")

    def _transcribe_via_http(self, audio_bytes: bytes, content_type: str) -> str:
        """Call router ASR with explicit Content-Type (workaround for client bug)."""
        if not self._asr_url or not self.token:
            raise ValueError("STT not configured")
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": content_type,
        }
        with httpx.Client(timeout=60.0) as http:
            resp = http.post(
                self._asr_url,
                content=audio_bytes,
                headers=headers,
            )
            if resp.status_code == 404:
                raise ValueError(
                    f"STT model '{self.model}' is not available (404). "
                    "Use a supported model and set HF_STT_MODEL in .env. "
                    f"See: {STT_SUPPORTED_URL}"
                ) from None
            resp.raise_for_status()
            data = resp.json()
        return data.get("text", "") or (data.get("transcription", "") or "")

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

        if not self.client and not self.token:
            logger.warning("STT mock mode: no HF client available")
            return f"Mock transcription of: {filename}"

        audio_file = Path(audio_path)
        if not audio_file.exists():
            raise ValueError(f"Audio file not found: {audio_path}")

        audio_bytes = audio_file.read_bytes()
        suffix = audio_file.suffix.lower()
        content_type = AUDIO_CONTENT_TYPES.get(suffix, "audio/ogg")

        # Use direct HTTP with Content-Type so server accepts the request
        try:
            transcription = self._transcribe_via_http(audio_bytes, content_type)
        except ValueError:
            raise
        except Exception as e:
            logger.warning(f"ASR via HTTP failed: {e}, trying InferenceClient")
            try:
                with open(audio_file, "rb") as f:
                    result = self.client.automatic_speech_recognition(
                        audio=f, model=self.model
                    )
                transcription = (
                    result.text if hasattr(result, "text") else str(result)
                )
            except Exception as e2:
                wrap_inference_error(
                    e2, service="STT", model=self.model, supported_url=STT_SUPPORTED_URL
                )
        logger.info(f"Transcription result: {transcription[:80]}...")
        return transcription

    async def transcribe_bytes(self, audio_bytes: bytes) -> str:
        """
        Transcribe audio bytes to text.

        Args:
            audio_bytes: Raw audio data (assumed OGG from e.g. Telegram voice)

        Returns:
            Transcribed text
        """
        logger.info(f"Transcribing audio bytes ({len(audio_bytes)} bytes)")

        if not self.token:
            logger.warning("STT mock mode: no HF token available")
            return "Mock transcription of audio bytes"

        # Use direct HTTP with Content-Type: audio/ogg
        try:
            transcription = self._transcribe_via_http(
                audio_bytes, "audio/ogg"
            )
        except ValueError:
            raise
        except Exception as e:
            logger.warning(f"ASR via HTTP failed: {e}, trying temp file + client")
            with tempfile.NamedTemporaryFile(
                suffix=".ogg", delete=False
            ) as tmp:
                tmp.write(audio_bytes)
                tmp_path = tmp.name
            try:
                result = self.client.automatic_speech_recognition(
                    audio=tmp_path, model=self.model
                )
                transcription = (
                    result.text
                    if hasattr(result, "text")
                    else str(result)
                )
            except Exception as e2:
                wrap_inference_error(
                    e2, service="STT", model=self.model, supported_url=STT_SUPPORTED_URL
                )
            finally:
                Path(tmp_path).unlink(missing_ok=True)
        logger.info(f"Transcription result: {transcription[:80]}...")
        return transcription
