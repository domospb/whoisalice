"""
Prediction request/response schemas.
"""
import logging
from pydantic import BaseModel, ConfigDict

logger = logging.getLogger(__name__)


class TextPredictRequest(BaseModel):
    """Text prediction request."""

    model_config = ConfigDict(protected_namespaces=())

    text: str
    model_name: str = "GPT-4 TTS"


class PredictionResponse(BaseModel):
    """Prediction response."""

    task_id: str
    status: str
    input_text: str
    result_text: str | None = None
    audio_url: str | None = None
    cost: float


class PredictionHistoryResponse(BaseModel):
    """Prediction history item."""

    model_config = ConfigDict(protected_namespaces=())

    task_id: str
    created_at: str
    status: str
    model_name: str
    cost: float
    input_type: str


logger.debug("Predict schemas loaded")
