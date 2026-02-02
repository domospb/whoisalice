"""
Prediction REST endpoints.

POST /predict/text - Text-based prediction
POST /predict/audio - Audio file prediction
GET /predict/{task_id} - Get prediction result
GET /predict/{task_id}/audio - Download result audio
"""
import logging
from pathlib import Path
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession

from ...core.config import settings
from ...core.security import get_current_user_id
from ...db.session import get_db
from ...services.audio_service import AudioService
from ...services.stt_service import STTService
from ...services.tts_service import TTSService
from ...services.prediction_service import PredictionService
from ..schemas.predict import TextPredictRequest, PredictionResponse

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/predict", tags=["Predictions"])

logger.info("Predict router initialized")


@router.post("/text", response_model=PredictionResponse)
async def predict_text(
    request: TextPredictRequest,
    user_id: str = Depends(get_current_user_id),
    session: AsyncSession = Depends(get_db),
):
    """
    Process text prediction.

    Requires authentication.
    Deducts credits from user balance.
    """
    logger.info(f"POST /predict/text called for user {user_id}")

    # Initialize services
    audio_service = AudioService()
    stt_service = STTService()
    tts_service = TTSService()
    prediction_service = PredictionService(
        session, audio_service, stt_service, tts_service
    )

    try:
        result = await prediction_service.process_text_prediction(
            user_id=UUID(user_id),
            input_text=request.text,
            model_name=request.model_name,
        )

        logger.info(f"Text prediction completed: {result['task_id']}")

        return PredictionResponse(**result)

    except ValueError as e:
        logger.warning(f"Text prediction failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except Exception as e:
        logger.error(f"Text prediction error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Prediction failed",
        )


@router.post("/audio", response_model=PredictionResponse)
async def predict_audio(
    audio: UploadFile = File(...),
    model_name: str = "Whisper STT",
    user_id: str = Depends(get_current_user_id),
    session: AsyncSession = Depends(get_db),
):
    """
    Process audio prediction.

    Requires authentication.
    Accepts audio files (OGG, MP3, WAV, M4A).
    Deducts credits from user balance.
    """
    logger.info(
        f"POST /predict/audio called for user {user_id}: {audio.filename}"
    )

    # Read audio file
    audio_data = await audio.read()

    # Initialize services
    audio_service = AudioService()
    stt_service = STTService()
    tts_service = TTSService()
    prediction_service = PredictionService(
        session, audio_service, stt_service, tts_service
    )

    try:
        result = await prediction_service.process_audio_prediction(
            user_id=UUID(user_id),
            audio_file=audio_data,
            filename=audio.filename,
            model_name=model_name,
        )

        logger.info(f"Audio prediction completed: {result['task_id']}")

        return PredictionResponse(
            task_id=result["task_id"],
            status=result["status"],
            input_text=result.get("transcription", ""),
            result_text=result.get("result_text"),
            audio_url=result.get("audio_url"),
            cost=result["cost"],
        )

    except ValueError as e:
        logger.warning(f"Audio prediction failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except Exception as e:
        logger.error(f"Audio prediction error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Prediction failed",
        )


@router.get("/{task_id}")
async def get_prediction(
    task_id: str,
    user_id: str = Depends(get_current_user_id),
    session: AsyncSession = Depends(get_db),
):
    """
    Get prediction result.

    Requires authentication.
    NOTE: Not fully implemented in Stage 4.
    """
    logger.info(f"GET /predict/{task_id} called for user {user_id}")

    # TODO: Stage 5 - Implement task retrieval from database

    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Prediction history not available in Stage 4",
    )


@router.get("/{task_id}/audio")
async def get_prediction_audio(
    task_id: str,
    user_id: str = Depends(get_current_user_id),
):
    """
    Download result audio file.

    Requires authentication.
    """
    logger.info(f"GET /predict/{task_id}/audio called for user {user_id}")

    # Build audio file path
    audio_filename = f"{task_id}_result.ogg"
    audio_path = Path(settings.AUDIO_RESULTS_DIR) / audio_filename

    if not audio_path.exists():
        logger.warning(f"Audio file not found: {audio_path}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Audio file not found",
        )

    logger.info(f"Serving audio file: {audio_path}")

    return FileResponse(
        path=str(audio_path),
        media_type="audio/ogg",
        filename=audio_filename,
    )
