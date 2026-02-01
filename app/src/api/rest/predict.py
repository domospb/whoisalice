"""
Prediction REST endpoints.

POST /predict/text - Text-based prediction
POST /predict/audio - Audio file prediction
GET /predict/{task_id} - Get prediction result
GET /predict/{task_id}/audio - Download result audio
"""
import logging
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/predict", tags=["Predictions"])

logger.info("Predict router initialized")


@router.post("/text")
async def predict_text():
    """Process text prediction."""
    logger.info("POST /predict/text called")
    # TODO: Implement text prediction
    raise HTTPException(status_code=501, detail="Not implemented yet")


@router.post("/audio")
async def predict_audio(audio: UploadFile = File(...)):
    """Process audio prediction."""
    logger.info(f"POST /predict/audio called: {audio.filename}")
    # TODO: Implement audio prediction
    raise HTTPException(status_code=501, detail="Not implemented yet")


@router.get("/{task_id}")
async def get_prediction(task_id: str):
    """Get prediction result."""
    logger.info(f"GET /predict/{task_id} called")
    # TODO: Implement result retrieval
    raise HTTPException(status_code=501, detail="Not implemented yet")


@router.get("/{task_id}/audio")
async def get_prediction_audio(task_id: str):
    """Download result audio file."""
    logger.info(f"GET /predict/{task_id}/audio called")
    # TODO: Implement audio download
    raise HTTPException(status_code=501, detail="Not implemented yet")
