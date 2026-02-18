"""
Chat service.

Uses Qwen2.5-7B-Instruct via HuggingFace Inference API
for Russian-language text generation.
"""
import logging

from huggingface_hub import InferenceClient

from src.core.config import settings

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = (
    "Тебя зовут Алиса. Ты умный и дружелюбный русскоязычный ассистент. "
    "Отвечай на русском языке, кратко и по делу."
)


class ChatService:
    """Chat service using HuggingFace Inference API."""

    def __init__(self):
        """Initialize chat service with HF Inference client."""
        self.model = settings.HF_CHAT_MODEL
        self.client = None

        if settings.HUGGINGFACE_API_TOKEN:
            self.client = InferenceClient(
                model=self.model,
                token=settings.HUGGINGFACE_API_TOKEN,
            )
            logger.info(f"ChatService initialized with model: {self.model}")
        else:
            logger.warning("ChatService: no HF token, using mock mode")

    async def generate_response(self, user_message: str) -> str:
        """
        Generate a response to user message.

        Args:
            user_message: Text input from user

        Returns:
            Generated response text
        """
        logger.info(f"Generating response for: {user_message[:50]}...")

        if not self.client:
            logger.warning("Chat mock mode: no HF client available")
            return f"Mock response to: {user_message[:50]}"

        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_message},
        ]

        response = self.client.chat_completion(
            messages=messages,
            max_tokens=1024,
            temperature=0.7,
            top_p=0.9,
        )

        result = response.choices[0].message.content
        logger.info(f"Chat response: {result[:80]}...")
        return result
