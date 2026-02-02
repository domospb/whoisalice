"""
Prediction REST endpoints.

Stage 5: Integrated with RabbitMQ for asynchronous processing.

POST /predict/text - Text-based prediction (queued)
POST /predict/audio - Audio file prediction (queued)
GET /predict/{task_id} - Get prediction result
GET /predict/{task_id}/audio - Download result audio
"""
import logging
from pathlib import Path
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Request, status
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession

from ...core.config import settings
from ...core.security import get_current_user_id
from ...db.session import get_db
from ...services.audio_service import AudioService
from ...services.prediction_service import PredictionService
from ..schemas.predict import TextPredictRequest, PredictionResponse

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/predict", tags=["Predictions"])

logger.info("Predict router initialized")


@router.post("/text", response_model=PredictionResponse)
async def predict_text(
    predict_request: TextPredictRequest,
    req: Request,
    user_id: str = Depends(get_current_user_id),
    session: AsyncSession = Depends(get_db),
):
    """
    Queue text prediction for asynchronous processing.

    Stage 5: Creates MLTask and publishes to RabbitMQ.
    Returns task_id immediately with status="pending".

    Requires authentication.
    """
    logger.info(f"POST /predict/text called for user {user_id}")

    # Get task publisher from app state
    task_publisher = getattr(req.app.state, "task_publisher", None)

    # Initialize services
    audio_service = AudioService()
    prediction_service = PredictionService(
        session, audio_service, task_publisher=task_publisher
    )

    try:
        result = await prediction_service.process_text_prediction(
            user_id=UUID(user_id),
            input_text=predict_request.text,
            model_name=predict_request.model_name,
        )

        logger.info(
            f"Text prediction task created: {result['task_id']} (status=pending)"
        )

        return PredictionResponse(
            task_id=result["task_id"],
            status=result["status"],
            input_text=result["input_text"],
            result_text=result.get("message"),
            cost=result["cost"],
        )

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
    req: Request = None,
    user_id: str = Depends(get_current_user_id),
    session: AsyncSession = Depends(get_db),
):
    """
    Queue audio prediction for asynchronous processing.

    Stage 5: Creates MLTask and publishes to RabbitMQ.
    Returns task_id immediately with status="pending".

    Requires authentication.
    Accepts audio files (OGG, MP3, WAV, M4A).
    """
    logger.info(f"POST /predict/audio called for user {user_id}: {audio.filename}")

    # Read audio file
    audio_data = await audio.read()

    # Get task publisher from app state
    task_publisher = getattr(req.app.state, "task_publisher", None)

    # Initialize services
    audio_service = AudioService()
    prediction_service = PredictionService(
        session, audio_service, task_publisher=task_publisher
    )

    try:
        result = await prediction_service.process_audio_prediction(
            user_id=UUID(user_id),
            audio_file=audio_data,
            filename=audio.filename,
            model_name=model_name,
        )

        logger.info(
            f"Audio prediction task created: {result['task_id']} (status=pending)"
        )

        return PredictionResponse(
            task_id=result["task_id"],
            status=result["status"],
            input_text="[Audio file uploaded]",
            result_text=result.get("message"),
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
    Get prediction result by task ID.

    Stage 5: Retrieves MLTask from database with status.

    Requires authentication.
    Returns task status (pending, processing, completed, failed).
    """
    logger.info(f"GET /predict/{task_id} called for user {user_id}")

    # Initialize services
    audio_service = AudioService()
    prediction_service = PredictionService(session, audio_service)

    try:
        result = await prediction_service.get_prediction_result(
            task_id=UUID(task_id), user_id=UUID(user_id)
        )

        logger.info(
            f"Prediction result retrieved: {task_id}, "
            f"status={result['status']}"
        )

        return result

    except ValueError as e:
        logger.warning(f"Prediction retrieval failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
    except Exception as e:
        logger.error(f"Prediction retrieval error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve prediction",
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
