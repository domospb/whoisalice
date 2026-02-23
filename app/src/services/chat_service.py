"""
Chat service.

Uses conversational LLM via Hugging Face router (OpenAI-compatible /v1/chat/completions).
"""
import logging
import re

import httpx
from huggingface_hub import InferenceClient

from src.core.config import settings

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = (
    "Тебя зовут Алиса. Ты умный и дружелюбный русскоязычный ассистент. "
    "Отвечай на русском языке, кратко и по делу."
)


def strip_think_block(text: str) -> str:
    """Remove <think>...</think> blocks from model output so they are not sent to users or TTS."""
    if not text or not text.strip():
        return text
    return re.sub(r"<think>.*?</think>", "", text, flags=re.DOTALL | re.IGNORECASE).strip()

# Supported models: https://huggingface.co/models?pipeline_tag=conversational
CHAT_SUPPORTED_URL = "https://huggingface.co/models?pipeline_tag=conversational"
# Vision: https://huggingface.co/models?pipeline_tag=image-text-to-text
VISION_SUPPORTED_URL = "https://huggingface.co/models?pipeline_tag=image-text-to-text"


class ChatService:
    """Chat and vision (image-to-text) via Hugging Face Inference Providers (router)."""

    def __init__(self):
        """Initialize chat service."""
        self.model = settings.HF_CHAT_MODEL
        self.vision_model = settings.HF_IMAGE_TO_TEXT_MODEL
        self.client = None
        self.token = settings.HUGGINGFACE_API_TOKEN or ""
        base = (settings.HF_INFERENCE_ENDPOINT or "").rstrip("/")
        self._chat_url = f"{base}/v1/chat/completions" if base else ""

        if settings.HUGGINGFACE_API_TOKEN:
            self.client = InferenceClient(
                token=settings.HUGGINGFACE_API_TOKEN,
                provider=settings.HF_PROVIDER,
            )
            logger.info(
                f"ChatService initialized: model={self.model}, "
                f"vision={self.vision_model}, provider={settings.HF_PROVIDER}"
            )
        else:
            logger.warning("ChatService: no HF token, using mock mode")

    def _generate_via_http(
        self, messages: list, max_tokens: int = 1024, model_id_override: str | None = None
    ) -> str:
        """Call router OpenAI-compatible /v1/chat/completions (only path that works; no fallback)."""
        if not self._chat_url or not self.token:
            raise ValueError("Chat not configured")
        model_id = model_id_override if model_id_override is not None else self.model
        # Pin provider suffix (e.g. :together) so router routes to correct provider.
        if not model_id_override and ":" not in model_id and settings.HF_PROVIDER:
            model_id = f"{model_id}:{settings.HF_PROVIDER}"
        # Minimal payload per HF router docs; extra params can cause 400
        payload = {
            "model": model_id,
            "messages": messages,
            "max_tokens": max_tokens,
            "stream": False,
        }
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json",
        }
        with httpx.Client(timeout=120.0) as http:
            resp = http.post(self._chat_url, json=payload, headers=headers)
            if not resp.is_success:
                err_body = (resp.text or "").strip()[:800]
                logger.warning("Chat HTTP %s: %s", resp.status_code, err_body)
                if resp.status_code == 400 and err_body:
                    if "model_not_supported" in err_body and "not supported by any provider you have enabled" in err_body:
                        raise ValueError(
                            "Chat model is not available: no Inference Provider enabled. "
                            "Enable at least one provider (e.g. Groq, Together) at "
                            "https://hf.co/settings/inference-providers"
                        )
                    if "model_not_supported" in err_body or "404" in err_body:
                        raise ValueError(
                            f"Chat model '{self.model}' is not available on the current inference provider. "
                            "Models change over time; use a supported model and set HF_CHAT_MODEL in .env. "
                            f"See: {CHAT_SUPPORTED_URL}"
                        ) from None
                    raise ValueError(f"Chat API 400 Bad Request: {err_body}")
                if resp.status_code == 404:
                    raise ValueError(
                        f"Chat model '{model_id}' is not available (404). "
                        "Use a supported model and set HF_CHAT_MODEL in .env. "
                        f"See: {CHAT_SUPPORTED_URL}"
                    ) from None
                resp.raise_for_status()
            data = resp.json()
        choices = data.get("choices") or []
        if not choices:
            raise ValueError("Empty choices in chat response")
        message = choices[0].get("message") or {}
        return (message.get("content") or "").strip()

    def _generate_via_http_with_fallback(self, messages: list, max_tokens: int = 1024) -> str:
        """Call /v1/chat/completions; if 404 with provider suffix, retry without suffix."""
        try:
            return self._generate_via_http(messages, max_tokens=max_tokens)
        except httpx.HTTPStatusError as e:
            if e.response.status_code != 404:
                raise
            # Retry without provider suffix (router may not support "model:hf-inference")
            if settings.HF_PROVIDER and ":" not in self.model:
                logger.warning(
                    "Chat 404, retrying without provider suffix",
                )
                return self._generate_via_http(
                    messages, max_tokens=max_tokens, model_id_override=self.model
                )
            raise

    async def generate_response(self, user_message: str) -> str:
        """
        Generate a response to user message.

        Args:
            user_message: Text input from user

        Returns:
            Generated response text
        """
        logger.info(f"Generating response for: {user_message[:50]}...")

        if not self.token:
            logger.warning("Chat mock mode: no HF token available")
            return f"Mock response to: {user_message[:50]}"

        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_message},
        ]

        # Use only router /v1/chat/completions (InferenceClient provider path returns 404)
        result = self._generate_via_http_with_fallback(messages, max_tokens=1024)
        result = strip_think_block(result)
        logger.info(f"Chat response: {result[:80]}...")
        return result

    def _build_model_id(self, model: str) -> str:
        """Append provider suffix if not present."""
        if not model or ":" in model or not settings.HF_PROVIDER:
            return model or ""
        return f"{model}:{settings.HF_PROVIDER}"

    async def generate_response_for_image(
        self, image_url: str, user_message: str = "Опиши это изображение."
    ) -> str:
        """
        Image-to-text (vision) using Kimi-K2.5 or HF_IMAGE_TO_TEXT_MODEL.

        Args:
            image_url: URL or data URL (e.g. data:image/png;base64,...) of the image
            user_message: Optional text prompt (default: describe the image)

        Returns:
            Model response text
        """
        if not self._chat_url or not self.token:
            raise ValueError("Chat/vision not configured")

        # OpenAI-compatible vision: user content as list of parts
        content = [
            {"type": "text", "text": user_message or "Опиши это изображение."},
            {"type": "image_url", "image_url": {"url": image_url}},
        ]
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": content},
        ]
        model_id = self._build_model_id(self.vision_model)
        payload = {
            "model": model_id,
            "messages": messages,
            "max_tokens": 1024,
            "stream": False,
        }
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json",
        }
        with httpx.Client(timeout=120.0) as http:
            resp = http.post(self._chat_url, json=payload, headers=headers)
            if not resp.is_success:
                err_body = (resp.text or "").strip()[:800]
                logger.warning("Vision HTTP %s: %s", resp.status_code, err_body)
                if resp.status_code in (400, 404):
                    raise ValueError(
                        f"Vision model '{self.vision_model}' failed or not available. "
                        f"Enable Together at https://hf.co/settings/inference-providers. "
                        f"See: {VISION_SUPPORTED_URL}"
                    ) from None
                resp.raise_for_status()
            data = resp.json()
        choices = data.get("choices") or []
        if not choices:
            raise ValueError("Empty choices in vision response")
        message = choices[0].get("message") or {}
        result = strip_think_block((message.get("content") or "").strip())
        logger.info(f"Vision response: {result[:80]}...")
        return result
