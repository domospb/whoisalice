"""
Text-to-Speech service.

Supports Hugging Face Inference Providers (router) or Yandex SpeechKit TTS.
"""
import logging
import struct
from pathlib import Path

import aiofiles
import httpx

from huggingface_hub import InferenceClient

from src.core.config import settings
from src.core.inference_errors import wrap_inference_error

logger = logging.getLogger(__name__)

# Supported models: https://huggingface.co/models?pipeline_tag=text-to-speech
SUPPORTED_MODELS_URL = "https://huggingface.co/models?pipeline_tag=text-to-speech"
YANDEX_TTS_URL = "https://tts.api.cloud.yandex.net/speech/v1/tts:synthesize"
YANDEX_TTS_DOCS = "https://cloud.yandex.com/docs/speechkit"


def _use_yandex_tts() -> bool:
    """Use Yandex SpeechKit TTS when provider is yandex and API key is set."""
    return (
        settings.TTS_PROVIDER == "yandex"
        and bool(settings.YANDEX_API_KEY)
    )


def _pcm_to_wav(pcm_bytes: bytes, sample_rate: int = 16000) -> bytes:
    """Wrap 16-bit mono PCM in a WAV header (44 bytes + data)."""
    n_samples = len(pcm_bytes) // 2
    data_size = n_samples * 2
    header = struct.pack(
        "<4sI4s4sIHHIIHH4sI",
        b"RIFF",
        36 + data_size,
        b"WAVE",
        b"fmt ",
        16,  # fmt chunk size
        1,   # PCM
        1,   # mono
        sample_rate,
        sample_rate * 2,
        2,   # block align
        16,  # bits per sample
        b"data",
        data_size,
    )
    return header + pcm_bytes


class TTSService:
    """Text-to-Speech via Yandex SpeechKit or Hugging Face Inference Providers."""

    def __init__(self):
        """Initialize TTS service."""
        self.model = settings.HF_TTS_MODEL
        self.client = None
        self._yandex = _use_yandex_tts()

        if self._yandex:
            logger.info(
                f"TTSService initialized: Yandex SpeechKit "
                f"(voice={settings.YANDEX_TTS_VOICE}, lang={settings.YANDEX_TTS_LANG})"
            )
        elif settings.HUGGINGFACE_API_TOKEN:
            self.client = InferenceClient(
                token=settings.HUGGINGFACE_API_TOKEN,
                provider=settings.HF_PROVIDER,
            )
            logger.info(
                f"TTSService initialized: model={self.model}, "
                f"provider={settings.HF_PROVIDER}"
            )
        else:
            logger.warning("TTSService: no HF token and no Yandex key, using mock mode")

    async def _synthesize_yandex(self, text: str) -> bytes:
        """Call Yandex SpeechKit TTS API v1. Returns WAV bytes (16-bit mono, 16 kHz)."""
        # При API-ключе сервисного аккаунта folderId в тело запроса не передавать (иначе 401).
        data = {
            "text": text,
            "lang": settings.YANDEX_TTS_LANG,
            "voice": settings.YANDEX_TTS_VOICE,
            "format": "lpcm",
            "sampleRateHertz": "16000",
        }
        async with httpx.AsyncClient(timeout=60.0) as http:
            r = await http.post(
                YANDEX_TTS_URL,
                headers={"Authorization": f"Api-Key {settings.YANDEX_API_KEY}"},
                data=data,
            )
            r.raise_for_status()
            pcm = r.content
        return _pcm_to_wav(pcm, sample_rate=16000)

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

        if self._yandex:
            try:
                audio_bytes = await self._synthesize_yandex(text)
            except httpx.HTTPStatusError as e:
                if e.response.status_code == 401:
                    raise ValueError(
                        "Yandex TTS: Unauthorized (401). Check YANDEX_API_KEY in .env: "
                        "valid API key, correct format (Authorization: Api-Key <key>), "
                        "and service account has role 'SpeechKit User'. See: " + YANDEX_TTS_DOCS
                    ) from e
                raise wrap_inference_error(
                    e,
                    service="TTS",
                    model=f"Yandex/{settings.YANDEX_TTS_VOICE}",
                    supported_url=YANDEX_TTS_DOCS,
                ) from e
            except Exception as e:
                raise wrap_inference_error(
                    e,
                    service="TTS",
                    model=f"Yandex/{settings.YANDEX_TTS_VOICE}",
                    supported_url=YANDEX_TTS_DOCS,
                ) from e
            async with aiofiles.open(output_path, "wb") as f:
                await f.write(audio_bytes)
            logger.info(f"Audio saved to: {output_path} ({len(audio_bytes)} bytes)")
            return output_path

        if not self.client:
            logger.warning("TTS mock mode: no HF client available")
            async with aiofiles.open(output_path, "wb") as f:
                await f.write(b"OggS")
            return output_path

        try:
            audio_bytes = self.client.text_to_speech(
                text=text, model=self.model
            )
        except Exception as e:
            raise wrap_inference_error(
                e,
                service="TTS",
                model=self.model,
                supported_url=SUPPORTED_MODELS_URL,
            )

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

        if self._yandex:
            try:
                audio_bytes = await self._synthesize_yandex(text)
                logger.info(f"Audio generated: {len(audio_bytes)} bytes")
                return audio_bytes
            except httpx.HTTPStatusError as e:
                if e.response.status_code == 401:
                    raise ValueError(
                        "Yandex TTS: Unauthorized (401). Check YANDEX_API_KEY in .env."
                    ) from e
                raise wrap_inference_error(
                    e,
                    service="TTS",
                    model=f"Yandex/{settings.YANDEX_TTS_VOICE}",
                    supported_url=YANDEX_TTS_DOCS,
                ) from e
            except Exception as e:
                raise wrap_inference_error(
                    e,
                    service="TTS",
                    model=f"Yandex/{settings.YANDEX_TTS_VOICE}",
                    supported_url=YANDEX_TTS_DOCS,
                ) from e

        if not self.client:
            logger.warning("TTS mock mode: no HF client available")
            return b"OggS"

        try:
            audio_bytes = self.client.text_to_speech(
                text=text, model=self.model
            )
        except Exception as e:
            raise wrap_inference_error(
                e,
                service="TTS",
                model=self.model,
                supported_url=SUPPORTED_MODELS_URL,
            )
        logger.info(f"Audio generated: {len(audio_bytes)} bytes")
        return audio_bytes
